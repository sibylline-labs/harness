# Retro Doc Template

File: `thoughts/retros/YYYY-MM-DD-<slug>.md`

```markdown
# Retro: <Title>
Date: YYYY-MM-DD
Anchor: <ISSUE-ID> — <issue title>
Mode: pre-merge | post-hoc | degraded (git-only)
PR: #<n> (if any)
Pass: 1 | 2 (<which streams ran, and the signal that fired them>)

## Divergence

<Expected path vs actual path, one paragraph. When the gap was discovered and how.>

## Timeline

| Date | Event | Source |
|---|---|---|
| | | <comment link / commit / doc> |

## Causal chain

| # | Altitude | Cause | Evidence |
|---|---|---|---|
| 1 | Surface | | <commit / comment / doc line> |
| 2 | Behavioural | | |
| 3 | Structural | | |

<Bottomed out at #N — or: chain ends at #N because X.>

## Learnings

### Surface
1. **<Learning>**: <transferable insight>

### Behavioural
1. **<Learning>**: <the habit and the control that changes it>

### Strategic flags (highlight only — not solutioned)
- **<Flag>**: <what is faltering / mounting / structurally wrong, and the evidence>

## Opportunities (proposals — filed only on accept)

### Harness & workflow
- [ ] <draft issue title> — <one-liner; suggested project>

### SOPs & controls
- [ ] <draft issue title> — <one-liner>

### /self-retro
<decision pattern named + offered/run | none implicated>

## Outputs

- Linear comment: <link>
- GOTCHA comments: <files:lines> (post-hoc: suggestions listed here instead)
- PR comment: <link | n/a>
- CLAUDE.md: <entry added | n/a>

## Sources

<dated, grouped: Linear (issue/doc IDs + links) / git (commits, PRs) / thoughts / external>
```

Keep the Linear comment a distillation of this doc — chain summary, learnings, flags, proposal list — never a paste of the whole body.
