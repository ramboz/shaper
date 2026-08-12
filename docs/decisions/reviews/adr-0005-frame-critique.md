---
adr: 0005
pass: frame-critique
verdict: pass
reviewer: jig:reviewer (5-round adversarial)
reviewed_at: 2026-08-12T00:34:06Z
prompt_source: review.py frame-critique docs/decisions/adr-0005-vertical-scope-shaping-and-architecture-appetite.md
---

VERDICT: pass

Adversarial frame-critique of ADR-0005 (Vertical-scope shaping and a bounded
architecture-appetite handoff). Passed on the fifth pass after four rounds of
hardening; the four prior `needs-changes` verdicts and their resolutions are the
audit trail for why the accepted frame is trustworthy.

## Load-bearing assumption tested

That a bounded "architecture *appetite*" can be expressed by shaper without
crossing into jig's "architecture *decisions*" ownership — i.e. that a
non-empty, actionable, non-prescriptive middle exists between vacuity, drift
(usurping jig), and redundancy (already expressible on existing surfaces).

## Why it now passes

The claim was narrowed, round by round, from an overclaim to a true modest
claim:

- **Round 1 (needs-changes):** bounded middle asserted, never shown — no worked
  example proving a line that is release-specific, actionable, non-prescriptive,
  and non-redundant all at once. → Added a worked example + a ceiling-vs-floor
  and axis argument.
- **Round 2 (needs-changes):** the added worked example smuggled in positive
  design ("extend the save path to queue writes… flush on reconnect" picks a
  sync mechanism). → Banned any "leanest architecture is X" slot outright;
  recast the field as strict content model (posture / over-investment no-gos /
  spike), no proposed-shape slot.
- **Round 3 (needs-changes):** the posture spectrum's top value ("durable seam
  because N future releases build on it") was a *floor* and named an interface.
  → Redefined the posture as a strict upper bound at both ends; the high end is
  "durability permitted, not required," names no seam; added a high-end worked
  example at the exact collapse point.
- **Round 4 (needs-changes):** the non-redundancy case overclaimed orthogonality
  ("a magnitude no No-Go can hold"); low end reduces to a graded leanness no-go,
  high end is non-binding. → Conceded the reduction; reframed the field's value
  as the modest, true set: **gradation + always-elicited prompt + considered-
  permission-vs-silence**; dropped the time-appetite analogy; marked the high
  end explicitly informational, not binding.
- **Round 5 (pass):** the modest claim is true and non-design at every point;
  the verb split (shaper = ceiling/appetite, jig = decisions) holds; the
  prospective-MVA gap is at shaper's stated altitude; every failure mode is
  bounded by an explicit content-model ban and falsifiable kill criteria. The
  frame survives the redundancy horn (conceded and answered with three things a
  binary exclusion cannot carry) and the round-3 floor attack (rewritten as a
  permission).

## Residual (non-frame, handed to spec 008)

- Field-vs-fold placement of the architecture-appetite content is an open
  question the ADR explicitly defers to spec 008 slice 02 — a design-taste
  choice, not a wrong premise.
- Spec 008 slice 02's AC1 wording ("the leanest architecture that satisfies this
  release") predates the round-2 ban on a positive-shape slot and must be
  reconciled to the accepted content model (posture / over-investment no-gos /
  spike; no "leanest architecture is X" line) during spec authoring review.

Reviewer: jig:reviewer (independent, read-only), 5 adversarial passes.
