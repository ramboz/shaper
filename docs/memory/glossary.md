# Glossary

> Status: Draft (wizard-generated)
>
> Domain terms and project-specific vocabulary for shaper. Loaded on demand
> when the hot cache (AGENTS.md) misses. Update via `/jig:memory-sync` or when
> `jig-memory-scan` surfaces an unknown reference.
>
> When `jig-memory-scan` flags an unrecognized capitalized reference, the user
> provides the definition once and `memory-sync` writes it here. High-frequency
> terms (referenced ≥3 times in a session) are promoted to the AGENTS.md hot cache.

<!-- Terms below, alphabetical. Format: ## TERM, followed by definition prose. -->

## Architecture appetite

A bounded, advisory leanness **ceiling** shaper writes into a release plan's
`## JIG Handoff` (Spec 008-02, per ADR-0005). Exactly three ceiling-shaped
elements, and no positive-shape slot: (i) **investment posture** — a strict
*upper bound* on architectural investment, phrased "at most" / "permitted up to",
never "at least" (spectrum: *throwaway is enough → durability permitted, not
required*); (ii) **over-investment no-gos** — specific over-builds to refuse;
(iii) **spike pointer** — architectural risk worth retiring early. The
load-bearing invariant (ADR-0005): shaper expresses architecture *appetite*; JIG
makes architecture *decisions* (ADRs, module boundaries, mechanism, design). The
field must never name any of those. It is the *prospective* half of a
minimum-viable-architecture concern; the *retrospective* half is a JIG-side
leanness/YAGNI review lens, enforced at JIG review, not by shaper.

## Vertical scopes

The new work in a release plan's `## Solution Outline`, written as an ordered
list of thin, end-to-end scopes with the thinnest walking-skeleton path first
(Spec 008-01, per ADR-0005). Each scope must deliver demoable end-to-end value on
its own — a scope that is "just the data model" or "just the parser" is
horizontal and must be re-split (shaper's application of JIG's SPIDR
anti-horizontal-phasing rule, one altitude up). Lets multi-spec work reach JIG
already delivery-ordered instead of as a single "main user-facing path" lump.
