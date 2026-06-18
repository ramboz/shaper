---
slice: 004-02 - release-please-pipeline
pass: arch
verdict: pass
reviewer: jig:reviewer
reviewed_at: 2026-06-18T20:55:15Z
prompt_source: review.py arch-review docs/specs/004-release-automation/spec.md 004-02
---

VERDICT: pass

REASONING:
The release-please layer preserves the architecture boundary: release automation stays an operational concern and does not couple into shaper's product skills, JIG lifecycle mutation, or host archive building. Public/config contracts are updated coherently across release workflow, release-please config, docs, and manifest validation. The only architecture note is a non-blocking CI/CD trust-boundary nit around mutable action pinning in a write-permission workflow.

SPECIFIC ISSUES:
- [nit] .github/workflows/release.yml:22 — The high-privilege release workflow uses `googleapis/release-please-action@v4` rather than an immutable SHA; acceptable for sibling alignment, but this is a supply-chain trust-boundary choice worth documenting if it remains intentional.
- [strength] docs/architecture.md:137 — Release automation is modeled as an operational layer that validates, delegates version/tag/release ownership to release-please, and leaves archive building to the later slice.
- [strength] .github/release-please-config.json:8 — Version coherence is centralized in release-please `extra-files`, covering root and committed host-package manifests without adding a custom versioning script.
- [strength] README.md:151 — The public release PR contract clearly names the files release-please owns and explicitly forbids hand-editing managed plugin versions.

RECONCILIATION NOTES:
Record the mutable-action pinning choice as an accepted CI/CD trust-boundary deviation if the project intentionally follows sibling mutable major tags. Strengths to preserve: release-please remains the single owner for version/changelog/tag/GitHub release state, and archive upload remains explicitly deferred to 004-03.
