---
status: DONE
dependencies: [002-01, 006-01, adr-0003]
last_verified: 2026-06-19
arch_review: true
---

## Slice 007-01 - JIG-only release check

**Goal:** A maintainer can run `shaper:release-check` against a release plan and
receive an advisory ship/cut-scope/stop/re-shape recommendation based on JIG
evidence only.

**DoR:**

- [x] Spec 002 is DONE.
- [x] Spec 006 is DONE.
- [x] ADR-0003 is accepted.
- [x] Fixtures include release plans linked to JIG specs in multiple states.

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

- [x] All ACs pass.
- [x] Verification covers ship, cut-scope, stop/re-shape, and explicit-extension
      paths.
- [x] No JIG lifecycle state is mutated in verification.
- [x] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, a maintainer can make
a real release decision from existing shaper and JIG artifacts.

### Deviation log (after reconciliation)

**Implementation summary.** Added the `release-check` skill
(`skills/release-check/SKILL.md` + `scripts/release_check.py`), a 13-test suite
(`tests/test_release_check.py`), wired both into `.jig/lint-command` and the CI
`check_python_syntax` step, regenerated both host packages, and updated
`README.md` and `docs/architecture.md`. No JIG lifecycle state is mutated; the
non-mutation contract is test-enforced (byte-equality before/after).

**Design decisions.**

- The recommendation decision tree is deterministic: no-go conflict or
  no-DONE-in-scope → `stop and re-shape`; incomplete work → `cut scope`
  (or `extend only with explicit rationale` when the plan carries an
  `## Extension` section); unresolved rabbit hole with no scope to cut →
  `stop and re-shape`; all clear → `ship`. `extend` is never invented — it
  requires an explicit extension rationale in the release plan, faithful to
  the fixed-appetite shaping model.
- Board/spec/slice parsing helpers are inlined (near-verbatim from
  `scope_audit.py`) rather than shared, because `scripts/` is not copied into
  host packages — only `skills/` is — so each skill must be self-contained.

**Review deviations (from the three review passes).**

- Craft blocker fixed: a backslash inside an f-string expression was a Python
  3.11 `SyntaxError` (CI runs 3.11/3.12); extracted to a plain statement.
- Craft blocker fixed: the new script and test were missing from CI's explicit
  `check_python_syntax` list; added.
- Craft nit fixed: softened "Active JIG work conflicts" rationale wording, since
  release-check intentionally flags DONE work that crosses a no-go.
- Compliance nit fixed: added a test for the cut-scope-with-unresolved-risk
  rationale branch; de-duped `jig_files_read`; documented the matching
  heuristic and accepted release-input shapes in SKILL.md "Matching notes".

**Accepted limitations (deferred, non-blocking).**

- The no-go matcher is heuristic (word-subset + phrase), so it can over-match on
  shared vocabulary and under-match across singular/plural wording — documented
  in SKILL.md as a prompt-to-confirm, not a verdict.
- Board/spec-parsing helpers are now triplicated across `cutline`,
  `scope-audit`, and `release-check`. A shared module is a candidate for a
  future spike if a fourth consumer appears; extracting now is constrained by
  host-package self-containment.
- Servo signal reads remain deferred to slice 007-02 behind the future
  read-boundary ADR (ADR-0004).
