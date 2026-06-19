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

## First scope-audit helper is intentionally shallow and advisory-only
Spec 006 introduced scope_audit.py following cutline's deterministic-first-pass pattern: it reads the release plan, release slate, JIG status board, and linked specs constrained under the repo, and groups advisory findings (appetite leakage, nice-to-have creep, unresolved rabbit holes/no-go conflicts, JIG overreach, orphan specs) from board rows plus simple word matches. It never mutates JIG lifecycle state — output is patch-ready guidance only, guarded by a before/after snapshot test. Richer semantic scope analysis remains future work.

## First release-check helper is JIG-only, deterministic, and advisory
Spec 007 slice 007-01 introduced release_check.py following the cutline/scope-audit deterministic-first-pass pattern: it reads release criteria (appetite, cutline, JIG handoff, release-check criteria, rabbit holes, no-gos) plus the JIG board and linked specs constrained under the repo, and emits exactly one advisory recommendation — ship / cut scope / stop and re-shape / extend only with explicit rationale. `extend` is never invented; it requires an explicit `## Extension` section in the release plan, faithful to the fixed-appetite shaping model. Servo signals are reported as "not evaluated", never as a failure; servo reads stay deferred to slice 007-02 behind the future read-boundary ADR. Non-mutation is guarded by a before/after snapshot test.

## CI syntax-check list is a second source of truth alongside .jig/lint-command
Adding a Python helper means updating the file list in BOTH `.jig/lint-command` AND the `Check Python syntax` step in `.github/workflows/ci.yml` — they are independent hardcoded lists, and the CI one will silently drop new files from the enforced syntax gate (which runs the Python 3.11/3.12 matrix) if you only update `.jig/lint-command`. Also: backslashes inside f-string expressions (PEP 701) are a SyntaxError on 3.11 — compute the escaped value in a plain statement first, as scope_audit.py does.
