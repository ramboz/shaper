---
status: DONE
dependencies: [003-01, 002-01, adr-0001, adr-0002]
last_verified: 2026-06-18
arch_review: true
code_health_review: true
---

## Slice 004-01 - ci-and-conventional-commit-gate

**Goal:** Add the first release-safe change gates: CI on pull requests and
`main`, plus a conventional commit PR-title check compatible with
release-please.

**DoR:**

- [x] ADR-0001 is accepted.
- [x] ADR-0002 is accepted.
- [x] Spec 003 has established the hybrid plugin baseline.
- [x] Spec 002 has delivered the first release-plan-to-JIG product loop.
- [x] The implementer has rechecked JIG `origin/v2` Spec 013 and Servo Spec
      010 for the current workflow shape.
- [x] The implementer confirms which checks are meaningful for shaper's code at
      implementation time: unit tests, Python syntax checks, spec/status
      linting, manifest validation, and host-package drift checks.

**Acceptance Criteria:**

1. **PR-title gate exists.** Pull requests are checked for conventional commit
   titles that release-please can consume after squash merge.
2. **Allowed release language is documented.** The project documents supported
   commit types and any shaper scopes used by the gate.
3. **CI runs on pull requests and `main`.** CI is triggered for proposed
   changes and the main branch.
4. **CI uses the best available project checks.** At minimum, CI runs the
   available spec/status lint checks and manifest/package validation introduced
   by Spec 003. It adds Python tests and static checks when the project has
   executable code to test.
5. **CI does not create releases.** This slice gates change quality only; no
   release-please or archive upload behavior is introduced here.

**DoD:**

- [x] All ACs pass.
- [x] The PR-title check is demonstrated with at least one passing and one
      failing title example.
- [x] CI passes on the branch after the workflow is added.
- [x] Documentation explains how PR titles affect release notes.
- [x] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled if
      the CI baseline resolves deferred decisions.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, every future release
change starts from the same quality and release-note gate that the automated
release pipeline will consume.

### Deviation log (after reconciliation)

- Implemented the first release-automation gate as two GitHub Actions
  workflows plus repo-owned validation tooling: `.github/workflows/ci.yml`,
  `.github/workflows/pr-title.yml`, `scripts/validate_manifests.py`, and
  `tests/test_release_ci_gate.py`. The CI workflow runs on pull requests and
  `main`; the PR-title workflow enforces scoped conventional-commit titles for
  release-please-compatible squash merges.
- Kept release creation out of scope. This slice does not add release-please,
  changelog/version/tag automation, release archives, or archive upload jobs;
  those remain in later Spec 004 slices.
- Rechecked sibling precedent before implementation. JIG `origin/v2` Spec 013
  and Servo Spec 010 both support the same PR-title / CI / release-please /
  package-job progression. The JIG Spec 061 reference resolved to the current
  `061-dual-host-plugin-artifacts/slice-04-host-explicit-release-zips.md`
  path; the concept matched shaper's host-explicit archive plan even though
  the local filename differed from the shorthand in this spec overview.
- Chose shaper's first CI floor from currently meaningful project checks:
  standard-library unit tests, AST syntax checks, manifest validation,
  committed host-package drift, and spec status-board drift. CI delegates those
  checks to repo-owned scripts/helpers instead of introducing a package manager
  or third-party linter dependency.
- Added `scripts/validate_manifests.py` as a table-driven, reusable validator
  for root and committed host package manifests. Reviewer feedback found and
  fixed two robustness issues before reconciliation: malformed Codex marketplace
  `source` values now report actionable validation errors instead of raising
  `AttributeError`, and failure summaries count valid manifest files rather
  than subtracting total errors.
- Added PR-title examples in tests. The passing/failing examples use a
  test-local matcher that reads the workflow's `subjectPattern` so the
  demonstration stays tied to the configured GitHub Action rule.
- Reconciled docs and generated host packages. README now documents the allowed
  PR-title release language; `docs/architecture.md` records the change-quality
  gate as a contract surface; `docs/refinement-todo.md` marks the first CI/CD
  gate resolved while leaving release-please and host-explicit archives deferred.
- Accepted major-version action pins for this slice (`actions/checkout@v4`,
  `actions/setup-python@v5`, `amannn/action-semantic-pull-request@v5`) as the
  current sibling-aligned workflow convention and recorded the arch-review
  supply-chain hardening note as non-blocking. Added `permissions: contents:
  read` to CI after review so the workflow follows least-privilege defaults.
- No new ADR was written. ADR-0002 already chooses the release-automation model;
  this slice implements the first reversible workflow/config layer of that
  decision.
- Non-blocking code-health follow-ups remain logged here rather than turned
  into new work: `.github/workflows/ci.yml` mirrors the `.jig/lint-command`
  Python file list, PR-title types appear in both workflow YAML and tests, and
  versioned manifest paths are a second subset of `MANIFESTS`. These are
  acceptable at current size; revisit if another release-gate slice expands the
  file list, title policy, or versioned manifest set.
