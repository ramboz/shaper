# Spec Status Board

> Status: Draft (wizard-generated)
>
> Current state of all specs for shaper. Update after each slice transition.
>
> A leading 🔬 in the Slice column flags slices marked `kind: spike` in
> their frontmatter — timeboxed investigation, not feature work. The
> marker is recomputed from each slice's `kind:` field on every regen
> by `workflow.py status-board`; it is never stored separately in this
> file.

| Spec | Slice | Status | Notes |
|------|-------|--------|-------|
| [001-adopt-jig](001-adopt-jig/spec.md) | 001-01 — bootstrap | **DONE** |  |
| [002-release-plan-handoff](002-release-plan-handoff/spec.md) | 002-01 - release-plan handoff | **DONE** |  |
| [003-hybrid-plugin-baseline](003-hybrid-plugin-baseline/spec.md) | 003-01 - hybrid-plugin-baseline | **DONE** |  |
| [004-release-automation](004-release-automation/spec.md) | 004-01 - ci-and-conventional-commit-gate | **DONE** |  |
| [004-release-automation](004-release-automation/spec.md) | 004-02 - release-please-pipeline | **DONE** |  |
| [004-release-automation](004-release-automation/spec.md) | 004-03 - host-explicit-release-zips | **DONE** |  |
| [005-release-slate](005-release-slate/spec.md) | 005-01 - release slate | **DONE** |  |
| [006-scope-audit](006-scope-audit/spec.md) | 006-01 - scope-audit-and-hammering | **DONE** |  |
| [007-release-check](007-release-check/spec.md) | 007-01 - JIG-only release check | **DONE** |  |
| [007-release-check](007-release-check/spec.md) | 007-02 - optional servo signal read | **DONE** |  |
| [008-vertical-scope-shaping](008-vertical-scope-shaping/spec.md) | 008-01 — vertical-scope-outline | **DONE** |  |
| [008-vertical-scope-shaping](008-vertical-scope-shaping/spec.md) | 008-02 — architecture-appetite-handoff | **DONE** |  |
| [009-copilot-third-host](009-copilot-third-host/spec.md) | 009-01 - installed-copilot-skills | RECONCILED (copilot-third-host) |  |
| [009-copilot-third-host](009-copilot-third-host/spec.md) | 009-02 - copilot-release-artifact | READY_FOR_REVIEW (copilot-third-host) |  |

## Richer-skill selection audit (spec 096-05)

Advisory (ADR-0040 auditability — never blocks). Regenerated from `reviews/slice-*.md` `substrate:` fields.

- **0** pass(es) recorded `not-shown` (selection step did not run — the kill-criterion-1 defect signal).
- **0** pass(es) recorded `non-interactive` (declared no-orchestrator / CI).
- **1** shown-and-declined anomaly(ies) (a high-confidence richer skill was shown and not applied):
  - `009-copilot-third-host/slice-01-craft.md` — applied `pr-review`; declined: scout-pr-review
