#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""review_report.py -- the digests and frontmatter of a review-report@1.

The reviewer (the model) judges the diff; this script computes every sha and writes the file, so no
digest is ever typed by a model. eris (`eris gate record --review-report`) is the one validator.

    prepare --pr N [--surface S] [--vocabulary PATH] [--pr-head SHA]
        -> <git-dir>/eris/review-<N>/{diff.patch,context.json}; prints the context path
    emit --context PATH --findings PATH --effort E --model M [--body PATH] [--actor A] [--author A]
         [--fresh-context] [--out PATH]
        -> <git-dir>/eris/review-report-<N>.md (default); prints the report path

Digest contract (references/review-report.md; `eris gate check` recomputes them and must stay equal):
  target.diff_sha256  sha256 of `git diff --no-ext-diff --no-color <merge-base origin/main HEAD> HEAD`
  skill.sha256        sha256 of the manifest "<path in skill dir>\\0<sha256 of blob bytes>\\n" over the
                      blobs of skills/<name>/ at harness_sha, sorted by path; a dirty skill dir is refused
  vocabulary.sha256   sha256 of the vocabulary file's bytes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SCHEMA = "review-report@1"
EFFORTS = ("low", "medium", "high", "max")
SEVERITIES = ("blocking", "major", "minor", "nit")
STATUSES = ("open", "fixed", "refuted")
DEFAULT_SURFACE = "code-quality"
BASE = "origin/main"  # eris gate check recomputes diff_sha256 against origin/main

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_NAME = SKILL_DIR.name
DEFAULT_VOCABULARY = SKILL_DIR / "references" / "code-quality-classes.md"
CLASS_HEADING = re.compile(r"^## Class ([A-Za-z]*\d+) — ", re.MULTILINE)


class ReportError(Exception):
    """A refusal: printed as one line on stderr, exit 2."""


@dataclass(frozen=True)
class Target:
    repo: str
    pr: int
    head_sha: str
    diff_sha256: str


@dataclass(frozen=True)
class SkillRef:
    name: str
    harness_sha: str
    sha256: str


@dataclass(frozen=True)
class VocabularyRef:
    path: str
    sha256: str


@dataclass(frozen=True)
class Context:
    target: Target
    base: str
    surface: str
    skill: SkillRef
    vocabulary: VocabularyRef
    vocabulary_arg: str | None
    classes: tuple[str, ...]

    @staticmethod
    def load(path: Path) -> Context:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return Context(
            target=Target(**raw["target"]),
            base=raw["base"],
            surface=raw["surface"],
            skill=SkillRef(**raw["skill"]),
            vocabulary=VocabularyRef(**raw["vocabulary"]),
            vocabulary_arg=raw["vocabulary_arg"],
            classes=tuple(raw["classes"]),
        )


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    class_: str
    file: str
    line: int
    status: str
    evidence: str

    def to_report(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "severity": self.severity,
            "class": self.class_,
            "file": self.file,
            "line": self.line,
            "status": self.status,
            "evidence": self.evidence,
        }


def _git(cwd: Path, *args: str) -> bytes:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False)
    if r.returncode != 0:
        raise ReportError(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout


def _git_text(cwd: Path, *args: str) -> str:
    return _git(cwd, *args).decode("utf-8").strip()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def remote_slug(url: str) -> str:
    """`owner/name` from an ssh (`git@host:o/n.git`) or https (`https://host/o/n(.git)`) origin."""
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$", url.strip())
    if m is None:
        raise ReportError(f"origin {url!r} has no owner/name")
    return m.group(1)


def diff_sha256(repo: Path, base: str) -> tuple[str, bytes]:
    merge_base = _git_text(repo, "merge-base", base, "HEAD")
    diff = _git(repo, "diff", "--no-ext-diff", "--no-color", merge_base, "HEAD")
    return _sha256(diff), diff


def skill_ref(skill_dir: Path = SKILL_DIR) -> SkillRef:
    root = Path(_git_text(skill_dir, "rev-parse", "--show-toplevel"))
    rel = skill_dir.resolve().relative_to(root.resolve()).as_posix()
    dirty = _git(root, "status", "--porcelain", "--", rel).decode("utf-8").rstrip()
    if dirty:
        raise ReportError(f"skill dir {rel} has uncommitted changes; commit them so harness_sha reproduces it:\n{dirty}")
    head = _git_text(root, "rev-parse", "HEAD")
    files = sorted(p for p in _git(root, "ls-tree", "-r", "-z", "--name-only", head, "--", rel).decode("utf-8").split("\0") if p)
    manifest = "".join(f"{Path(p).relative_to(rel).as_posix()}\0{_sha256(_git(root, 'cat-file', 'blob', f'{head}:{p}'))}\n" for p in files)
    return SkillRef(name=skill_dir.name, harness_sha=head, sha256=_sha256(manifest.encode("utf-8")))


def vocabulary_classes(text: str) -> tuple[str, ...]:
    return tuple(CLASS_HEADING.findall(text))


def _vocabulary(repo: Path, surface: str, given: str | None) -> tuple[VocabularyRef, tuple[str, ...]]:
    if given is not None:
        path, label = (repo / given), given
    elif surface == DEFAULT_SURFACE:
        harness = Path(_git_text(SKILL_DIR, "rev-parse", "--show-toplevel")).resolve()
        path, label = DEFAULT_VOCABULARY, DEFAULT_VOCABULARY.relative_to(harness).as_posix()
    else:
        label = f"thoughts/vocabulary/{surface}.md"
        path = repo / label
    if not path.is_file():
        raise ReportError(f"vocabulary {label} not found for surface {surface!r}; pass --vocabulary")
    data = path.read_bytes()
    classes = vocabulary_classes(data.decode("utf-8-sig"))
    if not classes:
        raise ReportError(f"vocabulary {label} declares no '## Class <ID> — ' headings")
    return VocabularyRef(path=label, sha256=_sha256(data)), classes


def _pr_head(repo: Path, pr: int) -> str:
    r = subprocess.run(["gh", "pr", "view", str(pr), "--json", "headRefOid", "-q", ".headRefOid"], cwd=repo, capture_output=True, check=False)
    if r.returncode != 0:
        raise ReportError(f"gh pr view {pr}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8").strip()


def _work_dir(repo: Path) -> Path:
    git_dir = Path(_git_text(repo, "rev-parse", "--absolute-git-dir"))
    return git_dir / "eris"


def prepare(repo: Path, pr: int, surface: str, vocabulary: str | None, base: str, pr_head: str | None) -> Path:
    head = _git_text(repo, "rev-parse", "HEAD")
    remote_head = pr_head if pr_head is not None else _pr_head(repo, pr)
    if remote_head != head:
        raise ReportError(f"local HEAD {head[:12]} is not PR #{pr} head {remote_head[:12]}; check out and push the PR head first")
    digest, diff = diff_sha256(repo, base)
    vocab, classes = _vocabulary(repo, surface, vocabulary)
    ctx = Context(
        target=Target(repo=remote_slug(_git_text(repo, "remote", "get-url", "origin")), pr=pr, head_sha=head, diff_sha256=digest),
        base=base,
        surface=surface,
        skill=skill_ref(),
        vocabulary=vocab,
        vocabulary_arg=vocabulary,
        classes=classes,
    )
    out = _work_dir(repo) / f"review-{pr}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "diff.patch").write_bytes(diff)
    path = out / "context.json"
    path.write_text(json.dumps(asdict(ctx), indent=2) + "\n", encoding="utf-8")
    return path


def parse_findings(raw: object, classes: tuple[str, ...]) -> tuple[Finding, ...]:
    if not isinstance(raw, list):
        raise ReportError("findings must be a JSON array")
    out: list[Finding] = []
    seen: set[str] = set()
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ReportError(f"findings[{i}] is not an object")
        item.setdefault("status", "open")
        missing = [k for k in ("id", "severity", "class", "file", "line", "evidence") if k not in item]
        if missing:
            raise ReportError(f"findings[{i}]: missing {missing}")
        texts = {k: item[k] for k in ("id", "severity", "class", "file", "status", "evidence")}
        bad = [k for k, v in texts.items() if not _is_text(v)]
        if bad:
            raise ReportError(f"findings[{i}]: {bad} must be non-empty UTF-8 strings")
        line = item["line"]
        if type(line) is not int:
            raise ReportError(f"findings[{i}]: line must be an integer, got {line!r}")
        f = Finding(
            id=texts["id"],
            severity=texts["severity"],
            class_=texts["class"],
            file=texts["file"],
            line=line,
            status=texts["status"],
            evidence=texts["evidence"],
        )
        if f.id in seen:
            raise ReportError(f"findings[{i}]: duplicate id {f.id}")
        if f.class_ not in classes:
            raise ReportError(f"findings[{i}] ({f.id}): class {f.class_!r} is not in the vocabulary {list(classes)}")
        if f.line < 1:
            raise ReportError(f"findings[{i}] ({f.id}): line must be >= 1")
        if f.severity not in SEVERITIES or f.status not in STATUSES:
            raise ReportError(f"findings[{i}] ({f.id}): severity in {SEVERITIES}, status in {STATUSES}")
        seen.add(f.id)
        out.append(f)
    return tuple(out)


def _is_text(v: object) -> bool:
    if not isinstance(v, str) or not v.strip():
        return False
    try:
        v.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def render(ctx: Context, findings: tuple[Finding, ...], *, effort: str, model: str, actor: str, author: str, fresh_context: bool, body: str) -> str:
    report = {
        "schema": SCHEMA,
        "target": asdict(ctx.target),
        "surface": ctx.surface,
        "effort": effort,
        "reviewer": {
            "actor": actor,
            "model": model,
            "fresh_context": fresh_context,
            "skill": asdict(ctx.skill),
            "vocabulary": asdict(ctx.vocabulary),
        },
        "author": {"actor": author},
        "classes_checked": list(ctx.classes),
        "findings": [f.to_report() for f in findings],
    }
    # JSON is YAML 1.2: eris reads this frontmatter with its YAML parser, no PyYAML needed here.
    text = "---\n" + json.dumps(report, indent=2, ensure_ascii=False) + "\n---\n"
    return text + ("\n" + body.strip() + "\n" if body.strip() else "")


def _session_actor() -> str | None:
    for var in ("CLAUDE_CODE_SESSION_ID", "OPENCODE_SESSION_ID"):
        if os.environ.get(var):
            return f"session:{os.environ[var]}"
    return None


def emit(
    repo: Path,
    context: Path,
    findings_path: Path,
    *,
    effort: str,
    model: str,
    actor: str,
    author: str,
    fresh_context: bool,
    body: str = "",
    out: Path | None = None,
) -> Path:
    ctx = Context.load(context)
    head = _git_text(repo, "rev-parse", "HEAD")
    digest, _ = diff_sha256(repo, ctx.base)
    if head != ctx.target.head_sha or digest != ctx.target.diff_sha256:
        raise ReportError(f"HEAD moved since prepare ({ctx.target.head_sha[:12]} -> {head[:12]}); run prepare and the review again")
    if skill_ref() != ctx.skill:
        raise ReportError("the skill changed since prepare (digest or harness_sha); run prepare and the review again")
    if _vocabulary(repo, ctx.surface, ctx.vocabulary_arg) != (ctx.vocabulary, ctx.classes):
        raise ReportError(f"vocabulary {ctx.vocabulary.path} changed since prepare; run prepare and the review again")
    blank = [name for name, v in (("--model", model), ("--actor", actor), ("--author", author)) if not _is_text(v)]
    if blank:
        raise ReportError(f"{blank} must be non-empty UTF-8 strings (--author: the actor that wrote the PR)")
    findings = parse_findings(json.loads(findings_path.read_text(encoding="utf-8")), ctx.classes)
    text = render(ctx, findings, effort=effort, model=model, actor=actor, author=author, fresh_context=fresh_context, body=body)
    path = out or _work_dir(repo) / f"review-report-{ctx.target.pr}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="review_report.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=".", help="the PR's checkout (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("prepare")
    pp.add_argument("--pr", type=int, required=True)
    pp.add_argument("--surface", default=DEFAULT_SURFACE)
    pp.add_argument("--vocabulary", help="repo-relative vocabulary file (default: by surface)")
    pp.add_argument("--pr-head", help="the PR head sha, instead of asking gh")
    pe = sub.add_parser("emit")
    pe.add_argument("--context", required=True)
    pe.add_argument("--findings", required=True)
    pe.add_argument("--effort", required=True, choices=EFFORTS)
    pe.add_argument("--model", required=True)
    pe.add_argument("--body")
    pe.add_argument("--actor")
    pe.add_argument("--author", required=True, help="the actor that wrote the PR (session:<id>, an email or a handle)")
    pe.add_argument("--fresh-context", action="store_true", help="the review ran in subagents given only the diff, rubric and vocabulary")
    pe.add_argument("--out")
    args = p.parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        if args.cmd == "prepare":
            print(prepare(repo, args.pr, args.surface, args.vocabulary, BASE, args.pr_head))
        else:
            actor = args.actor or _session_actor()
            if actor is None:
                raise ReportError("no reviewer actor: pass --actor (no CLAUDE_CODE_SESSION_ID or OPENCODE_SESSION_ID)")
            print(
                emit(
                    repo,
                    Path(args.context),
                    Path(args.findings),
                    effort=args.effort,
                    model=args.model,
                    actor=actor,
                    author=args.author,
                    fresh_context=args.fresh_context,
                    body=Path(args.body).read_text(encoding="utf-8") if args.body else "",
                    out=Path(args.out) if args.out else None,
                )
            )
    except ReportError as e:
        print(f"review_report: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
