# Decisions

> Status: Draft (wizard-generated)
>
> Architectural Decision Records for shaper. Nygard convention: immutable
> after acceptance. New decisions supersede old ones — never edit an accepted ADR.

## Index

- [ADR-0001: Hybrid plugin baseline](adr-0001-hybrid-plugin-baseline.md) — shaper should start as a Codex / Claude Code hybrid plugin, not as a single-host scaffold that later gets ported. (2026-06-17, Accepted)
- [ADR-0002: Release automation and host-explicit archives](adr-0002-release-automation-and-archives.md) — shaper should inherit the release and distribution lessons from JIG and servo instead of creating a bespoke release ritual. (2026-06-17, Accepted)
- [ADR-0003: Release plan and no-backlog slate artifact model](adr-0003-release-plan-no-backlog-slate.md) — shaper's initial language treated shaped work as one artifact and used version-like release labels as likely file names. (2026-06-17, Accepted)
- [ADR-0004: JIG/servo read boundary](adr-0004-jig-servo-read-boundary.md) — shaper can only consume servo quality signals safely if the read boundary is explicit and narrow. (2026-06-20, Accepted)
- [ADR-0005: Vertical-scope shaping and a bounded architecture-appetite handoff](adr-0005-vertical-scope-shaping-and-architecture-appetite.md) — shaper's charter is to shape raw product intent into a bounded release plan "before and above JIG specs," then hand implementation-ready work to jig ([product-vision.md](../product-vision.md) Identity / Positioning). (2026-08-11, Accepted)

## Format

Each ADR lives at `docs/decisions/adr-NNNN-<slug>.md`. Title: `# ADR-NNNN: <Title>`.

Required sections: Status, Context, Decision Options Considered, Recommended Decision, Consequences.

## When to write an ADR

- Hard-to-reverse decisions
- Decisions that affect multiple modules or the public API
- When a contract changes in a breaking way
- When the `architect` subagent produces a proposal that is accepted
