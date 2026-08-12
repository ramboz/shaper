---
status: Accepted
dependencies: []
last_verified: 2026-08-11
frame_review: true
---

# ADR-0005: Vertical-scope shaping and a bounded architecture-appetite handoff

## Status

Accepted (2026-08-11)

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
don't invest in a framework"; jig decides *what* to build within that ceiling.
No ADRs are minted by shaper. The guardrail — load-bearing, and the reason the
content model below is strict — is that the architecture-appetite field carries
**only** three ceiling-shaped elements and **never a proposed shape**:

- **(i) Investment posture** — a strict **upper bound** on how much
  architectural investment this release *warrants*, always phrased as "at most"
  / "permitted up to," never "at least." The spectrum is a ceiling that rises,
  and every value caps rather than mandates:
  *throwaway is enough* / *cap at the smallest shippable structure* / *no special
  leanness constraint — build it as the work needs* / *leanness not a constraint
  here — durability is **permitted** (a lasting investment may be warranted,
  e.g. because future releases will build here); do not force throwaway*. The
  top of the spectrum **removes** the ceiling; it never sets a floor — it permits
  durable investment without requiring any, and names no interface or seam
  (whether to build a lasting boundary, and what it is, stays jig's decision).
  This is a *graded* leanness ceiling — the same axis as a leanness no-go, dialled
  — not a wholly orthogonal magnitude (see the redundancy horn for exactly what
  it adds over a bare no-go); it is not a design.
- **(ii) Over-investment no-gos** — the specific over-builds to refuse
  ("no general conflict engine, no pluggable-backend abstraction, no second
  store"). A refusal, never a selection.
- **(iii) Spike pointer** — the architectural risk worth retiring early.

There is deliberately **no "leanest architecture is X" slot** — writing one is
the drift failure, because completing *"the leanest architecture is …"* forces a
positive mechanism and hands jig its own decision back pre-made. The Solution
Outline already carries the vertical **path**; naming the **design** that
realizes it is jig's, full stop.

**Why the bounded middle is non-empty (the load-bearing rebuttal).** The
strongest objection is that the middle collapses under three forces at once:
*vacuity* ("be lean" applies to every release → dead ceremony), *drift* (any
release-specific statement about architecture is really a design decision → jig
usurpation), and *redundancy* (whatever survives is already the existing
`No-Gos` / `Appetite` fields). The middle survives all three only under the
strict content model above:

1. **Not vacuous — the posture is release-specific.** "Throwaway, because this
   release is a bet offline editing is wanted at all" says something false of a
   release building a payments core; it is not boilerplate.
2. **Not drift — a ceiling is not a floor, including at the top of the posture
   spectrum.** Elements (ii)/(iii) forbid and flag; they never select. "Do not
   build a conflict engine here" leaves the *entire* in-appetite design space
   (queue, log, CRDT, timestamp-merge) to jig; it is categorically not a module
   boundary. Element (i) is held to the same test by construction: it is defined
   as an *upper bound only*, so its high end reads "durability is **permitted**,
   not required" — the absence of a leanness constraint, not a mandate to build a
   lasting interface. A high posture forces nothing (jig may still choose a thin
   design); it merely declines to *cap* investment. The failure mode the
   objection rightly flags — phrasing the high end as "build a durable seam,"
   which is a floor and names an interface — is exactly what the upper-bound-only
   definition forbids. The moment any element names the positive mechanism, or
   sets a *minimum*, it has drifted — which is why the content model bans the
   "leanest architecture is X" slot outright and pins the posture to "at most."
3. **Not redundant — but the claim is modest, not orthogonality.** The first
   draft overreached here ("a magnitude no `No-Go` can hold"), and that overclaim
   does not survive scrutiny: a low posture *is* largely expressible as a leanness
   no-go — "thin-and-deletable" recasts as the exclusion "will not build
   architecture that outlives this release." So the honest position concedes the
   reduction and claims something smaller and defensible. The posture is the same
   axis as a leanness no-go — *dialled* — and its value over a bare present/absent
   no-go is three concrete things, none of which a binary exclusion delivers:
   - **Gradation.** A no-go is present-or-absent; the posture *grades* how hard to
     hold leanness — "cap at the smallest shippable structure" is a stricter ceiling
     than "prefer thin," and a downstream jig spec reads the difference. A binary
     exclusion cannot say "how strict."
   - **Always-elicited.** The posture is a *required prompt* in `shape-release`, so
     leanness is decided every release. An over-investment no-go is written only if
     the maintainer happens to think of one; silence today is ambiguous between "we
     chose lean" and "nobody considered it."
   - **Considered permission vs. silence (the high end).** A high posture is
     *informational, not binding* — it converts the downstream leanness default's
     silence into an explicit "durability is permitted here; do not reflexively
     minimize." That is not a constraint and not a no-go's absence-by-accident; it
     is a deliberate signal that overrides jig's default-to-lean, which omission
     cannot carry.

   So (ii) over-investment no-gos + (iii) the spike *do* reuse the existing
   `## No-Gos` and `## Risks / Rabbit Holes` / `Risk-First` surfaces (A1 concedes
   the spike sub-part explicitly), and the low end of (i) is close to a graded
   no-go. What the field genuinely adds is **gradation + an always-on leanness
   prompt + a considered-permission signal at the high end** — a modest, real
   addition. It does *not* need to be an irreducible orthogonal quadrant to earn
   its place, and this ADR no longer claims it is one. The `## Appetite`
   (time/attention) analogy is deliberately dropped: time-appetite *binds*
   (fixed-time/variable-scope) and the posture at its high end does not, so the
   analogy licenses more than it should.

### Worked example (proof the middle is writable — no mechanism named)

A release "add offline editing to the notes app," time-appetite *6 weeks*:

> **Architecture appetite.**
> *Investment posture:* **thin-and-deletable** — this release is a bet that
> offline editing is wanted at all; it earns the smallest structure that ships
> and can be removed cleanly, not a durable sync platform.
> *Over-investment no-gos:* no general conflict-resolution engine, no
> pluggable sync-backend abstraction, no second persistence store — if the
> design grows one of these, scope has outrun appetite: stop and re-shape.
> *Spike:* whether offline writes can replay without data loss at all — retire
> before scope is committed.
> *(Which mechanism realizes offline editing — queue, append-only log, CRDT,
> timestamp merge — is jig's decision; this line names none by design.)*

This line is **release-specific** (useless pasted onto any other release),
**actionable to jig** (a downstream spec knows to keep the structure deletable,
refuse the three over-builds, and spike replay-safety first), and **strictly a
ceiling** (it names no module, interface, mechanism, or data structure — the
parenthetical even enumerates the choices it is *declining* to make for jig). At
this low end the posture is close to a graded leanness no-go, and the ADR
concedes that; its earn-its-place value here is *gradation* ("smallest shippable"
is a stricter dial than "prefer thin") and being *always elicited*, not
orthogonality. It is the frame's answer to "show me one" — and, unlike the first
draft, it buys its actionability from the *posture*, not from naming a design.

The harder case is a **high** posture — the top of the spectrum, where
ceiling and floor are easiest to confuse. A release "add a public plugin API,"
time-appetite *one quarter*:

> **Architecture appetite.**
> *Investment posture:* **leanness is not a constraint here** — this API is a
> foundation later releases will build on, so a durable investment is *permitted*
> (do not force a throwaway shim to save days). This grants headroom; it does
> not require a "platform," name an interface, or oblige any particular
> durability — jig decides whether and how to make it lasting.
> *Over-investment no-gos:* still no plugin marketplace, no remote-plugin
> sandboxing, no multi-language host this release.
> *Spike:* whether the host's existing extension points can carry a public
> contract, or a new boundary is unavoidable — jig's call, flagged early.

Even at the top of the spectrum the posture only *lifts the ceiling*: it says
"durability is allowed," never "build a seam." A jig spec is free to satisfy it
with the thinnest public surface that could work — so the high end is
**informational, not binding**. Its non-vacuity is exactly that: it converts the
downstream leanness default's silence into a deliberate "durability is permitted
here; don't reflexively minimize" — a considered signal omission cannot carry,
not a constraint. That is the round-3 collapse point ("durable seam because N
releases build on it") rewritten as a permission, not a mandate: no floor, no
interface named, jig's decision intact. The frame no longer claims the high end
*binds*; it claims only that a considered permission beats silence.

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

- **A1 (verified, narrowed).** shaper's current shaping carries no
  vertical-scope decomposition and no *leanness-ceiling* architecture stance.
  Verified by reading
  [`skills/shape-release/SKILL.md`](../../skills/shape-release/SKILL.md) (the
  "Inputs to gather" list: `solution outline` = "the smallest useful release
  shape"; `JIG handoff` = specs/slices to link or new specs to draft) and
  [`templates/release-plan.md`](../../templates/release-plan.md) (Solution
  Outline = Proposed shape / Main user-facing path / Important non-goals;
  JIG Handoff = candidate specs / new work / patch-ready instructions /
  non-mutating notes). The "Main user-facing path" line is the only
  vertical-first seed and it is a single lump, not an ordered scope set.
  **Scoping caveat:** shaper does carry a *limited* architecture stance already —
  product-vision principle 7 ("research spikes and architecture decisions should
  happen early when they unblock the release path") plus the existing
  `Risks / Rabbit Holes` and cutline `Risk-First` surfaces already home the
  "architectural risk worth an early spike" pointer in Option C.2. That
  sub-part is therefore a *formalization* of existing capability, not a new one;
  the genuinely new stance this ADR adds is the **leanness ceiling** (the
  over-investment no-go), and the vertical-scope ordering. A1 is scoped to those
  two to avoid overclaiming.
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
  into the existing `Appetite` / `No-Gos` sections? (Spec 008 slice 02 decides;
  a distinct field is more visible but adds surface.) Note the axis distinction
  the Recommended Decision draws: the investment-ceiling dial is a different axis
  than the time/attention `Appetite`, so even a folded rendering must keep the
  two legibly separate — folding is a layout choice, not a merge of the two
  signals. (This axis point is separate from, and unaffected by, horn 3's
  retraction of the stronger *orthogonal-to-a-leanness-no-go* claim.)
- Should `cutline` (which already reasons about Split / Risk-First against
  existing specs) also emit vertical-scope-ordering advice for new work, or does
  that stay solely in `shape-release`? Deferred to spec 008's slicing.
