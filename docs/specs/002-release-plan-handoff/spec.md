---
status: DRAFT
adr_required: true
adr: ../../decisions/adr-0003-release-plan-no-backlog-slate.md
last_verified:
---

# Spec 002: First release-plan-to-JIG handoff loop

## Overview

shaper's first product slice should prove one useful vertical loop: turn raw
product intent into a release plan, compare that release plan against existing
JIG specs/slices, and produce a non-mutating cutline plus compact release slate.

This spec deliberately avoids treating `mvp`, `v1`, or `v2` as canonical
architecture. Those remain possible release slugs, not shaper concepts. The
core concepts are release plan, appetite, risks/rabbit holes, no-gos, cutline,
JIG handoff, and release check.

## Relationship to JIG and servo

- JIG owns supervised spec-driven development: product vision, architecture,
  ADRs, SPIDR slicing, spec lifecycle, independent review, and slice landing.
- Servo owns eval-driven and unattended agent loops: project-specific oracles,
  quality gates, agent loops, hooks, variant races, and scheduled heartbeat
  discovery.
- shaper sits before and above JIG specs: it shapes raw product intent into a
  bounded release plan, then hands implementation-ready work to JIG.
- shaper may consume servo signals in later `release-check` work, but this
  first product slice must not run loops or define quality oracles.

## Dependencies

This product slice should not implement plugin packaging itself. It depends on:

- [Spec 003: Hybrid plugin baseline](../003-hybrid-plugin-baseline/spec.md)
- [ADR-0001: Hybrid plugin baseline](../../decisions/adr-0001-hybrid-plugin-baseline.md)
- [ADR-0003: Release plan and no-backlog slate artifact model](../../decisions/adr-0003-release-plan-no-backlog-slate.md)

## Scope

In scope:

- A release-plan Markdown template.
- A `shape-release` skill that elicits problem/baseline, appetite, solution
  outline, risks/rabbit holes, no-gos, release criteria, and JIG handoff.
- A `cutline` skill that reads existing JIG specs/status board and proposes
  include/defer/split/risk-first recommendations without mutating them.
- A compact `docs/releases/README.md` release slate.
- Clear docs explaining how shaper sits beside JIG and servo.

Out of scope:

- Task boards, sprint planning, estimation, backlog grooming, and issue-system
  replacement.
- Silent mutation of JIG spec states.
- `release-slate` automation beyond the minimal slate required for this handoff
  loop.
- `scope-audit` automation.
- `release-check` automation.
- Servo oracle/eval loops or unattended agent loops.
- Web UI.

## SPIDR analysis

**Chosen axis: Path - happy release-plan-to-JIG handoff path first.**

The first path is: a maintainer has raw product intent and a repo with
JIG-style specs. shaper helps them create a shaped release plan, then proposes
an include/defer/split/risk-first cutline without mutating JIG files. That path
crosses the artifact model, skill interface, JIG read boundary, and
documentation boundary in one end-to-end slice.

**Rejected splits:**

- Interface-only split: building only `shape-release` would create an artifact
  but would not prove the JIG handoff boundary.
- Data-only split: building only `docs/releases/` templates would be horizontal
  phasing.
- Rules-only split: implementing only cutline classification rules would lack
  the shaped appetite that makes the rules meaningful.
- Spike: ADR-0003 now fixes the artifact model enough for implementation to
  proceed; deviations can be captured during reconciliation.

## Slices

- [002-01 - release-plan handoff](slice-01-release-plan-handoff.md)
