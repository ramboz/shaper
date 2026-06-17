---
status: DRAFT
skill: release-slate
tier: product
adr_required: true
adr: ../../decisions/adr-0003-release-plan-no-backlog-slate.md
last_verified:
---

# Spec 005: Release slate overlay

## Overview

shaper needs a compact release slate that helps a maintainer see which release
plans are candidates, committed, actively shipping, recently shipped, or
intentionally dropped. It must not become a backlog, priority queue, or duplicate
JIG status board.

## Goals

1. Add `shaper:release-slate`.
2. Maintain `docs/releases/README.md` as the compact release slate.
3. Link to release plans and JIG specs/slices without copying JIG lifecycle
   state or release-plan content.
4. Support explicit dropped/no-go entries only while they remain relevant.

## Non-goals

- No backlog grooming.
- No long-lived priority queue.
- No sprint planning.
- No issue-system replacement.
- No silent mutation of JIG spec states.
- No release automation.

## SPIDR analysis

**Chosen axis: Interface.**

The useful interface is the release-slate view. It is valuable only when it can
read existing release-plan artifacts and produce a compact slate maintainers can
use for the next release decision.

**Rejected splits:**

- Data-only: writing `docs/releases/README.md` without skill behavior would not
  prove the workflow.
- Path-only: candidate-only and committed-only paths would each miss the
  slate's main value: comparison.
- Spike: ADR-0003 defines the artifact model enough for implementation.

## Dependencies

- [ADR-0003: Release plan and no-backlog slate artifact model](../../decisions/adr-0003-release-plan-no-backlog-slate.md)
- [Spec 002: Release plan to JIG handoff](../002-release-plan-handoff/spec.md)

## Slices

- [005-01 - release slate](slice-01-release-slate.md)
