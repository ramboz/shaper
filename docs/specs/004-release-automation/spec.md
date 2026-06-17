---
status: DRAFT
skill: release-pipeline
tier: operations
adr_required: true
adr: ../../decisions/adr-0002-release-automation-and-archives.md
last_verified:
---

# Spec 004: Release automation and host-explicit archives

## Overview

After the hybrid plugin baseline and first release-plan-to-JIG product loop exist,
shaper should adopt the release model already proven by JIG and servo:
conventional commit PR titles, CI gates, release-please-managed versions and
changelog, and smoke-tested release archives uploaded to GitHub releases.

This spec is planning-only until ADR-0002 is accepted. It does not implement
workflows, builders, or archives yet.

## Sibling references

- JIG `origin/v2` Spec 013, `release-pipeline`: CI, PR-title gate,
  release-please, release zip builder, smoke test, and install docs.
- JIG `origin/v2` Spec 061 slice 04, `host-explicit-release-zips`: separate
  Claude and Codex zips with host-specific install semantics.
- Servo ADR-0007, `align-release-with-jig`: accepted decision to reuse JIG's
  release model without taking a runtime dependency.
- Servo Spec 010, `release-automation`: PR-title gate, release-please,
  package job, release asset, and docs.

## Goals

1. Add a conventional commit PR-title gate compatible with release-please.
2. Add a CI baseline for pull requests and `main`.
3. Add release-please configuration and workflow ownership of changelog,
   version tags, and GitHub releases.
4. Build and smoke-test host-explicit release archives:
   `shaper-claude-vX.Y.Z.zip` and `shaper-codex-vX.Y.Z.zip`.
5. Document the release and install contract without duplicating JIG or servo
   internals.

## Non-goals

- No marketplace submission automation.
- No package registry publishing.
- No release signing or notarization.
- No web UI or hosted deployment.
- No changes to `shape-release`, `cutline`, release-slate, release-check, or
  scope-audit behavior.
- No silent mutation of JIG spec state.

## SPIDR analysis

**Chosen axis: Path.**

The release path is: a pull request passes title and CI gates, release-please
opens and merges a release PR, GitHub creates the release, and a package job
builds, smoke-tests, and uploads the Claude and Codex archives. The slices keep
that path progressive without pretending release zips can be designed apart
from the host package baseline.

**Rejected splits:**

- Data-only: adding only workflow YAML or release config would not prove the
  end-to-end release path.
- Host-only: releasing Claude first and Codex later would undermine the hybrid
  baseline.
- Spike: JIG and servo have enough precedent for a direct implementation spec;
  deviations can be captured during reconciliation.

## Dependencies

- [ADR-0001: Hybrid plugin baseline](../../decisions/adr-0001-hybrid-plugin-baseline.md)
- [ADR-0002: Release automation and host-explicit archives](../../decisions/adr-0002-release-automation-and-archives.md)
- [Spec 003: Hybrid plugin baseline](../003-hybrid-plugin-baseline/spec.md)
- [Spec 002: First release-plan-to-JIG handoff loop](../002-release-plan-handoff/spec.md)

## Slices

- [004-01 - ci-and-conventional-commit-gate](slice-01-ci-and-conventional-commit-gate.md)
- [004-02 - release-please-pipeline](slice-02-release-please-pipeline.md)
- [004-03 - host-explicit-release-zips](slice-03-host-explicit-release-zips.md)
