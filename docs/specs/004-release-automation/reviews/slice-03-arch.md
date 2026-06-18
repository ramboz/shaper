---
slice: 004-03 - host-explicit-release-zips
pass: arch
verdict: pass
reviewer: jig-reviewer
reviewed_at: 2026-06-18T23:23:57Z
prompt_source: "'review.py arch-review docs/specs/004-release-automation/spec.md 004-03 <deliverables>'"
---

VERDICT: pass

REASONING:
The slice preserves the intended architecture boundary: release-please owns version/tag/release state, the package job is gated on release_created, and the archive builder consumes committed host packages rather than root source. Claude/Codex public archive contracts are explicit in docs, workflow naming, builder behavior, and smoke-test coverage.

SPECIFIC ISSUES:
- [nit] .github/workflows/release.yml:24 - The write-capable release workflow still depends on mutable action tags; SHA pinning would tighten the release supply-chain trust boundary.
- [nit] hosts/claude/README.md:117 - Host package READMEs are root README copies and include repo-only links/commands, blurring installed package docs with source-repo maintainer docs.
- [strength] .github/workflows/release.yml:31 - Archive upload is gated on release-please creating a release.
- [strength] scripts/build_release_zip.py:158 - Archive entries are sorted from the host package root, keeping deterministic output tied to committed host payload shape.
- [strength] docs/architecture.md:179 - The architecture names the release archive contract as a public surface and distinguishes Claude flat archives from Codex marketplace bundles.

RECONCILIATION NOTES:
Record mutable action pinning and copied host README repo-only prose as non-blocking follow-ups. Preserve the clean release-please/package-builder boundary and explicit Claude-vs-Codex archive semantics.
