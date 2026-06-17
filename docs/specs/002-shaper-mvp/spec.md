---
status: DRAFT
last_verified:
---

# Spec 002: Shaper MVP release-shaping loop

## Overview

shaper's MVP should prove one useful vertical loop: turn raw product intent into a shaped release bet, compare that bet against existing JIG specs/slices, and produce a non-mutating cutline/roadmap overlay that makes MVP/v1/v2 tradeoffs explicit.

The MVP is not a complete agile system. It should create just enough repo-native Markdown structure and skill behavior for a maintainer to decide what belongs in a release, what is explicitly out, what risks must retire before implementation, and what JIG work should be included or deferred.

## Relationship to JIG and servo

- JIG owns supervised spec-driven development: product vision, architecture, ADRs, SPIDR slicing, spec lifecycle, independent review, and slice landing.
- Servo owns eval-driven and unattended agent loops: project-specific oracles, quality gates, agent loops, hooks, variant races, and scheduled heartbeat discovery.
- shaper sits before and above JIG specs: it shapes raw product intent into bounded release bets, then hands implementation-ready work to JIG.
- shaper may consume servo signals in later release-readiness work, but this MVP must not run loops or define quality oracles.

## MVP scope

In scope:

- A shaped-bet Markdown template.
- A `shape-bet` skill that elicits outcome, appetite, must-haves, no-goes, risks, and release criteria.
- A `cutline` skill that reads existing JIG specs/status board and proposes MVP/v1/v2 include/defer groupings without mutating them.
- A non-duplicating roadmap/bets overlay.
- Clear docs explaining how shaper sits beside JIG and servo.

Out of scope:

- Task boards, sprint planning, estimation, and issue-system replacement.
- Silent mutation of JIG spec states.
- Release-readiness automation.
- Scope-audit automation beyond the MVP cutline recommendation.
- Servo oracle/eval loops or unattended agent loops.
- Web UI.

## SPIDR analysis

**Chosen axis: Path - happy release-shaping path first.**

The first path is: a maintainer has raw product intent and a repo with JIG-style specs. shaper helps them create a shaped MVP bet, then proposes an include/defer cutline without mutating JIG files. That path crosses the artifact model, skill interface, JIG read boundary, and documentation boundary in one end-to-end slice.

**Rejected splits:**

- Interface-only split: building only `shape-bet` would create an artifact but would not prove the JIG handoff boundary.
- Data-only split: building only `docs/bets/` templates would be horizontal phasing.
- Rules-only split: implementing only cutline classification rules would lack the shaped appetite that makes the rules meaningful.
- Spike: the artifact model is open, but not so unknown that implementation must stop for research first.

## Slices

1. **`002-01 mvp-release-shaping-loop`** - Deliver the first usable shaper path: shaped-bet template, `shape-bet` skill, `cutline` skill, non-duplicating bet/roadmap overlay, and relationship docs.
