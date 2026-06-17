---
status: DRAFT
dependencies: []
last_verified:
arch_review: true
---

## Slice 002-01 - mvp-release-shaping-loop

**Goal:** A maintainer can create a shaped MVP bet from product intent, run a minimal cutline pass over existing JIG specs/status, and get a non-mutating roadmap/bet overlay that says what is in MVP, what moves to v1/v2, and what is explicitly deferred.

**DoR:**
- [x] `docs/product-vision.md` captures shaper's relationship to JIG and servo.
- [x] `docs/architecture.md` names the initial artifact model and boundaries.
- [x] JIG scaffold artifacts exist in `docs/specs/`.
- [ ] The implementer confirms the exact bet file path for the slice, defaulting to `docs/bets/mvp.md` unless implementation finds a simpler repo-native shape.

**Acceptance Criteria:**

1. **A shaped-bet Markdown template exists.** The implementation adds a template for shaped bets with sections for outcome, appetite, must-haves, no-goes, risks to retire, release criteria, cutline recommendations, JIG handoff, and tempting/deferred work.
2. **`shape-bet` creates or refines a bet without inventing product intent.** The `shape-bet` skill elicits outcome, appetite, must-haves, no-goes, risks, and release criteria, then writes or updates a bet file under the chosen `docs/bets/` shape using the user's words where practical.
3. **`cutline` reads JIG artifacts without mutating them.** The `cutline` skill reads `docs/specs/README.md` and relevant `docs/specs/*` files when present, proposes MVP/v1/v2/include/defer groupings, and does not edit JIG spec lifecycle state.
4. **The roadmap/bet overlay does not duplicate the JIG status board.** The implementation adds a `docs/bets/` overlay that links to JIG specs or slices and records shaper's release recommendation without copying lifecycle status into a second board.
5. **Relationship docs are clear.** User-facing docs explain that JIG owns implementation workflow and spec lifecycle, servo owns eval/oracle loops, and shaper owns release shaping before implementation starts.
6. **Missing sibling tools degrade gracefully.** In a repo without JIG specs, `cutline` reports that no JIG specs/status board were found and still leaves JIG files untouched. In a repo without servo signals, the MVP does not block or pretend release-readiness signals exist.
7. **Deferred work is explicit.** Release-readiness automation, scope-audit automation, servo signal consumption, web UI, task boards, sprint planning, estimation, and issue-system replacement remain out of scope or are captured as deferred follow-up ideas.

**DoD:**
- [ ] All ACs pass.
- [ ] Verification covers the happy path with at least one fixture or transcript: product intent -> shaped bet -> cutline recommendation -> non-duplicating overlay.
- [ ] Verification covers the no-JIG-specs path and confirms no JIG lifecycle state is mutated.
- [ ] `docs/architecture.md` is reconciled if implementation changes the artifact model or module boundaries.
- [ ] `docs/refinement-todo.md` is reconciled: resolved questions are removed or linked to the artifact/spec that resolved them.
- [ ] No ADR is written unless implementation makes a hard-to-reverse decision.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, a maintainer can perform the core shaper workflow end to end. They can shape raw intent into a bet, see a release cutline against JIG work, and hand the bounded implementation work to JIG without shaper becoming a second status board.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
