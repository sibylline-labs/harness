# Pass-2 Dispatch — research agents

One agent per evidence stream, dispatched in parallel. Each gets one scoped sub-question and returns a cited handoff and a terse summary. Handoffs land in `thoughts/retros/handoffs/<anchor-slug>/`.

Dispatch only the streams the pass-2 signals implicate — not all four by ritual.

## Streams

| Stream | Sub-question shape | Primary sources |
|---|---|---|
| Linear upstream walk | "What upstream decisions and events led to `<anchor>`? Walk parent/related issues and project/initiative docs; return a dated decision trail." | Linear MCP (source of truth) |
| Git archaeology | "When and how did `<surface>` change? Which commits introduced or copied the defect pattern, and what did review threads say at the time?" | `git log -S/-G`, `git blame`, `gh pr view` |
| Recurrence sweep | "Has this pattern appeared before? Search prior retros, the rules corpus, and sibling issues; return matches with dates." | `thoughts/retros/`, `~/.claude/rules/`, `list_issues` |
| External | "What do the vendor's docs/changelog say about `<dependency behaviour>`?" | web search and vendor docs |

## Agent type and tier

Every stream dispatches as `subagent_type="research-agent"` with an explicit `model`. Leave
either unset and the dispatch silently becomes `general-purpose` on the session's model —
these streams are evidence gathering, not judgment, and do not warrant a frontier tier.

| Stream | Tier | Why |
|---|---|---|
| Git archaeology | `haiku` | Mechanical: run `git log -S/-G`, `blame`, `gh pr view`; return what they printed. |
| Recurrence sweep | `haiku` | Grep the retros and rules corpus; return dated matches. |
| Linear upstream walk | `sonnet` | Walking a decision trail needs judgment about which links are load-bearing. |
| External | `sonnet` | Vendor docs need reconciling against what our code actually does. |

The causal chain is assembled in the **parent** context, from cited handoffs. No stream agent
draws the conclusion; that is the retro's job, not the gatherer's.

## Dispatch template

```
Agent(subagent_type="research-agent", model="<tier from the table above>", prompt="""
Internal-sources mode: Linear is the source of truth for internal facts; the repo is
second; the web is last. Return a cited handoff, not a conclusion.

Brief: retro on <ISSUE-ID> — <one-line divergence statement>.
Sub-question: <stream question, filled>
Deliverable section: evidence for causal-chain rung <N> (<altitude>)
Starting sources: <issue IDs / doc IDs / file paths already known>
Previous handoffs: thoughts/retros/handoffs/<slug>/ (read for awareness, don't re-do)
Handoff: thoughts/retros/handoffs/<slug>/<stream>.md
""")
```

## After return

Read each handoff and lift evidence into the chain **with its citations** — a rung inherits the handoff's sources, not a paraphrase of them. Contradictions between handoffs go to the timeline, not silently resolved.
