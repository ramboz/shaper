---
status: DRAFT
dependencies: [002-01, 006-01, adr-0003]
last_verified:
arch_review: true
---

## Slice 007-01 - JIG-only release check

**Goal:** A maintainer can run `shaper:release-check` against a release plan and
receive an advisory ship/cut-scope/stop/re-shape recommendation based on JIG
evidence only.

**DoR:**

- [ ] Spec 002 is DONE.
- [ ] Spec 006 is DONE.
- [ ] ADR-0003 is accepted.
- [ ] Fixtures include release plans linked to JIG specs in multiple states.

**Acceptance Criteria:**

1. **Release criteria are read.** The skill reads appetite, cutline, JIG
   handoff, release-check criteria, rabbit holes, and no-gos.
2. **JIG status is read without mutation.** The skill reads
   `docs/specs/README.md` and linked specs/slices but does not edit lifecycle
   state.
3. **Open risks are surfaced.** The skill reports unresolved risks, rabbit
   holes, and no-go conflicts before recommending ship.
4. **Recommendation is explicit.** Output is one of: ship, cut scope, stop and
   re-shape, or extend only with explicit rationale.
5. **Servo absence is honest.** The JIG-only slice reports servo signals as not
   evaluated rather than unavailable failures.

**DoD:**

- [ ] All ACs pass.
- [ ] Verification covers ship, cut-scope, stop/re-shape, and explicit-extension
      paths.
- [ ] No JIG lifecycle state is mutated in verification.
- [ ] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, a maintainer can make
a real release decision from existing shaper and JIG artifacts.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
