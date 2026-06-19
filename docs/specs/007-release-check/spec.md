---
status: IN_PROGRESS
skill: release-check
tier: product
last_verified:
---

# Spec 007: Release check

## Overview

shaper should eventually answer the release-shaping question: is this release
shippable enough, should scope be cut, should work stop and be reshaped, or is
an extension justified explicitly?

The first slice is JIG-only. Optional servo signal consumption waits for a
future ADR that defines the read boundary.

## Goals

1. Add `shaper:release-check`.
2. Produce advisory ship/cut-scope/stop/re-shape/extend-with-rationale output.
3. Start with JIG-only evidence.
4. Add optional servo signal reads only after the read-boundary ADR exists.

## Non-goals

- No automatic release.
- No mutation of JIG lifecycle state.
- No servo loop execution.
- No oracle definition.
- No task-board or issue-system replacement.

## SPIDR analysis

**Chosen axis: Data.**

The first useful data set is JIG-only: release criteria, JIG status, open
risks, cutline state, and explicit no-gos. Servo signals add a second data set
after their read boundary is accepted.

**Rejected splits:**

- Interface-only: a release-check skill without evidence would be vibes.
- Path-only: ship/cut/stop outcomes all need the same evidence read.
- Spike: JIG-only evidence is clear enough; servo integration is deferred by
  dependency instead.

## Dependencies

- [ADR-0003: Release plan and no-backlog slate artifact model](../../decisions/adr-0003-release-plan-no-backlog-slate.md)
- [Spec 002: Release plan to JIG handoff](../002-release-plan-handoff/spec.md)
- [Spec 006: Scope audit and scope hammering](../006-scope-audit/spec.md)
- Future ADR-0004: JIG/servo read boundary, before servo signal reads.

## Slices

- [007-01 - JIG-only release check](slice-01-jig-only-release-check.md)
- [007-02 - optional servo signal read](slice-02-optional-servo-signal-read.md)
