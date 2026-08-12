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

## release-check servo signal boundary
Spec 007 slice 007-02 completed optional servo signal reads for release-check. The only accepted servo input is docs/servo/release-signals/<release-slug>.md from ADR-0004; absence and unrecognized statuses render as not evaluated, signal disagreement is advisory/human-decision-only, and release-check must not run servo loops or mutate JIG/servo state.

## shape-release section writer: append bullets BEFORE nested `###` subsections
Spec 008 nested `### Vertical Scopes` under `## Solution Outline` (008-01) and `### Architecture appetite` under `## JIG Handoff` (008-02). `_append_section_bullets` in `shape_release.py` uses `_section_pattern`, whose span runs to the next `## ` and therefore *includes* any nested `###` subsection. Appending a plain bullet (e.g. `--jig-handoff`, `--solution`, fall-through `--cutline`) to the end of that span drops the bullet AFTER the subsection; if a later `_set_*` rewrite of that subsection's span then runs (as `_set_arch_appetite` does), it silently DELETES the bullet — real data loss on a combined refine. Fix: insert new bullets before the first nested `### ` in the section (end-of-section fallback when none). Any new nested-subsection-under-`##` pattern must respect this.

## ADR frame-critique is a real gate, not a formality — budget for iteration
ADR-0005 carried `frame_review: true`, so `adr.py accept` refused until a recorded `frame-critique` pass verdict existed (`docs/decisions/reviews/adr-NNNN-frame-critique.md`, written via `review.py record-review --adr NNNN --pass frame-critique`). The adversarial reviewer returned `needs-changes` four times before passing; each round exposed a genuine flaw in the "architecture appetite" idea (worked example smuggled in design → banned the positive-shape slot; posture top-end was a floor → made it strictly upper-bound; orthogonality overclaim → conceded it's a graded leanness constraint whose honest value is gradation + always-elicited + considered-permission). The frame-critique loop materially improved the decision. When approving an ADR with `frame_review: true`, expect to harden the frame, not rubber-stamp it — and the spec that implements it may need reconciling to the *post-critique* wording (008-02's AC1 predated the positive-shape-slot ban and had to be updated before READY_FOR_IMPLEMENTATION).
