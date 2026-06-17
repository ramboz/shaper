---
status: DRAFT
dependencies: [004-02, 003-01, adr-0002]
last_verified:
arch_review: true
code_health_review: true
---

## Slice 004-03 - host-explicit-release-zips

**Goal:** Build, smoke-test, and upload host-explicit release archives for
Claude Code and Codex whenever release-please creates a GitHub release.

**DoR:**

- [ ] Slice 004-02 is DONE.
- [ ] Spec 003 has committed `hosts/claude` and `hosts/codex` packages.
- [ ] ADR-0002 is accepted.
- [ ] The implementer has rechecked JIG `origin/v2` Spec 061 slice 04 for the
      host-explicit archive contract.
- [ ] The implementer confirms whether to copy JIG's archive builder directly
      or write a smaller shaper-specific builder.

**Acceptance Criteria:**

1. **Two deterministic archives are produced.** The package job creates
   `shaper-claude-vX.Y.Z.zip` and `shaper-codex-vX.Y.Z.zip` under `dist/` from
   the tagged source state.
2. **Claude archive is flat and install-shaped.** The Claude zip is built from
   `hosts/claude/` with `.claude-plugin/plugin.json` at the archive root.
3. **Codex archive is a marketplace bundle.** The Codex zip is built from
   `hosts/codex/` with `.agents/plugins/marketplace.json` and
   `plugins/shaper/.codex-plugin/plugin.json` at the expected paths.
4. **Codex install language is explicit.** Docs describe the Codex zip as an
   extract-then-add marketplace bundle, not as a directly installable zip.
5. **Archive smoke tests exist.** Smoke checks verify required files, version
   coherence, absence of repo-only scaffolding, and deterministic archive
   contents.
6. **Release upload is event-gated.** Archives are uploaded only when
   release-please creates a GitHub release.
7. **Generated archives are not committed.** `dist/` output and zip files stay
   ignored by git.

**DoD:**

- [ ] All ACs pass.
- [ ] The builder and smoke tests pass locally.
- [ ] The release workflow uploads both archives in a test or documented dry
      run.
- [ ] Install docs cover both artifacts and preserve the Claude/Codex semantic
      distinction.
- [ ] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, a maintainer can cut
a real shaper release and attach host-specific artifacts whose contents match
the installed plugin package shapes.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
