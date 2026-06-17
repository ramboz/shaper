---
status: DRAFT
dependencies: [007-01, adr-0004]
last_verified:
arch_review: true
---

## Slice 007-02 - optional servo signal read

**Goal:** `shaper:release-check` can include optional servo quality signals when
the target repo has accepted servo artifacts, while staying read-only and
degrading gracefully when servo is absent.

**DoR:**

- [ ] Slice 007-01 is DONE.
- [ ] Future ADR-0004 defines the JIG/servo read boundary and is accepted.
- [ ] The implementer has fixture coverage for absent servo artifacts and at
      least one accepted servo signal family.

**Acceptance Criteria:**

1. **Servo signals are read only through the accepted boundary.** The
   implementation reads only the artifacts allowed by ADR-0004.
2. **No servo loops run.** The skill does not invoke servo loops, define
   oracles, modify servo state, or trigger heartbeat dispatch.
3. **Signal absence degrades gracefully.** Missing servo artifacts are reported
   as not evaluated, not as a failure.
4. **Signal disagreement is advisory.** If JIG status and servo signals point in
   different directions, the skill explains the disagreement and recommends a
   human decision rather than overriding either source.

**DoD:**

- [ ] All ACs pass.
- [ ] Verification covers absent servo, readable pass signal, readable failing
      signal, and JIG/servo disagreement.
- [ ] No servo or JIG lifecycle state is mutated in verification.
- [ ] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, release-check
decisions can account for servo evidence without shaper becoming servo.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
