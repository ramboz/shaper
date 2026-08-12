---
status: DONE
skill: shape-release
use_cases: []
---

<!-- jig self-defining vocabulary (soft, forward-only): expand each acronym on first use and link the term to docs/memory/glossary.md (or jig's lexicon). See docs/workflow.md "Self-defining vocabulary". -->

# Spec 008: Vertical-scope shaping

> Implements [ADR-0005](../../decisions/adr-0005-vertical-scope-shaping-and-architecture-appetite.md).

## Overview

shaper today shapes a release's **appetite and boundaries** but stops short of
two things that would let vertical-first thinking propagate from raw intent down
into jig's specs:

1. New work in the solution outline is not decomposed into an **ordered set of
   vertical scopes** (thinnest end-to-end path first, then thicken). The
   template's only forward-delivery field is a single-line "Main user-facing
   path" ([templates/release-plan.md:26](../../../templates/release-plan.md));
   the cutline decomposes only *existing* jig specs.
2. The `## JIG Handoff` block is scope-only
   ([templates/release-plan.md:65-70](../../../templates/release-plan.md)) — it
   carries no stance on how lean the architecture should be, so nothing at the
   cheapest-to-prevent altitude discourages over-engineering.

Per [ADR-0005](../../decisions/adr-0005-vertical-scope-shaping-and-architecture-appetite.md)
(Option C), this spec adds exactly two capabilities and no more, using verbs
shaper already owns:

- **Vertical-scope decomposition** — `shape-release` captures new work as an
  ordered list of thin, demoable vertical scopes (walking-skeleton shape).
- **Architecture *appetite*** — a bounded, advisory leanness ceiling in the
  handoff (appetite / no-gos / risk-pointer only; **never** ADRs, design, or
  module boundaries — that guardrail is jig's boundary, enforced in the skill).

The retrospective complement — a jig-side leanness/YAGNI review lens — is built
in jig, not here. This spec owns only the prospective, shaping-time half.

## Assumptions

None. The two grounded claims this spec rests on are verified in
[ADR-0005 `## Assumptions`](../../decisions/adr-0005-vertical-scope-shaping-and-architecture-appetite.md)
(A1: current template/skill carry no vertical-scope or architecture stance —
read from the files; A2: jig owns architecture decisions). No unverified
load-bearing runtime assumptions remain at this altitude.

## Decomposition

SPIDR — split by **Path** then **Rules** (Spike not needed; the shape is known
from ADR-0005):

- **008-01 (Path)** — the happy path of shaping *new* work vertically: capture
  an ordered vertical-scope list in the template + `shape-release`.
- **008-02 (Rules)** — the guardrail rule that keeps architecture *appetite*
  from becoming architecture *decisions*: add the appetite field to the handoff
  and enforce the "appetite/no-gos/risk-pointer only" boundary in the skill.

**Out of scope (deferred).** Teaching `cutline` to emit vertical-scope-ordering
advice for *new* work (ADR-0005 open question 2) is not in this spec; it stays a
refinement-todo item until a real release exercises 008-01/02 and shows whether
`cutline` needs it. Recording no ADRs / no architecture decisions in shaper is a
hard boundary (ADR-0005), not a slice.

## Slices

- [008-01 — vertical-scope-outline](slice-01-vertical-scope-outline.md)
- [008-02 — architecture-appetite-handoff](slice-02-architecture-appetite-handoff.md)
