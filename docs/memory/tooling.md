# Tooling

> Status: Draft (wizard-generated)
>
> Idiosyncratic tool choices and the reasoning behind them.
> Why we use X instead of Y, even when Y is more common.
>
> Update via `/jig:memory-sync`.

<!-- Tooling decisions below. Format: ## Tool\n\n**Why not Y:** ...\n**Why X:** ... -->

## Subagent Use

**Why not ask every time:** The user explicitly approved Codex to spin up
reviewer, implementer, explorer, or worker subagents whenever they materially
help the task.
**Why use them proactively:** shaper's spec workflow depends on independent
reviewer passes, and parallel exploration/review can reduce delay without
weakening the main agent's responsibility for integration.
