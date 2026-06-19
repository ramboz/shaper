---
status: DONE
dependencies: [002-01, 005-01, adr-0003]
last_verified: 2026-06-19
arch_review: true
---

## Slice 006-01 - scope-audit-and-hammering

**Goal:** A maintainer can run `shaper:scope-audit` against a release plan and
receive advisory scope recommendations without mutating JIG state.

**DoR:**

- [x] Spec 002 is DONE.
- [x] Spec 005 is DONE.
- [x] ADR-0003 is accepted.
- [x] Fixtures cover at least one release plan and linked JIG specs.

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

- [x] All ACs pass.
- [x] Verification covers appetite leakage, nice-to-have creep, no-go conflict,
      unresolved rabbit hole, JIG overreach, orphan spec, and clean-pass paths.
- [x] No JIG lifecycle state is mutated in verification.
- [x] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, the maintainer can
make a real scope tradeoff against a release plan.

### Deviation log (after reconciliation)

- Implemented `shaper:scope-audit` as a deterministic standard-library helper
  plus skill instructions, following the existing `shape-release`, `cutline`,
  and `release-slate` source/host-package pattern.
- Added advisory grouped findings for appetite leakage, nice-to-have creep,
  unresolved rabbit holes/no-go conflicts, JIG overreach, orphan specs, and
  clean-pass output. The helper reports files read and ends with explicit
  patch-ready/non-mutating guidance.
- Added focused unittest coverage for each acceptance criterion, including
  linked slice-file acceptance criteria, specs absent from the status board,
  short no-go terms such as `UI`, no-JIG release-plan-only findings, clean
  non-goal restatements, out-of-repo release path rejection, and a full
  `docs/specs` before/after snapshot proving JIG lifecycle state is untouched.
- Updated release archive required-file contracts, CI syntax checks,
  `.jig/lint-command`, README/root docs, and committed Claude/Codex host
  packages so `scope-audit` ships with the plugin surfaces.
- Reconciled architecture docs to include all public scope-audit rule
  categories: appetite leakage, nice-to-have creep, unresolved risks/rabbit
  holes, no-go conflicts, orphan specs, and JIG work beyond the cutline.
- Review follow-up: craft noted that
  `tests/test_release_plan_handoff.py` still has an older host-package fixture
  focused on the first product skills; distribution is covered by archive
  required-file tests and host-package drift checks, so this remains
  non-blocking.
- Architecture note: `scope-audit` extends the existing read-only helper model
  without adding a state store, workflow ownership, or host-specific adapter.
- Reconciliation review (pass): contract-surface suggestion (non-blocking) to
  list scope-audit's `# Scope Audit` report under `docs/architecture.md`
  § Contract surfaces if/when other report-emitting skills are added; the report
  shape is already documented in `skills/scope-audit/SKILL.md` § Output shape and
  covered by `tests/test_scope_audit.py`.
