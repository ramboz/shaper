---
status: RECONCILED
dependencies: [004-02, 003-01, adr-0002]
last_verified: 2026-06-18
arch_review: true
code_health_review: true
---

## Slice 004-03 - host-explicit-release-zips

**Goal:** Build, smoke-test, and upload host-explicit release archives for
Claude Code and Codex whenever release-please creates a GitHub release.

**DoR:**

- [x] Slice 004-02 is DONE.
- [x] Spec 003 has committed `hosts/claude` and `hosts/codex` packages.
- [x] ADR-0002 is accepted.
- [x] The implementer has rechecked JIG `origin/v2` Spec 061 slice 04 for the
      host-explicit archive contract.
- [x] The implementer confirms whether to copy JIG's archive builder directly
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

- [x] All ACs pass.
- [x] The builder and smoke tests pass locally.
- [x] The release workflow uploads both archives in a test or documented dry
      run.
- [x] Install docs cover both artifacts and preserve the Claude/Codex semantic
      distinction.
- [x] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, a maintainer can cut
a real shaper release and attach host-specific artifacts whose contents match
the installed plugin package shapes.

### Deviation log (after reconciliation)

- **Smaller shaper-specific archive builder.** JIG `origin/v2` Spec 061 slice
  04 was rechecked before implementation. shaper keeps the same host-explicit
  archive contract and deterministic zip mechanics, but uses a smaller
  `scripts/build_release_zip.py` instead of copying JIG's builder directly
  because shaper does not have JIG's install-contract modules, live install
  smoke scripts, or legacy host-neutral archive alias.
- **Host zips are built from committed host packages.**
  `shaper-claude-vX.Y.Z.zip` archives `hosts/claude/` with
  `.claude-plugin/plugin.json` at the zip root. `shaper-codex-vX.Y.Z.zip`
  archives `hosts/codex/` with `.agents/plugins/marketplace.json` and
  `plugins/shaper/.codex-plugin/plugin.json` at the expected paths.
- **Version, determinism, and smoke checks are local and standard-library.**
  The builder refuses mislabeled artifacts when the requested version differs
  from the host package manifest. Tests cover byte-identical repeated builds,
  required files, repo-only scaffolding exclusions, version mismatch behavior,
  and per-host smoke output.
- **Release upload is gated by release-please output.** The release workflow now
  checks out the release tag, runs the host-package drift guard, builds and
  smoke-tests both archives, uploads both with `gh release upload`, and appends
  install-artifact notes only when `release_created == 'true'`.
- **No legacy alias zip.** Unlike JIG's migration slice, shaper has no existing
  `shaper-vX.Y.Z.zip` consumer, so the workflow uploads only the two
  host-explicit archives.
- **Docs and committed host READMEs were reconciled.** README, architecture,
  and refinement-todo now describe archive upload as implemented. The host
  packages were regenerated so their copied READMEs carry the same Codex
  extract-then-add language.
- **Review hardening was folded back before REVIEWED.** Craft review found that
  corrupt zip files produced raw `zipfile.BadZipFile` tracebacks and custom
  `--output` names could mislabel artifacts. The builder now reports corrupt
  zips as clean `FAIL smoke[...]` diagnostics and refuses custom output
  basenames that do not match `shaper-<host>-v<version>.zip`.
- **Release workflow hardening was folded back before REVIEWED.** Review
  iteration flagged broad workflow-level permissions and non-idempotent release
  body appends. The workflow now defaults to read-only permissions, grants
  write permissions per job, and skips the install-artifacts append when the
  section is already present.
- **Remaining non-blocking review notes.** The release workflow still uses
  mutable major action tags, matching the 004-01 accepted trade-off; SHA pinning
  remains future hardening. Host package READMEs are still root README copies,
  so installed payload docs include maintainer-oriented repo links/commands;
  this is the known host README exact-copy limitation until host-specific prose
  rewriting is justified. `tests/test_release_archives.py` and
  `tests/test_release_ci_gate.py` intentionally overlap on release workflow
  assertions so archive-specific and release-pipeline tests each guard their
  slice contract; if workflow churn grows, extract a shared assertion helper.
- **Session memory update.** During this slice, the user explicitly approved
  Codex to spin up subagents whenever they materially help the task. That
  working preference was recorded in AGENTS.md and `docs/memory/tooling.md`
  through memory-sync; it affects future workflow execution but does not change
  shaper's release artifact behavior.
