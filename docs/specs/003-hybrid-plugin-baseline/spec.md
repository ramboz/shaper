---
status: DRAFT
skill: release-pipeline
tier: host-adapter
adr_required: true
adr: ../../decisions/adr-0001-hybrid-plugin-baseline.md
last_verified:
---

# Spec 003: Hybrid plugin baseline

## Overview

Before implementing `shape-bet`, `cutline`, or roadmap behavior, shaper
should establish itself as a Codex / Claude Code hybrid plugin using the
baseline proven by JIG's `v2` branch.

This spec is planning-only until ADR-0001 is accepted. It defines the future
implementation slice that will create shaper's root plugin source, committed
host packages, and drift guard. It does not implement the skills themselves.

## JIG references

- JIG Spec 033, `host-adapter-portability`: host adapter contract, support
  matrix, host-native rendering, and "copy prose, share code".
- JIG Spec 059, `codex-port-polish`: Codex hook trust, Codex skill override
  language, TOML custom-agent caveats, and avoiding undocumented plugin
  manifest fields.
- JIG Spec 061, `dual-host-plugin-artifacts`: committed `hosts/claude` and
  `hosts/codex` packages generated from canonical source.
- JIG ADR-0018, `dual-host-generated-plugin-artifacts`: accepted decision for
  committed, source-derived host packages under `hosts/<host>/`.
- JIG Spec 061 slice 04, `host-explicit-release-zips`: release archives should
  be host-explicit once release automation is added.

## Goals

1. Establish root canonical plugin source for shaper.
2. Add Claude and Codex source manifests with shaper metadata.
3. Add committed host packages under `hosts/claude` and `hosts/codex`.
4. Add a drift guard that regenerates host packages and fails on drift.
5. Keep the existing project-local `.codex/` jig scaffold separate from
   shaper's plugin source.
6. Update docs so future skill work starts from the hybrid baseline.

## Non-goals

- No `shape-bet` implementation.
- No `cutline` implementation.
- No roadmap automation.
- No release-readiness or scope-audit automation.
- No servo signal consumption.
- No CI/CD workflows or release zips. Spec 004 owns release automation and
  archive distribution.
- No custom agents unless a concrete shaper role is identified during the
  baseline implementation.

## SPIDR analysis

**Chosen axis: Interface.**

The slice stabilizes the install/interface shape that both hosts consume:
Claude Code package, Codex marketplace package, root manifests, and drift
guard. Once this lands, product skills can be implemented against a stable
runtime layout.

**Rejected splits:**

- Data-only: adding manifests without package generation would not prove the
  install shape.
- Path-only: Codex-first then Claude-later repeats the retrofit this baseline
  is meant to avoid.
- Spike: JIG v2 already contains the relevant precedent. Any differences
  should surface as deviations during implementation.

## Slices

- [003-01 - hybrid-plugin-baseline](slice-01-hybrid-plugin-baseline.md)
