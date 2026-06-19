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

## First cutline helper is intentionally shallow
Spec 002 introduced cutline.py as a deterministic first pass: it reads the release plan, JIG status board, and linked specs constrained under docs/specs, but classifies from board rows plus simple release-plan no-go/risk word matches. Richer semantic cutline analysis remains future work.

## Host README exact-copy remains host-neutral
Spec 002 kept host package README generation as an exact root README copy while adding host-neutral product skills. Root README wording must stay accurate for installed host packages; host-specific README rewriting remains deferred until host-specific runtime prose or install verification needs it.

## Release-plan status parser must ignore allowed-status catalogs
Spec 005 found that release plans produced by shape-release include an explanatory Allowed statuses sentence listing every possible status. Helpers should parse frontmatter status: or a standalone status line first, not scan the whole Status section for any known status, or committed/shipping/shipped/dropped plans can collapse back to candidate.
