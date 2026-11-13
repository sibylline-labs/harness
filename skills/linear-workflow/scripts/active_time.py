#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""active_time.py — measure the active (inference + human) time spent on an issue.

The actual-effort half of the estimate-calibration loop (linear-workflow § Estimates).
Wall time is the wrong number: people context-switch and leave sessions idle. Active
time is read from Claude Code and OpenCode V2 transcripts instead: every entry carries a timestamp, and
any gap between consecutive entries longer than the cutoff counts as idle.

USAGE:
  uv run --script active_time.py --issue ABC-123
  uv run --script active_time.py --branch alice/abc-123-fix-login --session <uuid> ...
  uv run --script active_time.py --issue ABC-123 --current --gap 15 --json

SELECTION:
  A transcript entry counts when its `gitBranch` contains the issue key (case-insensitive)
  or equals `--branch`, in main and subagent transcripts alike. `--session` (repeatable)
  and `--current` ($CLAUDE_CODE_SESSION_ID) add whole sessions regardless of branch:
  sessions on main/HEAD or a `worktree-*` branch never match a key, so the closing
  session should always pass `--current`. A selected main transcript brings all of its
  subagent transcripts with it.

  OpenCode V2 transcripts (~/.claude/state/opencode-transcripts/) are scanned too. A
  subagent there runs in its own child session, so its `<child>/subagents/*.jsonl` has no
  main transcript beside it: it is selected by its own branch, or by `--session <child>`.
  Transcripts the plugin wrote before it stamped `gitBranch` match only `--session ses_…`.

OUTPUT:
  active_h  merged timeline across all transcripts: an hour with three parallel
            subagents counts once. This is the number that becomes the actual estimate.
  agent_h   sum over transcripts: parallel subagents count separately (inference spend).
  points    active_h snapped to the Linear exponential scale (nearest on a log2 scale).
  skipped   transcripts that vanished or could not be read mid-scan (other sessions add and
            remove transcripts while this one scans). They add nothing to the totals above;
            the text form names the count only when it is nonzero.

EXIT CODES: 0 ok; 1 nothing matched (an unreadable transcript is skipped, never fatal).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
OPENCODE = Path.home() / ".claude" / "state" / "opencode-transcripts"
SCALE = (1, 2, 4, 8, 16, 32, 64)


def parse_ts(raw: str) -> float | None:
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError):
        return None


def read_entries(path: Path):
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict):
                yield entry


def transcript_groups():
    """Yield (session id, main transcript or None, subagent transcripts), one per session."""
    for main_path in PROJECTS.glob("*/*.jsonl"):
        sid = main_path.stem
        yield sid, main_path, sorted((main_path.parent / sid / "subagents").glob("*.jsonl"))
    # An OpenCode subagent's child session has a subagents/ dir and no main transcript.
    sids = {p.stem for p in OPENCODE.glob("*.jsonl")} | {p.parent.parent.name for p in OPENCODE.glob("*/subagents/*.jsonl")}
    for sid in sorted(sids):
        main_path = OPENCODE / f"{sid}.jsonl"
        yield sid, main_path if main_path.exists() else None, sorted((OPENCODE / sid / "subagents").glob("*.jsonl"))


def intervals(stamps: list[float], gap_s: float) -> list[tuple[float, float]]:
    stamps = sorted(stamps)
    out: list[tuple[float, float]] = []
    for a, b in zip(stamps, stamps[1:]):
        if 0 < b - a <= gap_s:
            out.append((a, b))
    return out


def union_seconds(spans: list[tuple[float, float]]) -> float:
    total, end = 0.0, -math.inf
    for a, b in sorted(spans):
        if b <= end:
            continue
        total += b - max(a, end)
        end = b
    return total


def snap(hours: float) -> int:
    if hours <= 1:
        return 1
    return min(SCALE, key=lambda p: abs(math.log2(p) - math.log2(hours)))


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--issue", help="issue key, matched against gitBranch (e.g. ABC-123)")
    ap.add_argument("--branch", action="append", default=[], help="exact gitBranch to match")
    ap.add_argument("--session", action="append", default=[], help="session id to include whole")
    ap.add_argument("--current", action="store_true", help="include the running session ($CLAUDE_CODE_SESSION_ID)")
    ap.add_argument("--gap", type=float, default=15.0, help="idle cutoff in minutes (default 15)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not (args.issue or args.branch or args.session or args.current):
        ap.error("pass --issue, --branch, --session or --current")

    key = args.issue.lower() if args.issue else None
    branches = set(args.branch)
    whole = set(args.session)
    if args.current:
        current = os.environ.get("CLAUDE_CODE_SESSION_ID")
        if not current:
            ap.error("--current needs CLAUDE_CODE_SESSION_ID in the environment")
        whole.add(current)
    gap_s = args.gap * 60

    def branch_hit(entry: dict) -> bool:
        b = entry.get("gitBranch") or ""
        return (key is not None and key in b.lower()) or b in branches

    per_transcript: dict[Path, list[float]] = {}
    sessions: set[str] = set()
    skipped = 0
    for sid, main_path, subs in transcript_groups():
        take_all = sid in whole
        for path in [p for p in (main_path, *subs) if p is not None]:
            whole_file = take_all or (path is not main_path and main_path in per_transcript)
            # Other sessions add and remove transcripts while this scan runs, so a listed
            # file can be gone or unreadable by the time it is opened.
            try:
                stamps = [
                    t
                    for e in read_entries(path)
                    if (whole_file or branch_hit(e)) and (t := parse_ts(e.get("timestamp"))) is not None
                ]
            except OSError:
                skipped += 1
                continue
            if stamps:
                sessions.add(sid)
                per_transcript[path] = stamps

    skipped_note = f" · skipped {skipped} unreadable transcript(s)" if skipped else ""
    if not per_transcript:
        print(f"no transcript entries matched{skipped_note}", file=sys.stderr)
        return 1

    spans_by = {p: intervals(s, gap_s) for p, s in per_transcript.items()}
    active_h = union_seconds([sp for spans in spans_by.values() for sp in spans]) / 3600
    agent_h = sum(union_seconds(spans) for spans in spans_by.values()) / 3600
    result = {
        "active_h": round(active_h, 2),
        "agent_h": round(agent_h, 2),
        "points": snap(active_h),
        "gap_min": args.gap,
        "sessions": sorted(sessions),
        "transcripts": len(per_transcript),
        "skipped": skipped,
    }
    if args.json:
        print(json.dumps(result))
    else:
        print(
            f"active {result['active_h']}h · agent {result['agent_h']}h · "
            f"points {result['points']} · {len(sessions)} session(s), "
            f"{result['transcripts']} transcript(s), gap {args.gap:g}m{skipped_note}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
