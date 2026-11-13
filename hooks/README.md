# Hooks

Portable hook scripts. `eris org-skills install` links skills, agents and rules,
but never edits your agent's settings: you opt a hook in yourself.

| Hook | Event | What it does |
|---|---|---|
| `doctrine-posture.sh` | SessionStart | States the org's active doctrine posture from `~/.eris/doctrine/<orgId>/doctrine.md` (written by `eris doctrine pull`) and, with `eris` on PATH, the effective gate map. Set `ERIS_ORG` when you belong to several orgs. |

## Opting in (Claude Code)

Add this to `~/.claude/settings.json` (or a project's `.claude/settings.json`), with the
path to your checkout. After `eris org-skills install`, that is `~/.eris/skills/<orgId>`.

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "bash ~/.eris/skills/<orgId>/hooks/doctrine-posture.sh" }] }
    ]
  }
}
```

A hook must exit 0 on every path and print plain text: SessionStart output becomes
session context.
