---
paths:
  - "**/SKILL.md"
  - "skills/**"
  - ".claude/skills/**"
---

# Skill Development Rules

When working with files in `skills/` or `.claude/skills/`:

## SKILL.md Structure

```yaml
---
name: skill-name
kind: workflow                        # required: tool | gate | rubric | workflow | reference | mode
description: Brief description of what it does and when to use it
allowed-tools: [Bash, Read]           # Optional: restrict tools
allowed-tools: [Bash(npm *), Read]    # Wildcards supported
skills: [skill-1, skill-2]            # Skills inherited when spawned as subagent (one line)
context: fork                         # Run in isolated context
hooks:                                # Same shape as settings.json: event -> matcher groups
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh"   # event JSON on stdin; no $TOOL_* env vars
---
```

A bare string under an event name (`Stop: |`) is ignored with a warning, so it runs nothing.
Hooks in a `context: fork` skill may not fire for the fork's own tool calls; register a guard that
must see them in the settings file instead.

## The kind contract

Every `SKILL.md` declares one top-level `kind:`. `eris skills lint` enforces the contract:

| Kind | Contract |
|---|---|
| `tool` | ships a non-empty `scripts/`; the SKILL.md is judgment over the script |
| `gate` | a checkpoint that judges work; no structural contract |
| `rubric` | at most 60 lines; preloaded by at least one agent's or skill's `skills: [...]` line (its producer); named by at least one `gate` skill (its judge) |
| `workflow` | over 200 lines only with a `references/` holding at least one `.md`: each stage lives in a reference |
| `reference` | knowledge only: no numbered procedure outside fenced code (use bullets, or make it a `workflow`) |
| `mode` | an interaction-calibration skill; no structural contract |

A `kind:` in the body, indented under another key, or inside a folded `description:` is not a
declaration.

## DO
- Keep SKILL.md concise (< 200 lines); move stages and long tables to `references/`
- Include a clear "When to Use" section
- Provide copy-paste bash commands
- Reference `scripts/` for deterministic operations
- Use `skills:` to declare dependencies for agent-type skills
- Use `context: fork` for skills with large outputs

## DON'T
- Include implementation details in SKILL.md
- Duplicate content across skills
- Use allowed-tools that aren't needed
- Over-engineer hooks: use them only when validation is needed
- Write a hook as a bare string under an event name; it never runs

## Script-wrapper skills
For skills that wrap scripts:
- Use `allowed-tools: [Bash, Read]` to restrict capabilities
- Point to the script in the `scripts/` directory
- Include parameter documentation

## Agent-type skills
For skills that run as subagents:
- Add `skills:` to declare skill inheritance
- Consider `context: fork` to prevent context pollution
- State completion requirements in the skill body
