---
status: RECONCILED
dependencies: [003-01, adr-0001, adr-0003]
last_verified: 2026-06-18
arch_review: true
---

## Slice 002-01 - release-plan handoff

**Goal:** A maintainer can create a release plan from raw product intent, run a
minimal cutline pass over existing JIG specs/status, and get a compact
non-mutating release slate that says which plans are candidate, committed,
shipping, shipped, or dropped.

**DoR:**

- [x] `docs/product-vision.md` captures shaper's relationship to JIG and servo.
- [x] `docs/architecture.md` names the artifact model and boundaries.
- [x] JIG scaffold artifacts exist in `docs/specs/`.
- [x] ADR-0001 is accepted.
- [x] ADR-0003 is accepted.
- [x] Spec 003 establishes the hybrid Codex / Claude Code plugin baseline.

**Acceptance Criteria:**

1. **A release-plan Markdown template exists.** The implementation adds a
   template for release plans with sections for status, problem/baseline,
   appetite, solution outline, risks/rabbit holes, no-gos, cutline, JIG
   handoff, and release-check criteria.
2. **`shape-release` creates or refines a release plan without inventing
   product intent.** The `shape-release` skill elicits the release-plan fields
   and writes or updates `docs/releases/<slug>.md` using the user's words where
   practical.
3. **`cutline` reads JIG artifacts without mutating them.** The `cutline` skill
   reads `docs/specs/README.md` and relevant `docs/specs/*` files when present,
   proposes include/defer/split/risk-first recommendations, and does not edit
   JIG spec lifecycle state.
4. **The release slate does not become a backlog.** The implementation adds or
   updates `docs/releases/README.md` as a compact slate of active candidate,
   committed, shipping, shipped, and currently relevant dropped release plans;
   it does not copy JIG lifecycle status into a second board.
5. **Relationship docs are clear.** User-facing docs explain that JIG owns
   implementation workflow and spec lifecycle, servo owns eval/oracle loops,
   and shaper owns release shaping before implementation starts.
6. **Missing sibling tools degrade gracefully.** In a repo without JIG specs,
   `cutline` reports that no JIG specs/status board were found and still leaves
   JIG files untouched. In a repo without servo signals, this slice does not
   block or pretend release-check signals exist.
7. **Deferred work is explicit.** `release-slate`, `scope-audit`,
   `release-check`, servo signal consumption, web UI, task boards, sprint
   planning, estimation, backlog grooming, and issue-system replacement remain
   out of scope or are captured as deferred follow-up ideas.

**DoD:**

- [x] All ACs pass.
- [x] Verification covers the happy path with at least one fixture or
      transcript: raw intent -> release plan -> JIG cutline recommendation ->
      compact release slate.
- [x] Verification covers the no-JIG-specs path and confirms no JIG lifecycle
      state is mutated.
- [x] Verification covers the no-backlog path and confirms dropped/deferred
      ideas do not accumulate into an evergreen roadmap.
- [x] `docs/architecture.md` is reconciled if implementation changes the
      artifact model or module boundaries.
- [x] `docs/refinement-todo.md` is reconciled: resolved questions are removed
      or linked to the artifact/spec that resolved them.
- [x] No additional ADR is written unless implementation makes a new
      hard-to-reverse decision.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, a maintainer can
perform the core shaper workflow end to end. They can shape raw intent into a
release plan, see a release cutline against JIG work, and hand bounded
implementation work to JIG without shaper becoming a backlog or second status
board.

### Deviation log (after reconciliation)

- Implemented the first product loop as repo-native Markdown plus two product
  skills: `shape-release` and `cutline`. Added
  `templates/release-plan.md`, `docs/releases/README.md`, root skill
  instructions, standard-library helper scripts, and committed host-package
  copies for Claude Code and Codex.
- Kept `release-slate` automation, `scope-audit`, `release-check`, servo signal
  consumption, web UI, task boards, sprint planning, estimation, backlog
  grooming, and issue-system replacement out of scope. README and
  `docs/refinement-todo.md` now distinguish the shipped `shape-release` /
  `cutline` skills from planned later skills.
- The deterministic `cutline.py` helper intentionally remains a shallow first
  pass: it reads the release plan, the JIG status board, and linked spec files
  constrained under `docs/specs/`, but recommendations are based on status-board
  rows plus simple release-plan no-go / risk word matches. Richer semantic
  cutline analysis remains future work.
- Preserved the release-plan template contract during `shape-release` helper
  output: create/refine operations keep the `Cutline` include/defer/split /
  risk-first structure, append supplied refinement text instead of replacing
  prior user wording, and preserve existing release status unless explicitly
  changed.
- Host packages still copy the root README exactly. That leaves repo-relative
  documentation links in installed host READMEs, but the root README now
  accurately describes the shipped host-neutral product skills. Host-specific
  README rewriting remains deferred until host-specific runtime prose or install
  verification needs it.
- No new ADR was written. ADR-0003 already covers the release-plan and
  no-backlog slate artifact model; the new helper behavior is reversible
  implementation detail captured in this slice and refinement notes.
