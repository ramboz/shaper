# Release Plan: <title>

## Status

`candidate`

Allowed statuses: `candidate`, `committed`, `shipping`, `shipped`, `dropped`.
Do not move a plan from `candidate` to `committed` without an explicit user
decision.

## Problem / Baseline

- Current baseline:
- Problem this release addresses:
- Why now:

## Appetite

- Time or attention this release is worth:
- Fixed constraints:
- Variable scope:

## Solution Outline

- Proposed shape:
- Main user-facing path:
- Important non-goals:

### Vertical Scopes (delivery order)

Ordered thinnest-demoable-path-first. Each scope must deliver end-to-end,
demoable value on its own (not "just the data model" / "just the parser").

1. _TBD — thinnest walking-skeleton path and its demoable outcome._

## Risks / Rabbit Holes

- Risk:
  - Why it matters:
  - Retirement path:

## No-Gos

- This release will not:

## Cutline

### Include

| Item | Evidence | Rationale |
|---|---|---|
| _TBD_ | _TBD_ | _TBD_ |

### Defer

| Item | Evidence | Rationale |
|---|---|---|
| _TBD_ | _TBD_ | _TBD_ |

### Split

| Item | Evidence | Rationale |
|---|---|---|
| _TBD_ | _TBD_ | _TBD_ |

### Risk-First

| Item | Evidence | Rationale |
|---|---|---|
| _TBD_ | _TBD_ | _TBD_ |

## JIG Handoff

- Candidate JIG specs or slices:
- New JIG work to draft:
- Patch-ready instructions, if any:
- Non-mutating notes:

### Architecture appetite

A leanness ceiling jig reads before drafting specs. Appetite / no-gos /
spike pointer only — shaper never names an ADR, module boundary, mechanism,
or design; jig decides those. This is the prospective half; jig's
leanness/YAGNI review lens is the retrospective complement, enforced at jig
review — not here.

- Investment posture (upper bound — "at most", never "at least"): _TBD_
- Over-investment no-gos (over-builds to refuse): _TBD_
- Spike (architectural risk to retire early): _TBD_

## Release-Check Criteria

- Before this release can ship:
- Evidence to inspect:
- Known missing signals:
