> Status: Draft (elicited)
>
> Decisions the initial setup explicitly deferred. Each item has a resolution trigger.
> Resolve with the smallest durable artifact that fits: spec text for reversible choices,
> ADRs only where a hard-to-reverse decision is needed.

# Refinement Todo: shaper

## Architecture

### Decision: Release-plan artifact shape
**Resolved:** ADR-0003 chooses `docs/releases/<slug>.md` for release plans and `docs/releases/README.md` for the compact release slate. `mvp`, `v1`, and `v2` are allowed as project-specific slugs, but they are not canonical artifact names.
**Resolution:** [ADR-0003: Release plan and no-backlog slate artifact model](decisions/adr-0003-release-plan-no-backlog-slate.md).

### Decision: Cutline recommendation format
**Deferred:** shaper can recommend transitions and generate patch-ready instructions, but JIG remains the source of truth for spec lifecycle state. The exact format for include/defer recommendations and patch-ready instructions is still open.
**Resolution trigger:** First `cutline` skill implementation that reads existing JIG specs/status board.

### Decision: JIG and servo detection depth
**Deferred:** shaper should detect JIG and servo if present and degrade gracefully if not. The first release-plan handoff and later release-check specs should decide how much detection is enough without building a full integration layer.
**Resolution trigger:** First slice that reads JIG status or optional servo quality signals.

### Decision: Plugin packaging and host layout
**Resolved:** shaper adopts JIG `v2`'s committed host-package baseline: root source manifests, committed `hosts/claude` and `hosts/codex` packages, and a regenerate/check drift guard. Product skills remain deferred and will be added to this package shape by later specs.
**Resolution:** [Spec 003: Hybrid plugin baseline](specs/003-hybrid-plugin-baseline/spec.md) / [ADR-0001: Hybrid plugin baseline](decisions/adr-0001-hybrid-plugin-baseline.md).

### Decision: Release archive shape
**Deferred:** shaper should reuse the JIG/servo release lessons, but the exact archive contract should be explicit before implementation. ADR-0002 proposes host-explicit Claude and Codex zips rather than a single host-neutral archive.
**Resolution trigger:** ADR-0002 accepted and Spec 004 reconciled.

### Decision: Host-package README rewriting
**Deferred:** Spec 003 intentionally copies the root README into minimal host packages. That leaves root-relative documentation links such as `docs/specs/README.md` broken when someone inspects only `hosts/claude` or `hosts/codex/plugins/shaper`.
**Resolution trigger:** First slice that adds host-specific runtime prose, product skills, or install verification beyond metadata-only packages.

### Decision: Hook and agent host rendering
**Deferred:** `scripts/build_host_packages.py` has future copy hooks for `agents/` and `hooks/`, but no hooks or agents ship in the Spec 003 baseline. Before those directories become real product payloads, shaper should decide whether host-specific rendering/trust documentation is needed instead of blanket copying.
**Resolution trigger:** First slice that adds shaper-owned hooks or agents to the plugin package.

## Conventions

### Decision: Code style and linting
**Resolved:** Initial Python helpers stay standard-library only. Static checking is currently the repo-local `.jig/lint-command`, which runs an AST syntax check over owned Python files without producing bytecode or requiring third-party tools.
**Resolution:** [Spec 003: Hybrid plugin baseline](specs/003-hybrid-plugin-baseline/spec.md).

### Decision: Lint file discovery
**Deferred:** `.jig/lint-command` explicitly enumerates the Python files introduced by Spec 003. This keeps initial static checking deterministic, but future Python helpers can be missed unless the command is updated.
**Resolution trigger:** Second slice that adds or moves Python helper files, or first time the explicit list misses a file during review.

### Decision: Testing framework
**Resolved:** The first builder tests use standard-library `unittest` through `.jig/test-command`, and the first code-health check compiles owned Python through `.jig/lint-command`; no package manager or third-party test/lint dependency is introduced.
**Resolution:** [Spec 003: Hybrid plugin baseline](specs/003-hybrid-plugin-baseline/spec.md).

## Operations

### Decision: CI/CD setup
**Deferred:** No CI is configured for the clean new project. ADR-0002 and Spec 004 propose the release baseline: conventional commit PR-title gate, CI, release-please, and host-explicit release archives.
**Resolution trigger:** ADR-0002 accepted and Spec 004 reconciled.
