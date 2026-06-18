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
**Resolved:** The first `cutline` skill uses include/defer/split/risk-first recommendations with evidence, rationale, and non-mutating JIG handoff notes. It may write those recommendations to a release plan's `## Cutline` section when asked, but it must not edit JIG lifecycle state or run `workflow.py transition`.
**Resolution:** [Spec 002 slice 002-01](specs/002-release-plan-handoff/slice-01-release-plan-handoff.md) and [skills/cutline/SKILL.md](../skills/cutline/SKILL.md).

### Decision: JIG and servo detection depth
**Resolved for first handoff:** `cutline` performs shallow JIG detection by reading `docs/specs/README.md` and relevant `docs/specs/*` files when present. If no JIG specs/status board were found, it reports that state and leaves JIG files untouched. Servo signal consumption remains deferred to the later `release-check` work and must not block this handoff path.
**Resolution:** [Spec 002 slice 002-01](specs/002-release-plan-handoff/slice-01-release-plan-handoff.md), [skills/cutline/SKILL.md](../skills/cutline/SKILL.md), and [Spec 007: Release check](specs/007-release-check/spec.md).

### Decision: Plugin packaging and host layout
**Resolved:** shaper adopts JIG `v2`'s committed host-package baseline: root source manifests, committed `hosts/claude` and `hosts/codex` packages, and a regenerate/check drift guard. Spec 002 adds the first product skills (`shape-release` and `cutline`) to that package shape.
**Resolution:** [Spec 003: Hybrid plugin baseline](specs/003-hybrid-plugin-baseline/spec.md) / [ADR-0001: Hybrid plugin baseline](decisions/adr-0001-hybrid-plugin-baseline.md) / [Spec 002 slice 002-01](specs/002-release-plan-handoff/slice-01-release-plan-handoff.md).

### Decision: Release archive shape
**Deferred:** shaper should reuse the JIG/servo release lessons, but the exact archive contract should be explicit before implementation. ADR-0002 proposes host-explicit Claude and Codex zips rather than a single host-neutral archive.
**Resolution trigger:** ADR-0002 accepted and Spec 004 reconciled.

### Decision: Host-package README rewriting
**Resolved for first product skills:** Spec 002 keeps host README generation as an exact root README copy, but updates the root README so host packages accurately describe the shipped `shape-release` / `cutline` skills and deferred product skills. Host-specific link rewriting is still deferred because this slice adds host-neutral skills, not host-specific runtime prose or install verification.
**Resolution:** [Spec 002 slice 002-01](specs/002-release-plan-handoff/slice-01-release-plan-handoff.md) and [README.md](../README.md).

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
**Resolved for first gate:** Spec 004 slice 004-01 adds pull-request / `main` CI and a conventional-commit PR-title gate. CI runs the unittest suite, Python syntax check, manifest validation, host-package drift guard, and status-board drift check.
**Still deferred:** release-please and host-explicit release archives remain in later Spec 004 slices.
**Resolution:** [Spec 004 slice 004-01](specs/004-release-automation/slice-01-ci-and-conventional-commit-gate.md).
