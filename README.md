# shaper

> A Codex and Claude Code plugin for shaping release-sized work before
> implementation starts.

**shaper** turns rough product intent into a small, buildable release plan:
what problem matters, how much time it is worth, what is deliberately out, what
risks need answers first, and what evidence says the release is ready.

## Why shaper

AI-assisted projects can generate specs quickly, but speed creates a familiar
failure mode: scope spreads across too many plausible slices, risks stay vague
until implementation is already moving, and nobody can say what belongs in the
current release versus what should wait.

shaper sits above the spec-driven development (SDD) flow. It helps shape a
bounded release plan before that work is handed to specs, slices, or whatever
implementation workflow the project uses. It is inspired by
[Shape Up](https://basecamp.com/shapeup), but its public language stays
ordinary: release plans, release slates, release checks, and scope audits.

## Core terms

The project uses a few Shape Up-inspired terms, each with a small meaning:

- **Appetite** - the amount of time or attention this release is worth.
- **Cutline** - the boundary between what belongs in this release and what can
  wait.
- **No-gos** - explicit things this release will not do.
- **Risk retirement** - answering the scary unknowns before implementation
  starts.
- **Release slate** - the compact list of release plans that matter right now.
- **Release check** - an advisory ship/cut-scope/stop/re-shape decision.

## What it does

shaper is designed around repo-native Markdown artifacts and small agent skills:

- **Release plans** - `docs/releases/<slug>.md` captures the problem,
  appetite, solution outline, risks, no-gos, cutline, SDD handoff, and release
  criteria.
- **`shape-release`** - elicits raw intent into a bounded release plan.
- **`cutline`** - reads existing specs and status boards, then recommends
  include/defer/split/risk-first moves without mutating lifecycle state.
- **Release slate** - `docs/releases/README.md` stays compact and current
  without becoming a backlog or second status board.
- **Planned `scope-audit`** - will check whether active work is leaking past
  the appetite or cutline.
- **Planned `release-check`** - will give advisory
  ship/cut-scope/stop/re-shape guidance from implementation status and, later,
  optional quality signals.

## Relationship to jig and servo

shaper is a sibling plugin, not a replacement for either project.

- **[jig](https://github.com/ramboz/jig)** owns implementation workflow and
  spec lifecycle: specs, vertical slices, lifecycle state, review evidence,
  reconciliation, and landing.
- **[servo](https://github.com/ramboz/servo)** owns eval/oracle loops:
  oracles, quality gates, hooks, variant races, and scheduled discovery.
- **shaper** owns release shaping before implementation starts: release
  boundaries, no-gos, risk retirement, cutlines, and release readiness checks.

The coupling is intentionally soft. shaper should hand off to SDD generally,
read jig docs when jig is present, and later consume servo signals when they
exist. It should degrade gracefully when those artifacts are absent.

## Artifact model

Accepted ADR-0003 defines the public artifact shape:

| Artifact | Purpose |
|---|---|
| `docs/releases/<slug>.md` | A release plan: candidate, committed, shipping, shipped, or dropped. |
| `docs/releases/README.md` | A compact release slate for the small set of currently relevant plans. |
| `docs/specs/README.md` | When using jig, its status board remains the source of truth for implementation status. |

The release slate is deliberately not a roadmap, sprint planner, backlog, or
duplicate implementation board.

## Current status

shaper is currently moving from scaffolded baseline into the first product
loop. The project has accepted the major architecture decisions, has a minimal
hybrid plugin baseline, and now includes the first release-plan handoff assets:
`shape-release`, `cutline`, `templates/release-plan.md`, and a compact
`docs/releases/README.md` slate.

| Surface | Role | Status |
|---|---|---|
| Hybrid plugin baseline | Codex and Claude Code host package layout | Root manifests, committed host packages, and drift guard in Spec 003 |
| Release automation | CI, release-please, host-explicit zips | ADR-0002 accepted, Spec 004 draft |
| Release plan and slate artifacts | `docs/releases/<slug>.md` and compact slate | ADR-0003 accepted; first template and slate added by Spec 002 |
| `shape-release` and `cutline` | First release-plan-to-SDD handoff loop | Implemented by Spec 002 |
| `scope-audit` | Scope check against appetite and cutline | Spec 006 draft |
| `release-check` | Advisory release readiness check | Spec 007 draft |

For live per-slice state, see the
[spec status board](docs/specs/README.md).

## Distribution plan

ADR-0001 and ADR-0002 align shaper with the sibling plugin release model:

- canonical source at the repository root;
- committed host packages under `hosts/claude/` and `hosts/codex/`;
- a drift guard so host packages stay generated from source;
- release-please-managed versions and GitHub releases;
- host-explicit release archives:
  - `shaper-claude-vX.Y.Z.zip`
  - `shaper-codex-vX.Y.Z.zip`

The install surfaces package metadata, README content, the first product
skills, and the release-plan template. Release archives remain owned by
Spec 004.

Current host install semantics:

- Claude Code remote install reads the root `.claude-plugin/marketplace.json`,
  which resolves the plugin with `source: git-subdir` and `path:
  hosts/claude`; the committed `hosts/claude` package is the install payload,
  not the repository root.
- Codex install uses `hosts/codex` as a marketplace root. Its descriptor at
  `hosts/codex/.agents/plugins/marketplace.json` points at
  `./plugins/shaper` and includes `policy.installation`,
  `policy.authentication`, and `category`.

Regenerate committed host packages after changing plugin source:

```bash
python3 scripts/build_host_packages.py
```

Check for package drift without mutating `hosts/`:

```bash
python3 scripts/build_host_packages.py --check
```

## Still deferred

The first product loop is intentionally narrow. release-slate automation,
scope-audit automation, release-check automation, servo signal consumption, web
UI, task boards, sprint planning, estimation, backlog grooming, and
issue-system replacement remain out of scope for this handoff slice.

## Start here

If you are reading shaper as a user or contributor:

1. Read the [product vision](docs/product-vision.md) for the project boundary.
2. Read the [architecture](docs/architecture.md) for the planned plugin shape.
3. Check the [spec status board](docs/specs/README.md) for current work.
4. Follow the [workflow](docs/workflow.md) before implementing any non-trivial
   change.

## Repository structure

The current product layout:

```text
shaper/
|-- .claude-plugin/              # Claude source manifest + marketplace pointer
|-- .codex-plugin/               # Codex source manifest
|-- docs/
|   |-- releases/                # Release plans and compact release slate
|   |-- specs/                   # Spec-driven implementation docs and board
|   `-- decisions/               # ADRs for hard-to-reverse decisions
|-- hosts/
|   |-- claude/                  # Committed Claude Code plugin package
|   `-- codex/                   # Committed Codex marketplace package
|-- skills/
|   |-- shape-release/
|   `-- cutline/
|-- templates/                   # Release-plan template
|-- scripts/                     # Builders, drift guards, release checks
`-- dist/                        # Generated release zips; ignored by git
```

Later specs add `release-slate`, `scope-audit`, and `release-check`
automation; this slice ships only `shape-release`, `cutline`, the release-plan
template, and the compact release slate file.

## Contributing

shaper currently uses the spec lifecycle documented in this repo. Every
non-trivial change starts with a vertical spec slice and moves through:

```text
DRAFT -> READY_FOR_REVIEW -> READY_FOR_IMPLEMENTATION -> IN_PROGRESS
  -> REVIEWED -> RECONCILED -> DONE
```

See [docs/workflow.md](docs/workflow.md) for the full process and
[docs/conventions.md](docs/conventions.md) before changing project rules.
