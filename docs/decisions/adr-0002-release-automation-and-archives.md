---
dependencies: [adr-0001]
last_verified: 2026-06-17
---

# ADR-0002: Release automation and host-explicit archives

## Status

Accepted (2026-06-17)

## Context

shaper should inherit the release and distribution lessons from JIG and servo
instead of creating a bespoke release ritual.

The relevant sibling precedent is:

- JIG `origin/v2` Spec 013, `release-pipeline`, establishes a conventional
  commit PR-title gate, CI on pull requests and `main`, release-please
  ownership of versioning/CHANGELOG/GitHub releases, and a smoke-tested release
  zip uploaded to the GitHub release.
- JIG `origin/v2` Spec 061 slice 04, `host-explicit-release-zips`, updates the
  archive model for dual-host plugins: Claude and Codex receive separate
  release zips whose contents match their host install semantics.
- Servo ADR-0007, `align-release-with-jig`, accepts the same sibling release
  model without taking a runtime dependency on JIG.
- Servo Spec 010, `release-automation`, records the same pipeline shape:
  PR-title gate, release-please, package job, smoke test, and uploaded zip
  asset.

shaper is also a sibling plugin. If ADR-0001 is accepted, it will have
committed host packages under `hosts/claude` and `hosts/codex`. That makes a
host-explicit release archive model more appropriate than a single
host-neutral zip.

## Decision Options Considered

### Option A: Manual releases with a checklist

- **Pros:** No early automation cost.
- **Cons:** Easy to forget version bumps, changelog updates, smoke tests, or
  host-specific install caveats. This repeats the problem JIG and servo already
  solved.

### Option B: Release-please with one host-neutral zip

- **Pros:** Simple release automation and one artifact to document.
- **Cons:** Blurs the distinction between Claude Code's flat plugin package and
  Codex's marketplace bundle. This risks a misleading Codex zip that looks
  directly installable when it is really an extract-then-add marketplace
  bundle.

### Option C: Semantic-release or a custom versioning script

- **Pros:** Flexible and common in some ecosystems.
- **Cons:** Adds a second release convention across the sibling projects.
  shaper does not need npm-style publishing or a custom release engine.

### Option D: Adopt the JIG/servo release model with host-explicit zips

- **Pros:** Matches sibling precedent, keeps release decisions boring, and
  preserves host-specific install semantics. The release contract is explicit:
  release-please owns versioning and GitHub releases, CI guards changes, and
  release assets are smoke-tested host archives.
- **Cons:** Requires release workflow maintenance and two archive smoke tests.
  Host package version drift must be guarded carefully.

## Recommended Decision

Adopt Option D.

shaper should use the sibling release baseline:

- Enforce conventional commit PR titles so squash-merged main commits feed
  release-please correctly.
- Run CI on pull requests and `main`; the exact checks should be introduced by
  the release automation spec and should include tests, static checks, spec
  linting, manifest validation, and host-package drift checks once those exist.
- Use release-please with `release-type: simple` and `include-v-in-tag: true`.
- Let release-please own version bumps, `CHANGELOG.md`, Git tags, and GitHub
  releases.
- Build deterministic release archives only from the tagged source state.
- Smoke-test every archive before uploading it to the GitHub release.
- Do not publish to package registries or marketplaces as part of the initial
  release pipeline.
- Implement release/archive tooling as shaper-specific scripts that preserve
  the JIG/servo contracts without sharing runtime code.
- Document branch-protection expectations, but leave actual repository
  administration outside the plugin codebase.

The release archive contract should be host-explicit:

```text
dist/
  shaper-claude-vX.Y.Z.zip
  shaper-codex-vX.Y.Z.zip
```

`shaper-claude-vX.Y.Z.zip` is built from `hosts/claude/` and has the Claude
Code plugin package at the archive root, including `.claude-plugin/plugin.json`.

`shaper-codex-vX.Y.Z.zip` is built from `hosts/codex/` and has the Codex
marketplace bundle at the archive root, including
`.agents/plugins/marketplace.json` and
`plugins/shaper/.codex-plugin/plugin.json`. Documentation must describe this
as an extract-then-add marketplace bundle, not as a directly installable zip.

Release archives live in `dist/` during builds and are not committed.

## Consequences

**Becomes easier:**

- shaper follows the same release language as JIG and servo.
- Versioning, changelog generation, release tags, and GitHub releases have one
  owner.
- Claude and Codex users get archive shapes that match their host's install
  model.
- Future implementation specs can reason about release readiness without first
  inventing a release pipeline.

**Becomes harder:**

- The release pipeline needs two archive builders or one builder with
  host-specific modes.
- CI must validate generated host packages and release archive contents.
- Documentation must keep Codex's extract-then-add semantics distinct from
  Claude's flat plugin package.

## Open questions

None remaining for this decision. Before acceptance, the first CI floor was
set to spec/status checks where available, manifest validation, host-package
drift checks after Spec 003, and Python tests/static checks once executable
code exists.
