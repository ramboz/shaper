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

Current product/plugin layout after
[Spec 003: Hybrid plugin baseline](specs/003-hybrid-plugin-baseline/spec.md)
and the first release-plan handoff slice:

```text
shaper/
├── AGENTS.md                    # project hot cache and session workflow
├── .claude-plugin/              # Claude source manifest + marketplace pointer
├── .codex-plugin/               # Codex source manifest
├── docs/
│   ├── product-vision.md        # what shaper is and is not
│   ├── architecture.md          # technical framing and boundaries
│   ├── releases/                # release plans and compact release slate
│   ├── specs/                   # JIG implementation specs and status board
│   └── decisions/               # ADRs only where a hard-to-reverse decision is needed
├── hosts/
│   ├── claude/                  # committed Claude Code plugin package
│   └── codex/                   # committed Codex marketplace package
├── skills/                      # product skill instructions
├── templates/                   # release-plan template
├── scripts/                     # package builders, drift guards, manifest checks
├── tests/                       # unittest coverage for package contracts
├── dist/                        # generated release zips; ignored by git
├── .github/                     # CI, PR-title, and release-please workflows
└── .codex/                      # project-local jig runtime from scaffold-init
```

The `.codex/` directory is the project-local JIG scaffold runtime, not
shaper's canonical plugin source. The `hosts/<host>/` packages are generated
from root source and committed, following JIG `v2` ADR-0018. For now they carry
valid plugin metadata, README content, the first product skills, and the
release-plan template. Later specs add `release-slate`, `scope-audit`, and
`release-check` automation.

The `docs/releases/` shape follows ADR-0003. Each `docs/releases/<slug>.md`
file is a release plan. `docs/releases/README.md` is a compact release slate,
not a backlog or second status board.

## Tech stack

<!-- elicited: 2026-06-17 / status: filled -->

- **Runtime / language:** Python 3 standard-library tooling for repository
  helpers, consistent with `/Users/ramboz/Projects/misc/jig` and
  `/Users/ramboz/Projects/misc/servo`.
- **Platform commitments:** cross-host from the start: support both Claude Code
  and Codex plugin surfaces where practical. The accepted baseline is JIG
  `v2`'s committed host-package model: root source, `hosts/claude`,
  `hosts/codex`, and drift guard.
- **CI/CD and releases:** accepted via ADR-0002 and implemented progressively
  in Spec 004. The first gate adds conventional commit PR-title validation,
  pull-request / `main` CI, manifest validation, host-package drift checks, and
  a spec status-board drift check. The release-please slice adds version,
  changelog, tag, and GitHub-release ownership. A later slice adds
  host-explicit release zips.
- **Package manager:** deferred until implementation needs packaging.
- **Database / state:** no database; repo-native Markdown first.
- **Key external services:** JIG docs/specs/status board, optional servo quality
  signals after a future read-boundary ADR.
- **Locked-in decisions:** repo-native Markdown first; soft coupling to JIG and
  servo; no web UI; hybrid plugin baseline; host-explicit release archives;
  release-plan/no-backlog-slate artifact model.
- **Still open:** host-explicit release archive builders and the later JIG/servo
  read boundary for `release-check`.
- **Testing/static checks:** the first builder tests use standard-library
  `unittest` through `.jig/test-command`; the first code-health check compiles
  owned Python through `.jig/lint-command`. Both avoid a package-manager
  decision until the project needs one.

## Core architecture decisions

> _One H3 subsection per decision. Each decision should reference its ADR
> (when one exists) and split into Principle (from
> [product-vision.md](product-vision.md) where applicable) + Mechanics
> (technical detail). This section is the running summary; decisions
> themselves live in `docs/decisions/`._

### Hybrid plugin baseline

- **Principle:** shaper should be cross-host from the start and should not
  confuse project-local JIG scaffold runtime with shaper's own plugin source.
- **Mechanics:** ADR-0001 adopts JIG `v2`'s committed host-package baseline:
  root canonical source, `.claude-plugin` and `.codex-plugin` source manifests,
  generated `hosts/claude` and `hosts/codex` packages committed to git, and a
  drift guard. shaper uses a smaller builder than JIG because product skills
  and host prose rewriting are deferred.

### Release automation and host-explicit archives

- **Principle:** releases should be boring, sibling-aligned, and explicit about
  host install semantics.
- **Mechanics:** ADR-0002 adopts the JIG/servo release baseline: conventional
  commit PR-title gate, CI, release-please-managed versions and GitHub releases,
  and smoke-tested release archives named `shaper-claude-vX.Y.Z.zip` and
  `shaper-codex-vX.Y.Z.zip`.

### Release plan and no-backlog slate

- **Principle:** shaper should use release terminology for public artifacts
  while preserving Shape Up-inspired mechanics internally.
- **Mechanics:** ADR-0003 defines `docs/releases/<slug>.md` and
  `docs/releases/README.md` as the public Markdown artifact contracts.

## Module boundaries

<!-- elicited: 2026-06-17 / status: filled -->

- **Release shaping:** elicits problem/baseline, appetite, solution outline,
  risks/rabbit holes, no-gos, release criteria, and JIG handoff; writes release
  plan Markdown.
- **Cutline analysis:** reads existing JIG specs/status board and proposes
  include/defer/split/risk-first recommendations without mutating them.
- **Release slate:** maintains a compact current slate of release plans without
  becoming a backlog or duplicate JIG status board.
- **Scope audit:** detects appetite leakage, unresolved risks/rabbit holes,
  orphan specs, and JIG work exceeding the cutline.
- **Release check:** later skill that judges whether a release plan is
  shippable using JIG status and optional servo quality signals.
- **Host adapters:** keep Claude Code and Codex plugin surfaces aligned where
  practical.
- **Release automation:** operational layer that validates changes, delegates
  versioning/changelog/tag/GitHub-release ownership to release-please, and later
  builds host-explicit archives from committed host packages.

JIG remains the source of truth for spec lifecycle state. shaper can recommend
transitions and generate patch-ready instructions, but it must not silently
mutate JIG spec states.

## Data model

<!-- elicited: 2026-06-17 / status: filled -->

- **`docs/releases/*.md`** - release plans: status, problem/baseline, appetite,
  solution outline, risks/rabbit holes, no-gos, cutline, JIG handoff, and
  release-check criteria.
- **`docs/releases/README.md`** - compact release slate: active candidate,
  committed, shipping, shipped, and currently relevant dropped release plans.
- **`docs/specs/README.md`** - JIG status board read by cutline, scope-audit,
  release-slate, and release-check flows; shaper must not create a second
  status board.
- **`docs/specs/*`** - JIG specs and slices read as source material for
  recommendations.
- **`docs/product-vision.md` / `docs/architecture.md`** - project-level framing
  that constrains shaper's own future specs.
- **`docs/decisions/*`** - ADRs only where a hard-to-reverse decision is needed.
- **Optional servo quality signals** - consumed by future release-check work if
  present; shaper does not define or run servo oracles.

## Contract surfaces

<!-- elicited: 2026-06-17 / status: filled -->

- **Markdown artifact shapes** (templates under `templates/` and examples under
  `docs/releases/`) - release plans and the compact release slate are shaper's
  primary caller-facing contracts.
- **Skill invocation behavior** (`skills/<name>/SKILL.md`) - skills define how
  agents elicit, read, and update repo-native Markdown.
- **JIG read surfaces** (JIG's existing `docs/specs/README.md` and
  `docs/specs/*`) - cutline and scope-audit read JIG specs/status without
  mutating lifecycle state.
- **Servo signal surface** (no accepted artifact yet) - future release-check may
  consume servo quality signals after a read-boundary ADR.
- **Release archive contract** (Spec 004 builders and smoke tests) - Claude
  archives are flat plugin packages; Codex archives are marketplace bundles
  with extract-then-add install semantics.
- **Change-quality gate** (`.github/workflows/ci.yml`,
  `.github/workflows/pr-title.yml`, `scripts/validate_manifests.py`) - pull
  requests and `main` run the unit suite, Python syntax check, manifest
  validation, host-package drift guard, and status-board drift check; PR titles
  must be scoped conventional commits.
- **Release-please gate** (`.github/workflows/release.yml`,
  `.github/release-please-config.json`,
  `.github/.release-please-manifest.json`, `CHANGELOG.md`) - pushes to `main`
  let release-please open or update a release PR that bumps all versioned plugin
  manifests, updates the changelog and manifest, and creates the tag/GitHub
  release when merged. Archive upload is intentionally deferred to the
  host-explicit zip slice.
- **Plugin install contract** (`.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`,
  `hosts/claude/`, `hosts/codex/`) - root manifests are canonical source,
  host packages are committed generated payloads, and
  `scripts/build_host_packages.py --check` guards host-package drift. Cross-host
  version parity is owned by the source manifests plus the drift guard; Spec 004
  owns future release-bump automation.

No HTTP API, event bus, RPC, GraphQL surface, or web UI is planned for the
initial product.

## Open questions

> Deferred items live in [refinement-todo.md](refinement-todo.md).
