#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""mutate.py -- apply a mutant, run the gate, report KILLED/SURVIVED, restore.

The test-driven-development skill asks that every kept rule and test be seen red
on real code. This is that check as one command: each mutant is an exact-string
edit to one file; the gate command runs against it; the file is put back
byte-identical whatever happens.

USAGE:
  mutate.py run --file F --replace OLD --with NEW [options] -- CMD [ARG ...]
  mutate.py run --mutants mutants.json [options] [-- CMD [ARG ...]]
  mutate.py restore [PATH ...]

  run      Run the unmutated gate once (the baseline: it must exit 0, or every
           mutant would read as killed), then for each mutant: back up the file,
           apply the edit, run the gate, restore, verify the restore by sha256.
           A non-zero exit KILLS the mutant; exit 0 means it SURVIVED; a gate
           that runs past --timeout is killed and counts as KILLED (timeout).
  restore  Put back every file a crashed run left mutated, from its
           `<file>.mutate-orig` sidecar. With no PATH, scans the current
           directory tree (skipping .git and node_modules).

OPTIONS (run):
  --timeout S     per-gate-run timeout in seconds (default 600)
  --no-baseline   skip the unmutated run (only when you have just seen it green)
  --json          print one JSON object instead of the text report

MUTANTS FILE: a JSON list of mutants, or {"cmd": [...], "mutants": [...]}.
  {"id": "drop-guard",          optional; default "<file>#<n>"
   "file": "hooks/x.py",        relative to the current directory
   "replace": "if not ok:",     must occur exactly once in the file
   "with": "if False:",
   "cmd": ["pytest", "-q", "tests/test_x.py"]}   optional per-mutant gate
  A cmd is an argv list, or a string run through the shell. A mutant's cmd
  overrides the file's, which overrides `-- CMD`.

INVARIANTS:
  - Mutant k of a run is stamped mtime = original + 2k seconds, and restore puts
    the original mtime back, so no mtime+size cache (Python's `.pyc`, a bundler's
    transform cache) can serve the original to a mutant's gate or a mutant to
    the next one.
  - The original bytes go to `<file>.mutate-orig` before the edit, and that
    sidecar is deleted only after the file's sha256 matches the original again.
    A run killed with SIGKILL leaves the sidecar; `run` refuses to start while
    one exists for a file it would touch, and `restore` puts it back.
  - SIGINT, SIGTERM and SIGHUP stop the gate's process group, restore, and exit.
  - A mutant whose `replace` text is absent, occurs more than once, or equals
    `with` is an ERROR and its file is never written.

EXIT: 0 every mutant killed · 1 at least one survived · 2 error (usage, bad
mutant, red baseline, leftover sidecar, failed restore).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

SIDECAR_SUFFIX = ".mutate-orig"
SKIP_DIRS = {".git", "node_modules", ".venv"}
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
# One failure line per failing test, across the runners the harness repos use:
# bun test `(fail)`, pytest `FAILED`, bats/TAP `not ok`, vitest/jest `FAIL`/`✗`.
FAILURE_LINE = re.compile(r"^\s*(\(fail\)|FAILED\b|not ok\b|FAIL\b|[✗✘×]\s)")
MAX_FAILURES_SHOWN = 10


class MutateError(Exception):
    """A condition that stops the run with exit 2."""


class Interrupted(Exception):
    """A signal arrived; the `finally` blocks restore before the run exits."""


@dataclass
class Mutant:
    id: str
    file: Path
    replace: str
    with_: str
    cmd: list[str] | str


@dataclass
class Result:
    id: str
    file: str
    verdict: str  # KILLED | SURVIVED
    exit_code: int | None
    seconds: float
    timed_out: bool = False
    failures: list[str] = field(default_factory=list)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sidecar(path: Path) -> Path:
    return path.with_name(path.name + SIDECAR_SUFFIX)


def write_in_place(path: Path, data: bytes) -> None:
    """Rewrite `path`'s bytes, keeping its inode (hardlinks and mode survive)."""
    with open(path, "r+b") as f:
        f.seek(0)
        f.write(data)
        f.truncate()
        f.flush()
        os.fsync(f.fileno())


def restore_from(path: Path, original: bytes, mtime_ns: int | None = None) -> None:
    write_in_place(path, original)
    if mtime_ns is not None:
        os.utime(path, ns=(mtime_ns, mtime_ns))
    if sha256(path.read_bytes()) != sha256(original):
        raise MutateError(f"restore of {path} did not verify; original kept at {sidecar(path)}")
    sidecar(path).unlink(missing_ok=True)


# --- the gate --------------------------------------------------------------


_current_child: subprocess.Popen[bytes] | None = None


def _kill_group(proc: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    proc.wait()


def run_gate(cmd: list[str] | str, timeout: float) -> tuple[int | None, str, float, bool]:
    """Run the gate in its own process group. Returns (exit, output, seconds, timed_out)."""
    global _current_child
    start = time.monotonic()
    try:
        proc = subprocess.Popen(
            cmd,
            shell=isinstance(cmd, str),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as e:
        raise MutateError(f"cannot run gate `{describe(cmd)}`: {e}") from e
    _current_child = proc
    try:
        out, _ = proc.communicate(timeout=timeout)
        return proc.returncode, out.decode("utf-8", "replace"), time.monotonic() - start, False
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        out = proc.stdout.read() if proc.stdout else b""
        return None, out.decode("utf-8", "replace"), time.monotonic() - start, True
    finally:
        if proc.poll() is None:
            _kill_group(proc)
        _current_child = None


def failure_lines(output: str) -> list[str]:
    lines = [ANSI.sub("", ln).rstrip() for ln in output.splitlines()]
    hits = [ln.strip() for ln in lines if FAILURE_LINE.match(ln)]
    if hits:
        return list(dict.fromkeys(hits))[:MAX_FAILURES_SHOWN]
    tail = [ln.strip() for ln in lines if ln.strip()]
    return tail[-5:]


def describe(cmd: list[str] | str) -> str:
    return cmd if isinstance(cmd, str) else " ".join(cmd)


# --- mutants ---------------------------------------------------------------


def _cmd(value: object, where: str) -> list[str] | str:
    if isinstance(value, str) and value.strip():
        return value
    if isinstance(value, list) and value and all(isinstance(a, str) for a in value):
        return cast(list[str], value)
    raise MutateError(f"{where}: cmd must be a non-empty string or list of strings")


def load_mutants(args: argparse.Namespace) -> list[Mutant]:
    cli_cmd: list[str] | str | None = args.cmd or None
    if args.mutants:
        if args.file or args.replace is not None or args.with_ is not None:
            raise MutateError("use --mutants or --file/--replace/--with, not both")
        try:
            doc: Any = json.loads(Path(args.mutants).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise MutateError(f"{args.mutants}: {e}") from e
        file_cmd = None
        if isinstance(doc, dict):
            if "cmd" in doc:
                file_cmd = _cmd(doc["cmd"], args.mutants)
            doc = doc.get("mutants")
        if not isinstance(doc, list) or not doc:
            raise MutateError(f"{args.mutants}: expected a non-empty list of mutants")
        out = []
        for n, raw in enumerate(doc, 1):
            where = f"{args.mutants} mutant {n}"
            if not isinstance(raw, dict):
                raise MutateError(f"{where}: expected an object")
            m = cast(dict[str, Any], raw)
            for key in ("file", "replace", "with"):
                if not isinstance(m.get(key), str):
                    raise MutateError(f"{where}: `{key}` must be a string")
            cmd = _cmd(m["cmd"], where) if "cmd" in m else file_cmd or cli_cmd
            if cmd is None:
                raise MutateError(f"{where}: no gate command (give `cmd`, or `-- CMD`)")
            out.append(Mutant(str(m.get("id") or f"{m['file']}#{n}"), Path(m["file"]),
                              m["replace"], m["with"], cmd))
        return out
    if not args.file or args.replace is None or args.with_ is None:
        raise MutateError("give --mutants FILE, or all of --file, --replace and --with")
    if cli_cmd is None:
        raise MutateError("no gate command: put it after `--`")
    return [Mutant(f"{args.file}#1", Path(args.file), args.replace, args.with_, cli_cmd)]


def check_mutant(m: Mutant) -> bytes:
    """Validate a mutant against the file on disk; returns the file's bytes."""
    if not m.file.is_file():
        raise MutateError(f"{m.id}: {m.file} is not a file")
    if m.replace == m.with_:
        raise MutateError(f"{m.id}: `replace` equals `with`; the mutant changes nothing")
    if not m.replace:
        raise MutateError(f"{m.id}: `replace` is empty")
    data = m.file.read_bytes()
    count = data.count(m.replace.encode("utf-8"))
    if count != 1:
        raise MutateError(f"{m.id}: `replace` occurs {count} times in {m.file}; it must occur exactly once")
    return data


# --- verbs -----------------------------------------------------------------


def _on_signal(signum: int, _frame: object) -> None:
    if _current_child is not None and _current_child.poll() is None:
        _kill_group(_current_child)
    raise Interrupted(signal.Signals(signum).name)


def cmd_run(args: argparse.Namespace) -> int:
    mutants = load_mutants(args)
    for m in mutants:
        if sidecar(m.file).exists():
            raise MutateError(
                f"{sidecar(m.file)} exists: an earlier run did not finish. "
                f"Run `mutate.py restore {m.file}` first"
            )
        check_mutant(m)

    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, _on_signal)

    if not args.no_baseline:
        for cmd in dict.fromkeys(describe(m.cmd) for m in mutants):
            gate = next(m.cmd for m in mutants if describe(m.cmd) == cmd)
            code, output, secs, timed_out = run_gate(gate, args.timeout)
            if code != 0:
                why = "timed out" if timed_out else f"exit {code}"
                shown = "; ".join(failure_lines(output))
                raise MutateError(f"baseline is red ({why}) for `{cmd}`: {shown}. "
                                  "Every mutant would read as KILLED; fix the gate first")

    results: list[Result] = []
    for k, m in enumerate(mutants, 1):
        original = check_mutant(m)  # re-read: an earlier mutant may share the file
        mtime_ns = m.file.stat().st_mtime_ns
        mutated = original.replace(m.replace.encode("utf-8"), m.with_.encode("utf-8"), 1)
        try:
            sidecar(m.file).write_bytes(original)
            write_in_place(m.file, mutated)
            stamp = mtime_ns + k * 2_000_000_000
            os.utime(m.file, ns=(stamp, stamp))
            code, output, secs, timed_out = run_gate(m.cmd, args.timeout)
        finally:
            restore_from(m.file, original, mtime_ns)
        killed = timed_out or code != 0
        results.append(Result(
            m.id, str(m.file), "KILLED" if killed else "SURVIVED", code, round(secs, 2),
            timed_out, failure_lines(output) if killed else [],
        ))
        if not args.json:
            print(format_result(results[-1]), flush=True)

    survived = [r for r in results if r.verdict == "SURVIVED"]
    if args.json:
        print(json.dumps({
            "mutants": len(results), "killed": len(results) - len(survived),
            "survived": len(survived), "results": [r.__dict__ for r in results],
        }, indent=2))
    else:
        print(f"mutants: {len(results)} · killed {len(results) - len(survived)} · survived {len(survived)}")
    return 1 if survived else 0


def format_result(r: Result) -> str:
    why = "timeout" if r.timed_out else f"exit {r.exit_code}"
    head = f"{r.verdict:<8} {r.id}  ({why}, {r.seconds:.1f}s)"
    if r.verdict == "SURVIVED":
        return head + "  -- the gate passed with the mutant applied"
    return head + "".join(f"\n    {line}" for line in r.failures)


def cmd_restore(args: argparse.Namespace) -> int:
    if args.paths:
        targets = [Path(p) for p in args.paths]
    else:
        targets = []
        for dirpath, dirnames, filenames in os.walk("."):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            targets += [Path(dirpath, f[: -len(SIDECAR_SUFFIX)])
                        for f in filenames if f.endswith(SIDECAR_SUFFIX)]
    restored = 0
    for path in targets:
        side = sidecar(path)
        if not side.exists():
            if args.paths:
                print(f"nothing to restore: {path}")
            continue
        original = side.read_bytes()
        if not path.exists():
            shutil.copyfile(side, path)
        restore_from(path, original)
        print(f"restored {path}")
        restored += 1
    if not args.paths and not restored:
        print("nothing to restore")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd: list[str] = []
    if "--" in argv:
        at = argv.index("--")
        argv, cmd = argv[:at], argv[at + 1:]

    parser = argparse.ArgumentParser(prog="mutate.py", description=(__doc__ or "").split("\n\n")[0])
    sub = parser.add_subparsers(dest="verb", required=True)
    run = sub.add_parser("run", help="apply mutants, run the gate, report, restore")
    run.add_argument("--file")
    run.add_argument("--replace")
    run.add_argument("--with", dest="with_")
    run.add_argument("--mutants")
    run.add_argument("--timeout", type=float, default=600.0)
    run.add_argument("--no-baseline", action="store_true")
    run.add_argument("--json", action="store_true")
    restore = sub.add_parser("restore", help="put back files a crashed run left mutated")
    restore.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    args.cmd = cmd

    try:
        if args.verb == "run":
            return cmd_run(args)
        if cmd:
            raise MutateError("restore takes no `-- CMD`")
        return cmd_restore(args)
    except MutateError as e:
        print(f"mutate.py: error: {e}", file=sys.stderr)
        return 2
    except Interrupted as e:
        print(f"mutate.py: interrupted by {e}; files restored", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
