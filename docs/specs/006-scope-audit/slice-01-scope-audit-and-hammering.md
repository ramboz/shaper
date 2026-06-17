---
status: DRAFT
dependencies: [002-01, 005-01, adr-0003]
last_verified:
arch_review: true
---

## Slice 006-01 - scope-audit-and-hammering

**Goal:** A maintainer can run `shaper:scope-audit` against a release plan and
receive advisory scope recommendations without mutating JIG state.

**DoR:**

- [ ] Spec 002 is DONE.
- [ ] Spec 005 is DONE.
- [ ] ADR-0003 is accepted.
- [ ] Fixtures cover at least one release plan and linked JIG specs.

**Acceptance Criteria:**

1. **Appetite leakage is detected.** The skill flags work that appears outside
   the release plan's appetite or cutline.
2. **Nice-to-have creep is detected.** The skill flags requirements that read as
   optional polish, stretch scope, or post-release additions.
3. **Rabbit holes and no-gos are checked.** The skill flags unresolved rabbit
   holes and JIG work that conflicts with explicit no-gos.
4. **JIG overreach is detected.** The skill flags specs or slices whose
   acceptance criteria exceed the release-plan cutline.
5. **Orphan specs are detected.** The skill reports JIG specs that are not
   referenced by the current release plan or release slate when they appear
   relevant to the same release-shaping context.
6. **Output is advisory.** The skill writes recommendations or patch-ready
   instructions only; it never edits JIG lifecycle state.

**DoD:**

- [ ] All ACs pass.
- [ ] Verification covers appetite leakage, nice-to-have creep, no-go conflict,
      unresolved rabbit hole, JIG overreach, orphan spec, and clean-pass paths.
- [ ] No JIG lifecycle state is mutated in verification.
- [ ] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, the maintainer can
make a real scope tradeoff against a release plan.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
