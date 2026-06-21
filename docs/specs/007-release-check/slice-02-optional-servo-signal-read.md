---
status: DONE
dependencies: [007-01, adr-0004]
last_verified: 2026-06-20
arch_review: true
---

## Slice 007-02 - optional servo signal read

**Goal:** `shaper:release-check` can include optional servo quality signals when
the target repo has accepted servo artifacts, while staying read-only and
degrading gracefully when servo is absent.

**DoR:**

- [x] Slice 007-01 is DONE.
- [x] ADR-0004 defines the JIG/servo read boundary and is accepted.
- [x] The implementer has fixture coverage for absent servo artifacts and at
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

- [x] All ACs pass.
- [x] Verification covers absent servo, readable pass signal, readable failing
      signal, and JIG/servo disagreement.
- [x] No servo or JIG lifecycle state is mutated in verification.
- [x] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, release-check
decisions can account for servo evidence without shaper becoming servo.

### Deviation log (after reconciliation)

**Implementation summary.** Added optional servo release-signal reads to
`shaper:release-check` using ADR-0004's allowlisted
`docs/servo/release-signals/<release-slug>.md` artifact. The helper now renders
servo status and body-summary evidence, treats absence or unrecognized status as
not evaluated, and calls out JIG/servo disagreement as a human decision point
without letting servo override the JIG/release-plan recommendation.

**Verification.** Extended `tests/test_release_check.py` to cover absent servo
artifacts, readable pass signals, readable failing signals, JIG/servo
disagreement, malformed/unrecognized status handling, and byte-for-byte
non-mutation of both JIG specs and servo signal artifacts. Updated
`tests/test_release_archives.py` and `scripts/build_release_zip.py` so release
archive smoke checks require the shipped `release-check` skill and script.

**Docs and packaging.** Reconciled `skills/release-check/SKILL.md`, README,
`docs/architecture.md`, and `docs/refinement-todo.md` so they describe
release-check as JIG plus optional servo release-signal evidence rather than a
JIG-only or future/deferred surface. Regenerated both committed host packages.

**Review fixes.** Compliance review first found stale README/architecture
language and missing explicit servo non-mutation verification; those were fixed
before the passing compliance verdict. Craft and architecture review nits found
the README skill tree, release archive smoke coverage, and one stale
architecture phrase; those were fixed before the final passing craft and arch
verdicts were recorded.

**Accepted limitations.** `release-check` still does not run servo loops, read
servo runtime state, parse arbitrary servo reports, or define quality oracles.
Those remain servo-owned by design.
