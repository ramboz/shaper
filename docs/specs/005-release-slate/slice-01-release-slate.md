---
status: RECONCILED
dependencies: [002-01, adr-0003]
last_verified: 2026-06-18
arch_review: true
---

## Slice 005-01 - release slate

**Goal:** A maintainer can run `shaper:release-slate` to review and update a
compact release slate without creating a backlog or duplicating JIG status.

**DoR:**

- [x] Spec 002 is DONE.
- [x] ADR-0003 is accepted.
- [x] At least one release-plan fixture exists for verification.

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

- [x] All ACs pass.
- [x] Verification covers candidate, committed, shipping, shipped, dropped, and
      empty-state paths.
- [x] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, the maintainer has a
usable release-slate view that supports an actual release decision without
becoming a hidden backlog.

### Deviation log (after reconciliation)

- Implemented `shaper:release-slate` as a deterministic standard-library helper
  plus skill instructions, matching the existing `shape-release` / `cutline`
  source-and-host-package pattern.
- Added verification fixtures for candidate, committed, shipping, shipped,
  dropped, stale backlog/status-board rows, JIG handoff links without copied
  lifecycle state, host-package inclusion, and the no-plan empty state.
- Added a status parser regression for release plans that include the full
  allowed-status catalog in their `## Status` section, so actual status lines
  win over explanatory text.
- Reconciled docs to describe `release-slate` as shipped and to record that it
  reads JIG handoff links from release plans, not `docs/specs/README.md`
  lifecycle state.
- Hardened release-archive smoke tests so shipped product skills now require
  `shape-release`, `cutline`, and `release-slate` skill docs and helper scripts
  in both Claude and Codex archive shapes.
- Non-blocking craft note: the older Spec 002 happy-path fixture still
  hand-edits the slate; the dedicated release-slate tests now cover the helper
  behavior directly, so no follow-up was split from this slice.
