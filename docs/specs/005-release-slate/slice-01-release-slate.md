---
status: DRAFT
dependencies: [002-01, adr-0003]
last_verified:
arch_review: true
---

## Slice 005-01 - release slate

**Goal:** A maintainer can run `shaper:release-slate` to review and update a
compact release slate without creating a backlog or duplicating JIG status.

**DoR:**

- [ ] Spec 002 is DONE.
- [ ] ADR-0003 is accepted.
- [ ] At least one release-plan fixture exists for verification.

**Acceptance Criteria:**

1. **The skill reads release plans.** `shaper:release-slate` discovers
   `docs/releases/*.md` and the existing `docs/releases/README.md` when present.
2. **The slate is compact and current.** The skill writes or updates
   `docs/releases/README.md` with sections for candidate, committed, shipping,
   recently shipped, and relevant dropped/no-go release plans.
3. **No backlog behavior.** The skill does not preserve every old idea by
   default, does not assign priority ranks, and does not create a long-lived
   queue of unselected release ideas.
4. **No JIG status duplication.** Entries link to JIG specs or slices when
   useful but do not copy lifecycle status from `docs/specs/README.md`.
5. **Graceful empty state.** In a repo with no release plans, the skill creates
   an empty release slate with no invented work.

**DoD:**

- [ ] All ACs pass.
- [ ] Verification covers candidate, committed, shipping, shipped, dropped, and
      empty-state paths.
- [ ] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, the maintainer has a
usable release-slate view that supports an actual release decision without
becoming a hidden backlog.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
