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

Expected product/plugin layout after
[Spec 003: Hybrid plugin baseline](specs/003-hybrid-plugin-baseline/spec.md):

```
shaper/
├── AGENTS.md                    # project hot cache and session workflow
├── .claude-plugin/              # Claude source manifest + marketplace pointer
├── .codex-plugin/               # Codex source manifest
├── docs/
│   ├── product-vision.md        # what shaper is and is not
│   ├── architecture.md          # technical framing and boundaries
│   ├── bets/                    # shaped release bets and roadmap overlays
│   ├── specs/                   # JIG implementation specs and status board
│   └── decisions/               # ADRs only where a hard-to-reverse decision is needed
├── hosts/
│   ├── claude/                  # committed Claude Code plugin package
│   └── codex/                   # committed Codex marketplace package
├── skills/
│   ├── shape-bet/               # create or refine a shaped release bet from product intent
│   ├── cutline/                 # audit JIG specs/slices against release appetite
│   ├── roadmap/                 # maintain non-duplicating roadmap overlays
│   ├── release-readiness/       # judge shippability from JIG and optional servo signals
│   └── scope-audit/             # detect MVP/v1/v2 leakage and orphan specs
├── templates/                   # Markdown templates for shaped bets and overlays
├── scripts/                     # package builders and drift guards
├── dist/                        # generated release zips; ignored by git
├── .github/                     # CI and release workflows after Spec 004
└── .codex/                      # project-local jig runtime from scaffold-init
```

The `.codex/` directory is the project-local JIG scaffold runtime, not
shaper's canonical plugin source. The `hosts/<host>/` packages are generated
from root source and committed, following JIG `v2` ADR-0018.

The `docs/bets/` shape is recommended for the MVP because it keeps shaped bets close to JIG specs without turning them into a second status board.

## Tech stack

<!-- elicited: 2026-06-17 / status: filled -->

- **Runtime / language:** Probably python (python3) as we want this consistent with `/Users/ramboz/Projects/misc/jig` and `/Users/ramboz/Projects/misc/servo`.
- **Platform commitments:** cross-host from the start: support both Claude Code and Codex plugin surfaces where practical. The proposed baseline is JIG `v2`'s committed host-package model: root source, `hosts/claude`, `hosts/codex`, and drift guard.
- **CI/CD and releases:** proposed via ADR-0002 and Spec 004: conventional commit PR-title gate, CI, release-please, and host-explicit release zips.
- **Package manager:** deferred until implementation needs packaging.
- **Database / state:** no database; repo-native Markdown first.
- **Key external services:** JIG docs/specs/status board, optional servo quality signals.
- **Locked-in decisions:** repo-native Markdown first; soft coupling to JIG and servo; no web UI in the initial product.
- **Still open:** exact shaper-specific builder scope, test framework, first CI check set, and whether shaped bets are one file per release or an index plus per-bet files.

## Core architecture decisions

> _One H3 subsection per decision. Each decision should reference its ADR
> (when one exists) and split into Principle (from
> [product-vision.md](product-vision.md) where applicable) + Mechanics
> (technical detail). This section is the running summary; decisions
> themselves live in `docs/decisions/`._

### Hybrid plugin baseline

- **Principle:** shaper should be cross-host from the start and should not
  confuse project-local JIG scaffold runtime with shaper's own plugin source.
- **Mechanics:** ADR-0001 proposes adopting JIG `v2`'s committed
  host-package baseline: root canonical source, `.claude-plugin` and
  `.codex-plugin` source manifests, generated `hosts/claude` and `hosts/codex`
  packages committed to git, and a drift guard.

### Release automation and host-explicit archives

- **Principle:** releases should be boring, sibling-aligned, and explicit
  about host install semantics.
- **Mechanics:** ADR-0002 proposes adopting the JIG/servo release baseline:
  conventional commit PR-title gate, CI, release-please-managed versions and
  GitHub releases, and smoke-tested release archives named
  `shaper-claude-vX.Y.Z.zip` and `shaper-codex-vX.Y.Z.zip`.

## Module boundaries

<!-- elicited: 2026-06-17 / status: filled -->

- **Bet shaping:** elicits outcome, appetite, must-haves, no-goes, risks, and release criteria; writes shaped-bet Markdown.
- **Cutline analysis:** reads existing JIG specs/status board and proposes MVP/v1/v2 include/defer groupings without mutating them.
- **Roadmap overlay:** points to JIG specs rather than restating their lifecycle status.
- **Release readiness:** later skill that judges whether a release bet is shippable using JIG status and optional servo quality signals.
- **Scope audit:** later skill that detects MVP/v1/v2 leakage, orphan specs, and acceptance criteria that exceed the current appetite.
- **Host adapters:** keep Claude Code and Codex plugin surfaces aligned where practical.
- **Release automation:** later operational layer that validates changes,
  delegates versioning/releases to release-please, and builds host-explicit
  archives from committed host packages.

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
- **Release archive contract** (recommended artifact: Spec 004 builders and
  smoke tests) - Claude archives are flat plugin packages; Codex archives are
  marketplace bundles with extract-then-add install semantics.

No HTTP API, event bus, RPC, GraphQL surface, or web UI is planned for the initial product.

## Open questions

> Deferred items live in [refinement-todo.md](refinement-todo.md).
