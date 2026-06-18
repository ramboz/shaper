# Learnings

> Status: Draft (wizard-generated)
>
> Dead ends, failed approaches, and "we tried X and here's why it didn't work."
> The institutional memory that ADRs don't capture — these are not decisions,
> they're anti-patterns and gotchas discovered in practice.
>
> Update via `/jig:memory-sync` during reconciliation.

<!-- Learnings below. Format: ## Title, followed by what happened and what to do instead. -->

## Hybrid baseline stays metadata-only until product skills
Spec 003 established committed Claude/Codex host packages with root manifests and a drift guard, but intentionally copied only metadata and README content. Product skills, hooks, agents, host-specific README rewriting, and release zips remain deferred to later slices with more signal.

## Initial Python checks avoid package-manager commitments
Spec 003 introduced standard-library unittest via .jig/test-command and an AST syntax check via .jig/lint-command. This keeps the first builder test/lint loop deterministic without choosing pytest, ruff config, or a package manager yet.
