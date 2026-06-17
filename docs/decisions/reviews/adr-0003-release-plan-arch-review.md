# Architecture Review: ADR-0003 release plan and no-backlog slate artifact model

## Summary

ADR-0003 is ready to proceed after the vocabulary pivot to release terminology.
The important correction is using Shape Up as design inspiration while exposing
release-plan and release-slate terms that fit the JIG/servo context.

## Strengths

- Uses one artifact family, `docs/releases/<slug>.md`, which is easier for
  non-Shape-Up users than separate Shape Up-native artifact families.
- Keeps the no-backlog constraint explicit through `docs/releases/README.md` as
  a compact release slate.
- Preserves the useful mechanics: appetite, no-gos, risks/rabbit holes,
  cutlines, JIG handoff, and release checks.

## Findings

### Risks

**1. Release slate could become a backlog**

If `docs/releases/README.md` accumulates every dropped idea, it recreates the
roadmap/backlog problem in Markdown. The ADR mitigates this by limiting the
slate to active or currently relevant release plans.

*Perspective: Product and AI-native maintainability*
*Severity: Moderate*

### Gaps

**1. Servo read boundary is intentionally deferred**

The skill surface names `shaper:release-check`, but servo signal consumption is
not safe to define inside ADR-0003 because servo has multiple possible signal
families. The ADR correctly defers this to a later JIG/servo read-boundary ADR.

*Perspective: Technical soundness*
*Severity: Moderate*

## Completeness Check

The proposal covers problem, scope, alternatives, key decisions, artifact
interfaces, and follow-up work. It intentionally does not define the servo
signal contract.

## Verdict

**Ready to proceed:** Yes
**Reasoning:** The accepted ADR uses release terminology for public interfaces
while preserving the no-backlog and non-mutating constraints.
