> Status: Draft (elicited)
>
> Decisions the initial setup explicitly deferred. Each item has a resolution trigger.
> Resolve with the smallest durable artifact that fits: spec text for reversible choices,
> ADRs only where a hard-to-reverse decision is needed.

# Refinement Todo: shaper

## Architecture

### Decision: Bet artifact shape
**Deferred:** The pitch suggests `docs/bets/mvp.md`, `docs/bets/v1.md`, `docs/bets/v2.md`, or a better shape if the architecture pass recommends one. The MVP spec should prove the smallest useful shape before locking it down.
**Resolution trigger:** First implementation of the shaped-bet template and `shape-bet` skill.

### Decision: Cutline recommendation format
**Deferred:** shaper can recommend transitions and generate patch-ready instructions, but JIG remains the source of truth for spec lifecycle state. The exact format for include/defer recommendations and patch-ready instructions is still open.
**Resolution trigger:** First `cutline` skill implementation that reads existing JIG specs/status board.

### Decision: JIG and servo detection depth
**Deferred:** shaper should detect JIG and servo if present and degrade gracefully if not. The MVP should decide how much detection is enough without building a full integration layer.
**Resolution trigger:** First slice that reads JIG status or optional servo quality signals.

### Decision: Plugin packaging and host layout
**Deferred:** shaper should be cross-host from the start, supporting both Claude Code and Codex plugin surfaces where practical. ADR-0001 proposes adopting JIG `v2`'s committed host-package baseline before product skills are implemented.
**Resolution trigger:** ADR-0001 accepted and Spec 003 reconciled.

### Decision: Release archive shape
**Deferred:** shaper should reuse the JIG/servo release lessons, but the exact archive contract should be explicit before implementation. ADR-0002 proposes host-explicit Claude and Codex zips rather than a single host-neutral archive.
**Resolution trigger:** ADR-0002 accepted and Spec 004 reconciled.

## Conventions

### Decision: Code style and linting
**Deferred:** Python is likely, but no non-trivial shaper code exists yet.
**Resolution trigger:** First spec that produces non-trivial Python code, or first time inconsistency causes friction.

### Decision: Testing framework
**Deferred:** The project starts clean with no test suite. The MVP should introduce only the test shape it actually needs.
**Resolution trigger:** First spec that requires tests beyond ad-hoc verification.

## Operations

### Decision: CI/CD setup
**Deferred:** No CI is configured for the clean new project. ADR-0002 and Spec 004 propose the release baseline: conventional commit PR-title gate, CI, release-please, and host-explicit release archives.
**Resolution trigger:** ADR-0002 accepted and Spec 004 reconciled.
