---
status: DRAFT
dependencies: [003-01, adr-0001, adr-0002]
last_verified:
arch_review: true
code_health_review: true
---

## Slice 004-01 - ci-and-conventional-commit-gate

**Goal:** Add the first release-safe change gates: CI on pull requests and
`main`, plus a conventional commit PR-title check compatible with
release-please.

**DoR:**

- [ ] ADR-0001 is accepted.
- [ ] ADR-0002 is accepted.
- [ ] Spec 003 has established the hybrid plugin baseline.
- [ ] The implementer has rechecked JIG `origin/v2` Spec 013 and Servo Spec
      010 for the current workflow shape.
- [ ] The implementer confirms which checks are meaningful for shaper's code at
      implementation time.

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

- [ ] All ACs pass.
- [ ] The PR-title check is demonstrated with at least one passing and one
      failing title example.
- [ ] CI passes on the branch after the workflow is added.
- [ ] Documentation explains how PR titles affect release notes.
- [ ] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled if
      the CI baseline resolves deferred decisions.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, every future release
change starts from the same quality and release-note gate that the automated
release pipeline will consume.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
