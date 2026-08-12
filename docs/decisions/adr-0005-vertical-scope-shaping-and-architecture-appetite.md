---
status: Proposed
dependencies: []
last_verified:
frame_review: true
---

# ADR-0005: Vertical-scope shaping and a bounded architecture-appetite handoff

## Status

Proposed (2026-08-11)

## Context

shaper's charter is to shape raw product intent into a bounded release plan
"before and above JIG specs," then hand implementation-ready work to jig
([product-vision.md](../product-vision.md) Identity / Positioning). jig owns
supervised spec-driven development — SPIDR slicing, ADRs, architecture — and
shaper's competitive-landscape row for jig is explicit: *"shaper must not
replace or duplicate it."* One of shaper's out-of-scope lines is *"No
implementation workflow; JIG owns that."*

A maintainer audit of the jig side surfaced a real gap: **SPIDR's vertical-slice
discipline lives entirely at the spec→slice altitude and never propagates
upward.** jig has no guidance toward a minimal viable architecture (nothing that
discourages over-engineering prospectively — the leanness value is re-derived
ADR by ADR), and nothing that shapes *major features / multi-spec work* in a
vertical-first form. The jig-side answer to the retrospective half (a
leanness/YAGNI review lens at arch-review + reconciliation) is being built in
jig. This ADR is about the **prospective** half — the shaping altitude, which
is shaper's.

The question is whether shaper is the right owner, and if so, how far it may go
without crossing into jig's architecture ownership. Two grounded observations
frame it (see `## Assumptions`):

1. shaper's `shape-release` skill and `release-plan.md` template today shape
   **appetite and boundaries** — a "smallest useful release shape," no-gos, and
   a cutline (`Include`/`Defer`/`Split`/`Risk-First`). But the solution outline's
   only forward-delivery field is a single-line **"Main user-facing path"**
   ([templates/release-plan.md:26](../../templates/release-plan.md)); new work is
   never decomposed into an *ordered set of vertical scopes* (thinnest
   end-to-end first, then thicken). The cutline decomposes only against
   *existing* jig specs, not the new work being shaped.
2. The template's `## JIG Handoff` block is **scope-only** — candidate specs,
   new work to draft, patch-ready instructions
   ([templates/release-plan.md:65-70](../../templates/release-plan.md)). It
   carries no architectural stance, so nothing at the cheapest-to-prevent
   altitude (before any spec exists) discourages over-engineering. When the work
   lands in jig, SPIDR slices it — but "keep the architecture minimal" was never
   said upstream.

The tension: closing (2) means shaper says *something* about architecture,
which brushes against "JIG owns that." The forces pull both ways — say nothing
and the gap stays unowned; say too much and shaper duplicates jig's ADR /
architecture role and violates its own non-duplication principle.

## Decision Options Considered

### Option A: Stop at scope and appetite (status quo)
shaper keeps shaping boundaries only; architecture leanness stays entirely a
jig review-time concern (the jig-side leanness lens).
- **Pros:** Cleanest boundary; zero duplication of jig; shaper stays lightweight.
- **Cons:** Leaves the prospective MVA gap **unowned**. jig's lens is
  retrospective — it catches over-engineering at review, after the architecture
  already exists and cost has been paid. Nobody shapes vertical *delivery order*
  for new multi-spec work, which is squarely shaper's altitude.

### Option B: shaper owns the release's architecture decisions
`shape-release` elicits and records the architectural approach; shaper mints its
own architecture notes / ADR-like artifacts.
- **Pros:** Closes the gap decisively and in one place.
- **Cons:** Directly usurps jig's ADR + `architecture.md` ownership; violates
  shaper's "must not replace or duplicate jig" and "JIG owns implementation"
  lines; pushes shaper toward the heavyweight framework its vision rejects.

### Option C (recommended): Bounded extension — vertical scopes + architecture *appetite*
shaper adds two things and no more:
1. **Vertical-scope decomposition** in the solution outline — order the new work
   as a small set of vertical scopes, thinnest end-to-end path first, each
   delivering demoable value (the walking-skeleton shape SPIDR uses one level
   down). This is shaper's native cutline logic applied to *new* work, not just
   to existing specs.
2. An **architecture-appetite** line in the handoff — a bounded, advisory
   *ceiling* on architectural investment ("what's the leanest architecture that
   satisfies this release; what would be over-engineering here"), expressed as
   an appetite / no-go, and a pointer to any architectural risk that should be
   retired early (a spike). It records **no ADRs, mandates no design, and names
   no module boundaries.**
- **Pros:** Owns the prospective half at the correct altitude; discourages
  over-engineering at the cheapest point; gives multi-spec work a delivery
  order — all using verbs shaper already has (appetite, cutline, risk
  retirement). The jig-side leanness lens becomes the retrospective complement.
- **Cons:** Adds a step to shaping (more to elicit); the architecture-appetite
  line must be actively guarded against drifting into prescriptive design.

## Recommended Decision

**Option C.** The boundary that keeps this clean is a verb split shaper already
lives by for scope:

- **shaper expresses architectural _appetite_** — a leanness ceiling, advisory,
  fixed-appetite/variable-scope applied to architecture (how much design is *too
  much* for this release), plus the vertical delivery order and any risk worth a
  spike.
- **jig makes architectural _decisions_** — the ADRs, module boundaries, and the
  actual design that satisfies that appetite.

Appetite is shaper's native verb; decisions are jig's — exactly the split shaper
already uses for scope (shaper sets the appetite, jig's specs decide the
details). shaper's handoff says "the appetite for architecture here is small —
a thin path, don't build a framework"; jig decides *what* thin thing to build.
No ADRs are minted by shaper; the guardrail is that the architecture-appetite
field carries appetite / no-gos / risk pointers only, never a design.

## Consequences

**Becomes easier:**
- The vertical-first propagation gap gets an owner at the altitude where it
  belongs (before specs exist).
- Over-engineering is discouraged prospectively — the cheapest point — instead
  of only caught at jig review time.
- New multi-spec work arrives at jig already ordered thinnest-path-first, so
  SPIDR at the slice level inherits a coherent spine instead of re-deriving one.

**Becomes harder:**
- `shape-release` has one more thing to elicit; the template grows two fields.
- The architecture-appetite field is a drift risk: it must stay appetite-shaped.
  The guardrail (appetite / no-gos / risk pointers only — never ADRs, decisions,
  or module boundaries) is load-bearing and belongs in the skill's Boundaries.
- Full coverage of the maintainer's concern needs the matching **jig-side
  leanness/YAGNI review lens** (the retrospective complement). The two are the
  prospective and retrospective halves of one value; this ADR owns only the
  prospective half. They should cross-reference.

## Assumptions

<!-- Spec 064-02 / ADR-0020 §1–§2 — grounding-by-probe (risk-gated). -->

- **A1 (verified).** shaper's current shaping carries no vertical-scope
  decomposition and no architecture stance. Verified by reading
  [`skills/shape-release/SKILL.md`](../../skills/shape-release/SKILL.md) (the
  "Inputs to gather" list: `solution outline` = "the smallest useful release
  shape"; `JIG handoff` = specs/slices to link or new specs to draft) and
  [`templates/release-plan.md`](../../templates/release-plan.md) (Solution
  Outline = Proposed shape / Main user-facing path / Important non-goals;
  JIG Handoff = candidate specs / new work / patch-ready instructions /
  non-mutating notes). The "Main user-facing path" line is the only
  vertical-first seed and it is a single lump, not an ordered scope set.
- **A2 (verified).** jig owns architecture decisions via ADRs and
  `docs/architecture.md`; shaper's own competitive-landscape row commits to not
  duplicating that (product-vision.md). This is why Option C forbids shaper from
  minting ADRs or naming module boundaries.

## Kill criteria

- If in practice the architecture-appetite line is **always ignored** (dead
  ceremony that no downstream jig spec ever reads), or **always drifts** into
  prescribing design (usurping jig), the bounded middle has failed — revert to
  Option A and let the jig-side leanness lens carry the whole concern alone.

## Open questions

- Does the architecture-appetite belong as a distinct template field, or folded
  into the existing `Appetite` / `No-Gos` sections? (Spec 008 slice 01 decides;
  a distinct field is more visible but adds surface.)
- Should `cutline` (which already reasons about Split / Risk-First against
  existing specs) also emit vertical-scope-ordering advice for new work, or does
  that stay solely in `shape-release`? Deferred to spec 008's slicing.
