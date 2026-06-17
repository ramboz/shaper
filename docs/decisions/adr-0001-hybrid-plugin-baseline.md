---
dependencies: []
last_verified: 2026-06-17
---

# ADR-0001: Hybrid plugin baseline

## Status

Proposed (2026-06-17)

## Context

shaper should start as a Codex / Claude Code hybrid plugin, not as a
single-host scaffold that later gets ported.

The project exists as a sibling to JIG and servo, and it should reuse the
delivery lessons from JIG instead of rediscovering them. JIG's `v2` branch
records the relevant path:

- Spec 033, `host-adapter-portability`, defines the adapter contract:
  keep one workflow model, render host-native files, copy prose, share code,
  and avoid a universal runtime import layer.
- Spec 059, `codex-port-polish`, records the practical Codex caveats:
  Codex hook trust must be explicit, unsupported manifest fields must be
  avoided, and custom agents remain TOML/project-local or explicitly installed
  until plugin-native discovery is documented.
- Spec 061, `dual-host-plugin-artifacts`, completes the delivery shape:
  root source is canonical, and committed host packages under `hosts/claude`
  and `hosts/codex` are generated from source and drift-checked.
- JIG ADR-0018 accepts the key decision: committed, source-derived per-host
  packages are worth the duplication because they preserve remote
  one-command install with no local build step.

shaper can adopt that baseline before any `shape-bet` or `cutline`
implementation begins.

## Decision Options Considered

### Option A: Start Codex-only and add Claude later

- **Pros:** Smallest immediate setup because the repo was scaffolded from
  Codex first.
- **Cons:** Repeats JIG's portability sequence and makes Claude support a
  retrofit. Early specs may accidentally bake in Codex-only paths.

### Option B: Keep only scaffold-mode project-local runtime

- **Pros:** Uses the existing `.codex/` scaffold output and avoids package
  source decisions.
- **Cons:** Does not create an installable shaper plugin. It also confuses
  the development scaffold with the product's own plugin source.

### Option C: Generate host packages into untracked `dist/`

- **Pros:** Clean source/output separation and no generated files in git.
- **Cons:** Breaks the remote marketplace install path that needs the runtime
  package to exist in the repository. This is the rejected option from JIG
  ADR-0018.

### Option D: Adopt JIG v2's committed host-package baseline

- **Pros:** Starts shaper with the proven hybrid plugin architecture: root
  source, host-native committed packages, explicit Codex caveats, and a drift
  guard. Remote install can point to committed host packages instead of the
  entire repo.
- **Cons:** Built package content lives in git and must be regenerated and
  drift-checked after source changes.

## Recommended Decision

Adopt Option D: shaper should use JIG v2's hybrid plugin baseline.

The repository root is canonical source. Host-specific install payloads are
committed, source-derived packages:

```text
repo root/
  skills/ templates/ agents/ hooks/       canonical plugin source as needed
  .claude-plugin/                         Claude source manifest + marketplace pointer
  .codex-plugin/                          Codex source manifest
  hosts/
    claude/                               committed Claude Code plugin package
    codex/                                committed Codex marketplace package
  dist/                                   generated release zips only, not tracked
```

The first implementation spec should establish this baseline before building
the `shape-bet`, `cutline`, roadmap, release-readiness, or scope-audit skills.

Implementation must preserve these constraints:

- Do not treat the existing project-local `.codex/` scaffold runtime as
  shaper's canonical plugin source.
- Do not point Claude remote install at the repository root.
- Do not put unsupported fields such as hooks or agents into
  `.codex-plugin/plugin.json`.
- Do keep Codex hook trust and custom-agent discovery caveats explicit if
  shaper adds hooks or agents later.
- Do add a drift guard so committed host packages cannot silently diverge from
  source.
- Do leave CI/CD and release zip automation to ADR-0002 and Spec 004.

## Consequences

**Becomes easier:**

- shaper starts with equal respect for Codex and Claude Code.
- Future release and install docs can follow JIG's already-tested package
  shape.
- MVP skills can be written against a stable plugin layout instead of moving
  during implementation.

**Becomes harder:**

- The repo will carry generated `hosts/` packages that must be regenerated and
  checked.
- The first implementation slice must establish packaging infrastructure before
  shaper's product skills are useful.
- Future source edits need to consider both host renderings.

## Open questions

- How much of JIG's host-package builder should shaper copy directly versus
  shrinking for shaper's smaller surface?
- Should shaper define any custom agents in the first baseline, or defer agents
  until a concrete role emerges?
