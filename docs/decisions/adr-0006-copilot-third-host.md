---
status: Accepted
dependencies: [adr-0001, adr-0002]
last_verified: 2026-10-12
frame_review: true
---

# ADR-0006: Copilot CLI as a third committed host

## Status

Accepted (2026-10-12)

## Context

Shaper needs a first-class Copilot CLI package generated from its existing source.
UC-7 already captures use from Claude Code, Codex, or GitHub Copilot CLI.
ADR-0001 establishes committed, generated host packages; ADR-0002 establishes
host-explicit archives and release-please version ownership. This decision
extends those contracts without superseding either record.

JIG's migration provides the precedent and the mistakes to avoid:

- [`dc8d4534`](https://github.com/ramboz/jig/commit/dc8d4534) adds the third
  generated package and release artifact under JIG ADR-0061 / Spec 113.
- [`a51de9ba`](https://github.com/ramboz/jig/commit/a51de9ba) fixes component
  discovery by declaring `.github/skills` in `.plugin/plugin.json`.
- [`3e6faff0`](https://github.com/ramboz/jig/commit/3e6faff0) adds a separate
  `.github/plugin/marketplace.json` with a relative string source, avoiding
  Copilot's rejection of Claude's `git-subdir` source object.
- [`3412c4d5`](https://github.com/ramboz/jig/commit/3412c4d5) fixes agent-issued
  helper commands: they run from the consuming repository, not the plugin.

The tracked product set is closed by `git ls-files skills/* templates/*
agents/* hooks/*`: five public skills, five Python helpers, one release-plan
template, and no product agents or hooks. The development-only `.codex/`
JIG runtime is not Shaper source (ADR-0001). `copilot --version` reports
1.0.93-1 on 2026-10-12; its plugin help documents marketplace and repository
subdirectory installation.

## Decision Options Considered

### Option A: Reuse the Claude package unchanged

- **Pros:** No third generated tree.
- **Cons:** The root marketplace uses Claude's source dialect, and existing
  skill commands are project-relative. This does not adopt the corrected JIG
  install/runtime model.

### Option B: A generated, committed Copilot package (chosen)

- **Pros:** One product source, native discovery metadata, remote installation
  without building, and the existing drift/release model.
- **Cons:** A third generated tree and a small Copilot-only prose/root adapter.

### Option C: Copy JIG's complete Copilot runtime

- **Pros:** Reuses its complete scaffolding, hook, and agent adapters.
- **Cons:** Introduces capabilities Shaper does not own and unnecessary runtime
  coupling. JIG's enforced lifecycle remains JIG's responsibility.

## Recommended Decision

Choose Option B. The repository root remains canonical source. Extend
`scripts/build_host_packages.py` and its read-only drift guard to generate:

```text
.github/plugin/marketplace.json       source: "./hosts/copilot"
hosts/copilot/
  .plugin/plugin.json                skills: ".github/skills"
  README.md
  shaper.jpg
  .github/
    skills/<name>/SKILL.md
    skills/<name>/scripts/*.py
    templates/release-plan.md
    scripts/shaper_root.py
```

The generated manifest takes its version from the existing canonical Claude
manifest, matching JIG's mechanism; it is added to release-please's extra files
and cross-host version validation. There is no new root version authority.
Omit `agents`, `hooks`, and other unsupported/unneeded component declarations.

Keep executable product helpers and the release-plan template shared and
byte-identical. Apply Copilot path/loader adaptations to generated skill prose
only. Each skill is self-contained: its quoted `$SHAPER_ROOT` helper and
template references resolve to the installed `.github` runtime, not the
consuming repository. Use the disclosed absolute skill directory when
available, with a standard-library locator/bootstrap for fresh-shell use
that honors `COPILOT_HOME`, validates Shaper identity/runtime files, and
fails visibly if no runtime exists. No hook is added to publish this root.

Enforce colon-free frontmatter names and descriptions of at most 1,024
characters at the Copilot render boundary. Existing descriptions fit; if
shortening becomes necessary, retain the full description in the skill body.
Keep consumer paths such as `docs/releases/` and `docs/specs/` unchanged.
Do not copy project instructions or development scaffolding into the package.

Publish `shaper-copilot-vX.Y.Z.zip` from the committed Copilot package,
with `.plugin/plugin.json` at the archive root. Document extraction followed
by local-directory installation, not an unverified direct zip-install flow.
Retain Claude/Codex layout and behavior. This decision covers Copilot CLI;
it makes no IDE or cloud-agent parity claim.

Static manifest/archive checks are necessary but insufficient. The implementing
spec requires actual installed skill discovery in an isolated Copilot home,
documented helper execution from a separate consumer directory, and a live
Copilot workflow run.

## Consequences

**Becomes easier:**
- Copilot users run the same release-shaping skills without copying files.
- Future releases carry three host-explicit artifacts with one version owner.

**Becomes harder:**
- Source changes require regeneration of three committed packages.
- Copilot install/loader behavior needs an honest live verification boundary.

## Assumptions

- A1: JIG's corrected legacy-manifest and marketplace layout remains accepted
  by CLI 1.0.93-1. Spec 009's isolated installed-package probe must verify this
  before claiming the port works.

## Kill criteria

- The supported CLI cannot discover the generated skills through the declared
  package paths or cannot install the marketplace package. Revisit the host
  rendering rather than ship an installed-but-unusable plugin.

## Open questions

None beyond assumption A1's implementation-time verification.
