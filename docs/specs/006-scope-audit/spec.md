---
status: IN_PROGRESS
skill: scope-audit
tier: product
adr_required: true
adr: ../../decisions/adr-0003-release-plan-no-backlog-slate.md
last_verified:
---

# Spec 006: Scope audit and scope hammering

## Overview

shaper should help maintainers notice when JIG specs or acceptance criteria are
exceeding a release plan's appetite. The public skill remains
`shaper:scope-audit`, while the product framing is scope tightening around a
specific release plan.

## Goals

1. Detect appetite leakage.
2. Detect nice-to-have creep.
3. Detect unresolved rabbit holes and no-go violations.
4. Detect JIG specs or slices that exceed the release-plan cutline.
5. Detect orphan JIG specs that are not linked from the current release plan or
   release slate.
6. Produce recommendations only.

## Non-goals

- No mutation of JIG lifecycle state.
- No backlog grooming.
- No release automation.
- No servo signal consumption.
- No ship/stop verdict.

## SPIDR analysis

**Chosen axis: Rules.**

The value is in applying a focused set of scope rules to existing release-plan
and JIG artifacts. The first slice should cover the core rules together because
each is needed to make scope auditing useful.

**Rejected splits:**

- Interface-only: a skill shell without the scope rules would not help.
- Data-only: parsing artifacts without recommendations would be horizontal.
- Spike: the first rule set is straightforward enough to implement and refine
  via reconciliation.

## Dependencies

- [ADR-0003: Release plan and no-backlog slate artifact model](../../decisions/adr-0003-release-plan-no-backlog-slate.md)
- [Spec 002: Release plan to JIG handoff](../002-release-plan-handoff/spec.md)
- [Spec 005: Release slate overlay](../005-release-slate/spec.md)

## Slices

- [006-01 - scope-audit-and-hammering](slice-01-scope-audit-and-hammering.md)
