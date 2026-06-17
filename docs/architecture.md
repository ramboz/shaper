> Status: Draft (elicited)
>
> Technical mechanics. Vision and design principles live in
> [product-vision.md](product-vision.md). Update via reconciliation after each
> spec slice completes.

# Architecture: shaper

> For *what this project is*, *who it's for*, and *why*, see
> [product-vision.md](product-vision.md). This document covers the technical
> mechanics: repository structure, tech stack, decisions, modules, data.

## Repository structure

<!-- elicited: 2026-06-17 / status: filled -->

Expected initial layout:

```
shaper/
├── AGENTS.md                    # project hot cache and session workflow
├── docs/
│   ├── product-vision.md        # what shaper is and is not
│   ├── architecture.md          # technical framing and boundaries
│   ├── bets/                    # shaped release bets and roadmap overlays
│   ├── specs/                   # JIG implementation specs and status board
│   └── decisions/               # ADRs only where a hard-to-reverse decision is needed
├── skills/
│   ├── shape-bet/               # create or refine a shaped release bet from product intent
│   ├── cutline/                 # audit JIG specs/slices against release appetite
│   ├── roadmap/                 # maintain non-duplicating roadmap overlays
│   ├── release-readiness/       # judge shippability from JIG and optional servo signals
│   └── scope-audit/             # detect MVP/v1/v2 leakage and orphan specs
├── templates/                   # Markdown templates for shaped bets and overlays
└── .codex/                      # project-local jig runtime from scaffold-init
```

The `docs/bets/` shape is recommended for the MVP because it keeps shaped bets close to JIG specs without turning them into a second status board.

## Tech stack

<!-- elicited: 2026-06-17 / status: filled -->

- **Runtime / language:** Probably python (python3) as we want this consistent with `/Users/ramboz/Projects/misc/jig` and `/Users/ramboz/Projects/misc/servo`.
- **Platform commitments:** cross-host from the start: support both Claude Code and Codex plugin surfaces where practical.
- **Package manager:** deferred until implementation needs packaging.
- **Database / state:** no database; repo-native Markdown first.
- **Key external services:** JIG docs/specs/status board, optional servo quality signals.
- **Locked-in decisions:** repo-native Markdown first; soft coupling to JIG and servo; no web UI in the initial product.
- **Still open:** exact plugin packaging, test framework, CI/CD setup, and whether shaped bets are one file per release or an index plus per-bet files.

## Core architecture decisions

> _One H3 subsection per decision. Each decision should reference its ADR
> (when one exists) and split into Principle (from
> [product-vision.md](product-vision.md) where applicable) + Mechanics
> (technical detail). This section is the running summary; decisions
> themselves live in `docs/decisions/`._

_(No ADR-backed decisions recorded yet. The current choices are reversible enough to live in vision, architecture, and the first spec.)_

## Module boundaries

<!-- elicited: 2026-06-17 / status: filled -->

- **Bet shaping:** elicits outcome, appetite, must-haves, no-goes, risks, and release criteria; writes shaped-bet Markdown.
- **Cutline analysis:** reads existing JIG specs/status board and proposes MVP/v1/v2 include/defer groupings without mutating them.
- **Roadmap overlay:** points to JIG specs rather than restating their lifecycle status.
- **Release readiness:** later skill that judges whether a release bet is shippable using JIG status and optional servo quality signals.
- **Scope audit:** later skill that detects MVP/v1/v2 leakage, orphan specs, and acceptance criteria that exceed the current appetite.
- **Host adapters:** keep Claude Code and Codex plugin surfaces aligned where practical.

JIG remains the source of truth for spec lifecycle state. shaper can recommend transitions and generate patch-ready instructions, but it must not silently mutate JIG spec states.

## Data model

<!-- elicited: 2026-06-17 / status: filled -->

- **`docs/bets/*.md`** - shaped release bets: appetite, outcome, must-haves, no-goes, risks, release criteria, and cutline recommendations.
- **`docs/specs/README.md`** - JIG status board read by cutline and roadmap flows; shaper must not create a second status board.
- **`docs/specs/*`** - JIG specs and slices read as source material for include/defer recommendations.
- **`docs/product-vision.md` / `docs/architecture.md`** - project-level framing that constrains shaper's own future specs.
- **`docs/decisions/*`** - ADRs only where a hard-to-reverse decision is needed.
- **Optional servo quality signals** - consumed by future release-readiness work if present; shaper does not define or run servo oracles.

## Contract surfaces

<!-- elicited: 2026-06-17 / status: filled -->

- **Markdown artifact shapes** (recommended artifact: templates under `templates/` and examples under `docs/bets/`) - shaped bets and roadmap overlays are shaper's primary caller-facing contract.
- **Skill invocation behavior** (recommended artifact: each `skills/<name>/SKILL.md`) - skills define how agents elicit, read, and update repo-native Markdown.
- **JIG read surfaces** (recommended artifact: JIG's existing `docs/specs/README.md` and `docs/specs/*`) - cutline reads JIG specs/status without mutating lifecycle state.
- **Servo signal surface** (recommended artifact: no artifact yet) - future release-readiness may consume servo quality signals if present.

No HTTP API, event bus, RPC, GraphQL surface, or web UI is planned for the initial product.

## Open questions

> Deferred items live in [refinement-todo.md](refinement-todo.md).
