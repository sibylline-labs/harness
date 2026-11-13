#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""emerging_tech.py -- the `work` research stage's mechanical trigger.

A library fires when the plan's version of it is one the model can't know: it is missing
from the lockfile, its requested major is above the installed one, or the version the plan
will run (the requested exact version, else the installed one) was released after the
model's knowledge cutoff. A fired library needs a `research/<lib>@<version>/README.md`
cache (repo-local or harness-level), judged by `emerging-tech-research@1`.

USAGE:
  uv run --script emerging_tech.py --lockfile <lockfile> [--cutoff YYYY-MM-DD]
      [--research-dir DIR] [--offline] <lib>[@<spec>] ...

  <lockfile> is `bun.lock`, `bun.lockb` (read through `bun`, which must be on PATH),
  `yarn.lock` (classic or berry), `package-lock.json`, `pnpm-lock.yaml`, `uv.lock`, `go.mod` or
  `go.sum`; the file name picks the reader. <lib> is the package name, or a Go module path.
  <spec> is a version or range (`4`, `4.0.7`, `^3.24.0`, `v1.6.0`); its first number is the major.
  For a 0.x version the minor counts as the major, as semver treats it as breaking.
  A lockfile holding several copies of a package counts its highest.
  The cache is looked up in --research-dir (the target repo's `research/`), then in
  --shared-research-dir (default: `<harness root>/research`), so a library that fires in every
  repo is cached once. A shared hit prints its own path in the cache column.
  --offline skips the release-date leg; online, a failed registry lookup fires
  (`release-unverified`) rather than passing.

OUTPUT: one TSV row per library:
  <lib>  fire|quiet  <reasons,|->  <installed|->  <cache dir>  present|missing|-

EXIT: 0 when every fired library has a cache, 1 when one has none, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

#: The knowledge cutoff of the harness's default model (Opus 5.5: June 2026).
MODEL_CUTOFF = dt.date(2026, 6, 1)

#: Lockfile name -> package ecosystem; any other lockfile is a usage error.
LOCKFILES: dict[str, str] = {
    "bun.lock": "npm",
    "bun.lockb": "npm",
    "yarn.lock": "npm",
    "package-lock.json": "npm",
    "pnpm-lock.yaml": "npm",
    "uv.lock": "pypi",
    "go.mod": "go",
    "go.sum": "go",
}

REGISTRY_TIMEOUT_S = 10
BUN_TIMEOUT_S = 30

#: The harness-level cache: `<harness root>/research`, resolved from this file's real path
#: (`skills/work/scripts/`), so it is the install root whether run directly or through the
#: `~/.claude/skills` symlinks.
SHARED_RESEARCH_DIR = Path(__file__).resolve().parents[3] / "research"

#: A `bun.lock` "packages" row: `"<key>": ["<name>@<version>"`. The file is JSONC (trailing
#: commas), so it is matched, not `json.loads`-ed. A nested `parent/child` key is a
#: non-hoisted copy and is skipped by requiring key == name.
_BUN_ROW_RE = re.compile(r'^\s*"([^"]+)":\s*\["((?:@[^@"/]+/)?[^@"]+)@([^"]+)"', re.MULTILINE)
#: A yarn header's version row: classic `  version "1.2.3"` (its key sometimes quoted too) and
#: berry `  version: 1.2.3`. `bun bun.lockb` prints the classic spelling.
_YARN_VERSION_RE = re.compile(r'^  "?version"?:? "?([^"\s]+)"?\s*$')
#: A pnpm `packages:` key at two-space indent: v9 `name@1.2.3:`, v6 `/name@1.2.3(peer):`,
#: v5 `/name/1.2.3_peer:`; a scoped name is quoted.
_PNPM_ROW_RE = re.compile(r"""^  ['"]?/?((?:@[^/@'"\s:]+/)?[^/@'"\s:]+)[@/](\d[^()'"_:\s]*)""")
_NESTED_NODE_MODULES = "/node_modules/"
_EXACT_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+.][0-9A-Za-z.-]+)?$")
_NUMS_RE = re.compile(r"\d+")

ReleaseLookup = Callable[[str, str, str], dt.date | None]


@dataclass(frozen=True)
class Verdict:
    lib: str
    spec: str | None
    installed: str | None
    reasons: tuple[str, ...]

    @property
    def fires(self) -> bool:
        return bool(self.reasons)

    @property
    def target(self) -> str | None:
        """The version the plan will run: the requested spec without range operators, else
        the installed version."""
        if self.spec:
            return self.spec.lstrip("^~=<>v ")
        return self.installed


def normalise(ecosystem: str, name: str) -> str:
    """PyPI names compare by PEP 503; npm names are exact."""
    return re.sub(r"[-_.]+", "-", name).lower() if ecosystem == "pypi" else name


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(n) for n in _NUMS_RE.findall(version)[:3])


def _keep_highest(found: dict[str, str], name: str, version: str) -> None:
    """A lockfile may hold several copies of one package; the trigger judges the highest."""
    have = found.get(name)
    if have is None or _version_key(version) > _version_key(have):
        found[name] = version


def _parse_bun_lock(text: str) -> dict[str, str]:
    start = text.find('"packages"')
    rows = _BUN_ROW_RE.finditer(text, start if start >= 0 else len(text))
    return {name: version for key, name, version in (m.groups() for m in rows) if key == name}


def _parse_yarn(text: str) -> dict[str, str]:
    """Yarn classic and berry (and `bun bun.lockb`'s classic text): a header line, then its
    `version` row. `__metadata`, workspace, patch and virtual headers are not packages."""
    found: dict[str, str] = {}
    name: str | None = None
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        if not line[0].isspace():
            first = line.rstrip().rstrip(":").split(",")[0].strip().strip('"')
            at = first.find("@", 1)
            skipped = any(f"@{kind}:" in first for kind in ("workspace", "patch", "virtual"))
            name = first[:at] if at > 0 and not skipped else None
        elif name and (m := _YARN_VERSION_RE.match(line)):
            _keep_highest(found, name, m.group(1))
            name = None
    return found


def _parse_package_lock(text: str) -> dict[str, str]:
    """npm lockfile v2/v3 `packages` (hoisted `node_modules/<name>` keys only) or v1
    `dependencies`."""
    data = json.loads(text)
    found: dict[str, str] = {}
    packages = data.get("packages")
    if isinstance(packages, dict):
        for key, row in packages.items():
            name = key.removeprefix("node_modules/") if key.startswith("node_modules/") else None
            if name and _NESTED_NODE_MODULES not in f"/{name}" and isinstance(row, dict) and "version" in row:
                _keep_highest(found, name, str(row["version"]))
        return found
    for name, row in (data.get("dependencies") or {}).items():
        if isinstance(row, dict) and "version" in row:
            _keep_highest(found, name, str(row["version"]))
    return found


def _parse_pnpm(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    in_packages = False
    for line in text.splitlines():
        if line and not line[0].isspace():
            in_packages = line.rstrip() == "packages:"
        elif in_packages and (m := _PNPM_ROW_RE.match(line)):
            _keep_highest(found, m.group(1), m.group(2))
    return found


def _go_add(found: dict[str, str], parts: list[str]) -> None:
    if len(parts) >= 2 and parts[1].startswith("v") and not parts[1].endswith("/go.mod"):
        _keep_highest(found, parts[0].strip('"`'), parts[1].removeprefix("v"))


def _parse_go_mod(text: str) -> dict[str, str]:
    """`require` rows, single-line and in a block, `// indirect` ones included."""
    found: dict[str, str] = {}
    block: str | None = None
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        if block is not None:
            if line == ")":
                block = None
            elif block == "require":
                _go_add(found, line.split())
            continue
        head, _, rest = line.partition(" ")
        if rest.strip() == "(":
            block = head
        elif head == "require":
            _go_add(found, rest.split())
    return found


def _parse_go_sum(text: str) -> dict[str, str]:
    """`<module> v<version> h1:...` rows; the `v<version>/go.mod` rows repeat them."""
    found: dict[str, str] = {}
    for line in text.splitlines():
        _go_add(found, line.split())
    return found


def _read_bun_lockb(path: Path) -> str:
    """`bun <file>` prints the binary lockfile as yarn v1 text."""
    try:
        done = subprocess.run(
            ["bun", str(path.resolve())], capture_output=True, text=True, timeout=BUN_TIMEOUT_S, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f"{path.name}: reading a binary lockfile needs `bun` on PATH ({exc})") from exc
    if done.returncode:
        raise ValueError(f"{path.name}: `bun {path.name}` exited {done.returncode}: {done.stderr.strip()}")
    return done.stdout


#: Lockfile name -> reader of its text into `{package: version}`.
_READERS: dict[str, Callable[[str], dict[str, str]]] = {
    "bun.lock": _parse_bun_lock,
    "bun.lockb": _parse_yarn,
    "yarn.lock": _parse_yarn,
    "package-lock.json": _parse_package_lock,
    "pnpm-lock.yaml": _parse_pnpm,
    "go.mod": _parse_go_mod,
    "go.sum": _parse_go_sum,
}


def read_lock(path: Path) -> tuple[str, dict[str, str]]:
    """The lockfile's ecosystem and its installed `{normalised name: version}`."""
    ecosystem = LOCKFILES.get(path.name)
    if ecosystem is None:
        raise ValueError(f"{path.name}: not one of {sorted(LOCKFILES)}")
    text = (_read_bun_lockb(path) if path.name == "bun.lockb" else path.read_text(encoding="utf-8")).lstrip(
        "\ufeff"
    )
    if ecosystem == "pypi":
        packages = tomllib.loads(text).get("package", [])
        return ecosystem, {normalise(ecosystem, p["name"]): str(p["version"]) for p in packages}
    return ecosystem, _READERS[path.name](text)


def split_lib(arg: str) -> tuple[str, str | None]:
    """`@scope/pkg@^1.2` -> (`@scope/pkg`, `^1.2`); the scope's leading `@` is not a separator."""
    at = arg.rfind("@")
    if at <= 0:
        return arg, None
    return arg[:at], arg[at + 1 :] or None


def major_key(version: str) -> tuple[int, ...] | None:
    nums = [int(n) for n in _NUMS_RE.findall(version)[:2]]
    if not nums:
        return None
    return (0, nums[1]) if nums[0] == 0 and len(nums) > 1 else (nums[0],)


def evaluate(
    ecosystem: str,
    arg: str,
    installed: dict[str, str],
    cutoff: dt.date,
    released: ReleaseLookup | None,
) -> Verdict:
    """Which trigger legs fire for one `<lib>[@<spec>]`; `released=None` skips the date leg."""
    lib, spec = split_lib(arg)
    have = installed.get(normalise(ecosystem, lib))
    reasons: list[str] = []
    if have is None:
        reasons.append("missing")
    elif spec:
        want_key, have_key = major_key(spec), major_key(have)
        if want_key and have_key and want_key > have_key:
            reasons.append("major-above")
    verdict = Verdict(lib, spec, have, ())
    target = verdict.target
    if released is not None and target and _EXACT_RE.match(target):
        when = released(ecosystem, lib, target)
        if when is None:
            reasons.append("release-unverified")
        elif when > cutoff:
            reasons.append("released-after-cutoff")
    return Verdict(lib, spec, have, tuple(reasons))


def registry_release(ecosystem: str, name: str, version: str) -> dt.date | None:
    """The publish date of `name@version` from the npm registry, PyPI or the Go proxy; None on any failure."""
    if ecosystem == "npm":
        url = f"https://registry.npmjs.org/{name.replace('/', '%2F')}"
    elif ecosystem == "go":
        escaped = re.sub(r"[A-Z]", lambda m: "!" + m.group().lower(), name)
        url = f"https://proxy.golang.org/{escaped}/@v/v{version}.info"
    else:
        url = f"https://pypi.org/pypi/{normalise(ecosystem, name)}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=REGISTRY_TIMEOUT_S) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None
    if ecosystem == "npm":
        stamp = data.get("time", {}).get(version)
    elif ecosystem == "go":
        stamp = data.get("Time")
    else:
        stamp = next((u.get("upload_time_iso_8601") for u in data.get("urls", [])), None)
    return dt.date.fromisoformat(stamp[:10]) if stamp else None


def _cache_in(research: Path, verdict: Verdict) -> Path | None:
    """The `<lib>@<version>` dir under `research` holding a README.md for the verdict's target
    version. A partial target (`4`) matches any pinned `4.x.y` dir."""
    target = verdict.target
    exact = research / f"{verdict.lib}@{target or '<version>'}"
    if (exact / "README.md").is_file():
        return exact
    parent = research / verdict.lib
    base = parent.parent
    for candidate in sorted(base.glob(f"{parent.name}@*")) if base.is_dir() else []:
        version = candidate.name.split("@", 1)[1]
        if (target is None or version.startswith(f"{target}.")) and (candidate / "README.md").is_file():
            return candidate
    return None


def find_cache(research: Path, shared: Path | None, verdict: Verdict) -> tuple[Path, bool]:
    """The cache dir for the verdict's target version and whether its README.md exists: the
    target repo's `research` first, then the harness-level `shared` dir. A miss names the repo
    path, where a new cache is built unless the library fires in every repo (see research.md)."""
    for root in (research, shared):
        hit = _cache_in(root, verdict) if root else None
        if hit:
            return hit, True
    return research / f"{verdict.lib}@{verdict.target or '<version>'}", False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The work research stage's emerging-tech trigger.")
    parser.add_argument("--lockfile", type=Path, required=True)
    parser.add_argument("--cutoff", type=dt.date.fromisoformat, default=MODEL_CUTOFF)
    parser.add_argument("--research-dir", type=Path, default=Path("research"))
    parser.add_argument(
        "--shared-research-dir",
        type=Path,
        default=SHARED_RESEARCH_DIR,
        help="harness-level cache checked after --research-dir (default: <harness root>/research)",
    )
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("libs", nargs="+")
    args = parser.parse_args(argv)
    try:
        ecosystem, installed = read_lock(args.lockfile)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"emerging_tech: {exc}", file=sys.stderr)
        return 2
    released = None if args.offline else registry_release
    uncached = 0
    for arg in args.libs:
        verdict = evaluate(ecosystem, arg, installed, args.cutoff, released)
        cache, present = find_cache(args.research_dir, args.shared_research_dir, verdict)
        state = ("present" if present else "missing") if verdict.fires else "-"
        uncached += verdict.fires and not present
        print(
            "\t".join(
                (
                    verdict.lib,
                    "fire" if verdict.fires else "quiet",
                    ",".join(verdict.reasons) or "-",
                    verdict.installed or "-",
                    str(cache),
                    state,
                )
            )
        )
    return 1 if uncached else 0


if __name__ == "__main__":
    sys.exit(main())
