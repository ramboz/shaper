---
status: IN_PROGRESS
skill: build-host-packages
use_cases: [UC-7, UC-8]
---

# Spec 009: Copilot CLI as a third committed host

> Implements [ADR-0006](../../decisions/adr-0006-copilot-third-host.md).
> Numbers reserved provisionally on the feature branch using JIG's local
> reservation mode; recheck against origin/main before opening the PR.

## Overview

Copilot users install and run Shaper's five existing skills through the same
committed, generated host-package mechanism used by JIG. Existing root source,
Claude/Codex packages, release-plan shape, and JIG/servo read-only boundaries
remain authoritative.

The port includes marketplace discovery, native skill paths, installed-runtime
helper resolution, loader guards, drift/version checks, and a released
`shaper-copilot-vX.Y.Z.zip`. It does not introduce product hooks, agents,
scaffolding, project instructions, a new version source, or IDE/cloud support.

### Grounded current state

- `scripts/build_host_packages.py` generates Claude and Codex packages and
  compares complete expected/committed file maps in its read-only drift guard.
- `scripts/build_release_zip.py` archives committed packages and checks
  versions, required files, forbidden repository content, and deterministic
  archive bytes.
- The five `skills/*/SKILL.md` files currently document source-relative helpers.
  Copilot rendering must separate installed runtime paths from consumer paths.
- `shape_release.py:_source_root` walks three parents to find `templates/`;
  placing skills and templates together under `.github` preserves that lookup.
- JIG's four migration/repair commits are linked in ADR-0006. The historical
  framing probe reported CLI 1.0.93-1; final repaired-package discovery,
  helper and authenticated skill-use evidence records CLI 1.0.96-2.

## Assumptions

The per-slice assumptions below define the frame-review scope. The installed
package probes are required evidence; static file presence is not substituted
for actual Copilot skill discovery.

## Decomposition

SPIDR uses **Interface** (install/use through the third host) followed by
**Path** (release/download/extract/install). Both slices provide end-to-end
consumer value. No standalone spike is needed: current-host contract checks
belong inside the install slice, and JIG already provides a concrete precedent.

## Slices

- [009-01 - installed-copilot-skills](slice-01-installed-copilot-skills.md)
- [009-02 - copilot-release-artifact](slice-02-copilot-release-artifact.md)
