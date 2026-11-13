# Agent Orchestration — Divide by Context, Not Problem Type

Fold routers, planners, validators, and tightly coupled sequential work into the **main agent loop** via progressively disclosed skills (`SKILL.md` + `references/`). Spawn subagents only when **dividing by context** earns a separate window.

| Work | Where It Runs | Why |
|------|---------------|-----|
| Planning (`/work plan`) & reviews (`/premise-gate`, `/plan-review`, `/prd-review`) | **Main loop (skills)** | Shared context connects ticket, Canon, and codebase; the model revises the plan in place without lossy handoffs |
| 1–3 tasks or tightly coupled edits on the same files | **Main loop** | Lower latency and zero handoff loss |
| Parallel read-only lookups (`explore`, `research-agent`, `tpm-auditor`) | **Subagents (parallel)** | Discardable context windows return compact `file:line` results |
| 4+ independent plan phases with clean interfaces (`impl-*`) | **Subagents (per phase)** | Isolates phase churn and test loops from the main window |
| Post-build adversarial gate (`verify-adversarial`) | **Subagent (black-box)** | Fresh context uncontaminated by builder priors |

Never split by problem type (`planner → validator → builder`). Give each subagent a self-contained brief (reference impl, phase spec, `Invariants and Their Rung` rows) and have it return a compact handoff.
