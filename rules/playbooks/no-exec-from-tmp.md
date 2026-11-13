# Never Write-And-Execute Scripts From /tmp (or World-Writable Temp)

> **Playbook for** [`no-exec-from-tmp.md`](~/.claude/rules/no-exec-from-tmp.md): the resident core carries the statement, trigger and red flags; this file is the full body.

When you generate an ad-hoc script or query file to run, write it to a **trusted project-local working
directory** and execute it from there, never `/tmp`, `/var/tmp`, `/private/tmp`, or `$TMPDIR`. And when
your own tooling trips a security detector, fix the **tooling's behavior**, never suppress the
**detector**.

## Pattern

An interpreter (`python`, `node`, `bash`, …) executing a file located in a world-writable temp
directory **and** making a network connection is a classic attacker TTP. Endpoint security tooling
(EDR, "malicious behavior prevention" engines, macOS Endpoint Security) flags exactly this shape. Two
costs follow:

1. **On a monitored host you self-generate high-severity malware alerts.** In one security-triage
   agent, a subagent wrote a query file under `/tmp` and ran it with `python3` against the SIEM:
   eight high-severity `malware` alerts in about a minute, contaminating the very queue it was draining.
2. **It genuinely is dangerous.** `/tmp` is world-writable and predictable; exec'ing from it is the
   thing the detector is right to catch.

The wrong fix is to exclude your own tooling from the detector: that blinds the detector to the real
attack it exists to catch, and it doesn't scale (every future script needs its own exclusion). The
right fix is to stop exec'ing from temp.

## DO

- **Prefer in-process tools** (a real CLI in the repo `bin/`, an SDK or HTTP call in-process) over
  writing and exec'ing an ad-hoc file at all.
- When an ad-hoc script or query file is genuinely needed, write it to a **gitignored repo working
  dir** and run it from the repo root:
  ```bash
  mkdir -p data/scratch
  cat > data/scratch/q.py <<'PY'
  ...
  PY
  python3 data/scratch/q.py        # script path is under the trusted repo dir, not /tmp
  ```
- Or pipe a single-quoted heredoc straight to the interpreter so **no file lands on disk**:
  ```bash
  python3 - <<'PY'
  ...
  PY
  ```
- When you task a **subagent** to run queries or scripts, put the no-`/tmp` instruction in the
  dispatch prompt explicitly: subagents improvise `/tmp` files unless told otherwise.

## DON'T

- `python3 /tmp/q.py` · `node /tmp/x.js` · `bash /tmp/run.sh` · any `mktemp`-then-exec on a temp path.
- Suppress, exclude or allowlist your own tooling out of a security detector to quiet alerts it
  raised. Change *where you exec from*, not *what the detector sees*.
- Rationalize "`$TMPDIR` isn't literally `/tmp`, so it's fine": any world-writable temp path is the
  anti-pattern. Use a repo-local working dir.

## Red Flags

- You're about to `mktemp` or write to `/tmp/...` and then run an interpreter on it.
- A security rule fired on your own automation and your first instinct is an allowlist or exclusion.
- A threat-model doc lists "exec from /tmp" as a *malicious* signal, and your tooling does it. You're
  imitating the threat; stop, don't suppress.

## Source shape

The first proposed fix for the eight self-inflicted alerts was a self-exclusion for the triage
tooling. The correction was that nothing should be excluded: every alert must be triaged, so find a
way to execute safely from a trusted path instead.
