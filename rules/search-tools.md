# Search Tool Hierarchy

**Pick the search tool by what you already know: a name, a shape, or only an intent.**

```
Know the exact text / name / regex?            → rg (or the Grep tool)
Need code STRUCTURE (calls, usages, rewrites)? → ast-grep
Know the intent but not the name?              → rg with a broad OR of plausible names, then read the hits
```

`rg -l` to shortlist, then `ast-grep` for precision, is the structural pattern.

| Tool | Answers | Use when |
|---|---|---|
| **rg** / Grep tool | "where does this text occur" | You know a literal, a name or a regex: config values, TODOs, error strings, non-code assets |
| **ast-grep** | "where does this code shape occur" | Calls to `foo()`, usages by node type, safe structural rewrites that must parse the code |

A zero-hit search is a fact about the search's scope, not about the codebase. Before you report an
absence, run a control in the same scope that must hit (a neighbouring symbol, a known file), and
paste the command, the directory and the hit count.

## Red Flags

- A bare `rg` or `grep` in `Bash` with no path operand and no stdin pipe/redirect. In a non-TTY shell
  (a tool call, `$(…)`, a background loop) it reads stdin forever and hangs the session. Always pass
  `.` or a path.
- Regex-rewriting code whose structure matters (nested calls, multi-line arguments) when `ast-grep`
  would parse it.
- Reporting "nothing calls X" from one grep with no control and no scope stated.
