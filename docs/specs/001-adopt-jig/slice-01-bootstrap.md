---
status: DONE
dependencies: []
last_verified:
---

## Slice 001-01 — bootstrap

**Goal:** Adopt jig in shaper by running `scaffold-init`, so the
project opens with the jig docs tree, an honest AGENTS.md, a populated
status board, and the `.codex/` runtime machinery — a complete pattern
for the spec-driven loop from turn one.

**DoR:**
- ✅ The target directory exists and is not already scaffolded (no
  `scaffold.json`).
- ✅ `scaffold-init` is installed (plugin or scaffold-mode) and runnable.
- ✅ No pre-existing spec-driven layout that would route to `/jig:migrate`.

**Acceptance Criteria:**

1. **The docs tree exists.** `docs/product-vision.md`,
   `docs/workflow.md`, `docs/architecture.md`, `docs/conventions.md`,
   `docs/refinement-todo.md`, `docs/inbox.md`, the `docs/memory/` stubs,
   `docs/specs/README.md`, and `docs/decisions/README.md` are all
   present after the scaffold runs.
2. **AGENTS.md is present and honest.** A generated `AGENTS.md` exists at
   the project root, carries the jig watermark, and points at the docs
   above without claiming work that has not happened.
3. **The status board is populated.** `docs/specs/README.md` contains a
   real row for `001-01 — bootstrap` marked `DONE`.
4. **A next step exists.** `docs/specs/002-shaper-mvp/spec.md` is present
   as a `DRAFT` spec for shaper's first real implementation work.
5. **The seed is well-formed.** The emitted `001-adopt-jig` and
   `002-shaper-mvp` specs follow jig's spec/slice structure and validated
   clean when scaffolded. (Structural linting runs in jig's own dev/CI
   environment — the scaffolded project does not ship `spec_lint.py`.)

**DoD:**
- [x] All ACs pass — Verified by scaffold-completion check (deterministic
      template output; first subagent review is your spec 002).
- [x] Implementer test coverage exercises each AC — Verified by
      scaffold-completion check (the scaffold's own test suite asserts the
      emitted tree; this slice ships no new test of its own).
- [x] Reviewer-subagent review — not applicable: deterministic template
      output, nothing authored to review. Your first subagent review is
      spec 002.
- [x] Implementation review — satisfied by the scaffold-completion check
      (deterministic output, not a subagent verdict).
- [x] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.
- [x] `docs/refinement-todo.md` updated if any decisions were deferred —
      none were; the stub doc is in place.

**Anti-horizontal-phasing check:** After this slice lands, a developer
opening shaper finds a complete `DONE` worked example *and* a
clear next step, so the spec-driven loop is imitable from the first turn
instead of being skipped. End-to-end observable; one slice.

### Deviation log (after reconciliation)

The original spec is preserved above. Implementation notes:

1. **Tier 2 offered but not installed.** Scaffold-init offered the Tier 2
   skill group because shaper will involve AI-native project work, but the
   scaffold installed only tier-0. `docs/memory/people.md` was not created
   because the project is explicitly solo for now.
2. **Review boxes satisfied by the deterministic completion check, not a
   subagent.** This slice's output is deterministic template emission —
   reviewing template copies with a subagent would be rubber-stamp
   theater. The review boxes above are annotated as verified by the
   scaffold-completion check accordingly. Your first *real* subagent
   review is spec 002, where there is genuine implementation to inspect.
