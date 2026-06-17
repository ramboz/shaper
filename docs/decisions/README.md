# Decisions

> Status: Draft (wizard-generated)
>
> Architectural Decision Records for shaper. Nygard convention: immutable
> after acceptance. New decisions supersede old ones — never edit an accepted ADR.

## Index

- [ADR-0001: Hybrid plugin baseline](adr-0001-hybrid-plugin-baseline.md) — shaper should start as a Codex / Claude Code hybrid plugin, not as a single-host scaffold that later gets ported. (Accepted 2026-06-17)
- [ADR-0002: Release automation and host-explicit archives](adr-0002-release-automation-and-archives.md) — shaper should adopt the JIG/servo release automation model with separate Claude and Codex release zips. (Accepted 2026-06-17)
- [ADR-0003: Release plan and no-backlog slate artifact model](adr-0003-release-plan-no-backlog-slate.md) — shaper uses release plans and a compact release slate instead of Shape Up-specific public artifact names or a backlog. (Accepted 2026-06-17)

## Format

Each ADR lives at `docs/decisions/adr-NNNN-<slug>.md`. Title: `# ADR-NNNN: <Title>`.

Required sections: Status, Context, Decision Options Considered, Recommended Decision, Consequences.

## When to write an ADR

- Hard-to-reverse decisions
- Decisions that affect multiple modules or the public API
- When a contract changes in a breaking way
- When the `architect` subagent produces a proposal that is accepted
