---
status: DONE
dependencies: [009-01, adr-0006]
last_verified: 2026-10-12
arch_review: true
frame_review: true
---

## Slice 009-02 - copilot-release-artifact

**Goal:** A Shaper release publishes a version-coherent Copilot archive that a
user can extract, install, and use with the same skill behavior.

**DoR:**
- [x] Slice 009-01 DONE.
- [x] Spec/slice frame review passes.
- [x] Existing release-please and host-explicit archive pipeline exists.

**Acceptance Criteria:**

1. **Host-explicit deterministic archive.** `--host copilot` builds
   `shaper-copilot-vX.Y.Z.zip` from committed `hosts/copilot`, with the manifest
   at the archive root. It includes all five skill/helper trees, template, root
   locator, README and image. Repeated builds are byte-identical. Reject unknown
   hosts, missing packages, mismatched filename/version, missing or invalid
   discovery paths, and repository-only content. Preserve existing Claude/Codex
   archive contracts.
2. **Version and release wiring.** Release-please updates
   `hosts/copilot/.plugin/plugin.json` alongside existing versioned manifests.
   The gated tagged-source package job checks drift, builds and smoke-tests the
   Copilot archive, uploads all three archives, and appends an accurate install
   note without replacing changelog notes. Manifest validation and tests cover
   the fifth versioned manifest and the new marketplace descriptor.
3. **Extracted-package consumer proof.** Extract the Copilot archive, install
   that directory under an isolated Copilot home, and prove all five skills
   are discovered from a clean consumer directory. Execute installed helpers to
   create/refine a plan and refresh its slate; read-only advice preserves the
   JIG/servo fixtures. Validate the archive's declared component paths rather
   than merely counting files.
4. **Distribution documentation.** README and architecture docs describe the
   three-host mechanism, archive naming, supported CLI-only scope, and
   extract-then-install semantics. Contributor checks cover newly owned Python.
   No hand-managed manifest version, JIG runtime migration, hook/agent adapter,
   or new product behavior is introduced.

## Assumptions

- A1: Installing an extracted directory exercises the same discovery contract
  as the committed package. AC3 must prove this through the current CLI.
  GitHub release upload is validated locally by workflow contracts; actual
  publication occurs only when release-please's release PR is merged.

**DoD:**
- [x] Archive/release tests have a witnessed red-to-green run.
- [x] Full unit suite and syntax/manifest/drift/board/index checks pass.
- [x] Independent compliance, craft, and architecture reviews pass.
- [x] Deviation log and reconciliation sweep completed.
- [x] Reconciliation review passes; memory and primers reconciled.

### Close-out (post-DONE)

- [x] Status board regenerated and audited.
- [x] Active-spec primer compressed after both slices DONE.

**Anti-horizontal-phasing check:** A user can download/extract/install the
release artifact and run Shaper, completing the released distribution path.

### Implementation evidence

- [Witnessed red/green](evidence/slice-02-tdd.json): focused 36 tests green;
  implementer-handoff full suite 127 tests green on Python 3.14.0.
- [Final parent checks](evidence/slice-02-final-checks.json): 134 tests,
  24 owned Python syntax checks, both current/vendored-compatible board gates,
  all three archives and an exact final extracted-payload CLI probe pass.
- [Local checks](evidence/slice-02-checks.json): all three packages regenerated,
  manifests/drift/archive/syntax gates pass; current JIG board and ADR index
  checks pass without changing parent-owned derived docs. The discovered
  legacy-renderer footer mismatch is resolved by the read-only CI adapter in
  [board compatibility evidence](evidence/slice-02-board-compatibility.json);
  no `.codex` runtime migration was performed.
- [Actual extracted-directory install](evidence/slice-02-extracted-cli.json):
  Copilot CLI 1.0.96-2, five enabled installed skills from a separate consumer,
  create/refine/slate/advice helpers and unchanged JIG/servo SHA-256 fixtures.
  No authenticated agent session or GitHub publication is claimed by this probe.
- Python 3.12 shim could not resolve an interpreter. All owned files parse with
  Python 3.11 grammar; actual minimum-version interpreter runs remain CI-owned.
- Independent compliance/craft/architecture passes are recorded. Reconciliation
  and landing remain parent-owned until their gates clear.

### Deviation log (after reconciliation)

1. **Archive/release contract delivered without a version fork.** The flat
   Copilot archive comes from committed `hosts/copilot`; native validation is
   shared with the package builder. Release-please owns all five manifests.
   Tagged-source drift, three archive smoke checks, uploads and additive
   install notes retain the existing release boundary.
2. **Real extracted install, not mocked substitution.** Local CLI evidence
   records five enabled skills from the copied extracted payload, create/refine,
   slate and advisory helper commands, byte-identical payload and protected
   JIG/servo fixture hashes. The unit probe mocks only external CLI operations;
   the real local probe is separate. Actual publication remains release-owned.
3. **Scoped CI compatibility addition.** Current JIG ceremony introduced an
   advisory richer-skill audit footer that the older vendored renderer removed.
   `scripts/check_spec_board.py` runs the existing renderer in a scratch copy
   and compares lifecycle rows/spec rollups without discarding the source audit.
   This is necessary to preserve the required CI gate, not a runtime migration.
   Craft review caught a missing/audit-hidden table false pass; witnessed red
   regressions now verify explicit structural rejection and source immutability.
   Later REVIEWED-state checks also exposed older-renderer display differences:
   only committed lifecycle Status cells normalize nonlocking review-owner
   hints. Regenerated source truth, deferred triggers and `IN_PROGRESS` claims
   remain untouched, with seven regression tests proving those boundaries.
4. **Interpreter evidence is bounded.** Local checks run on Python 3.14, with
   Python 3.11 grammar parsing. The 3.12 shim cannot resolve an interpreter.
   Actual 3.11/3.12 execution is delegated to the existing GitHub CI matrix,
   not claimed from grammar parsing.
5. **Review outcome.** Compliance and architecture pass; craft passes after
   the board blocker repair. No new dependency, product capability, lifecycle
   owner, convention, or accepted-record rewrite was introduced.

### Reconciliation sweep

| Artifact | Disposition | Rationale |
|---|---|---|
| `README.md` / all three generated READMEs | `updated` | Third archive, extract/install/probe instructions, release flow and local CI checks. |
| `docs/architecture.md` / `docs/product-vision.md` | `updated` | Three-host release contract, CLI-only scope and read-only board compatibility boundary. |
| `.github/release-please-config.json` / release workflow | `updated` | Fifth versioned manifest, third build/smoke/upload artifact and additive notes. |
| CI / `.jig/lint-command` | `updated` | New probe/board helper tests in owned syntax inventory; board gate remains strict/read-only. |
| `scripts/build_release_zip.py` / `tests/test_copilot_release.py` | `updated` | Third-host archive, shared native guards, deterministic/type-safe rejection coverage and release workflow contracts. |
| `scripts/smoke_copilot_archive.py` | `updated` | Actual extracted-directory install proof reuses existing discovery/helper boundary routines and adds refinement checks. |
| `scripts/check_spec_board.py` / `tests/test_spec_board_check.py` | `updated` | Read-only scratch adapter and seven witnessed compatibility/false-pass regression cases. |
| `tests/test_release_ci_gate.py` | `updated` | Five-manifest release inventory and new compatible board-check invocation. |
| Inherited `.github/plugin/marketplace.json`, `scripts/build_host_packages.py`, `scripts/shaper_root.py`, `scripts/validate_manifests.py`, `scripts/smoke_copilot_install.py`, `tests/test_copilot_host.py` | `no-op` | Delivered, independently reviewed and reconciled in 009-01; reused rather than reimplemented or regraded here. |
| Non-README `hosts/copilot/**` payload | `no-op` | Inherited 009-01 manifest/image/skills/helpers/template/locator bytes; 009-02 archives and validates that committed payload without altering its product behavior. |
| Spec 009 overview/plan/tasks/slice records | `updated` | Implemented release path and current phase tracking; earlier first-slice record only receives prescribed post-DONE close-out ticks. |
| Spec 009 evidence/reviews | `updated` | Witnessed red/green, real extracted CLI proof, board blocker fix and durable actual verdicts. |
| `docs/specs/README.md` / `.jig/spec-ref` | `updated` | Current JIG lifecycle-derived board/reference; CI wrapper verifies core against vendored renderer. |
| `AGENTS.md` | `updated` | Tracks the final in-flight release slice; compress-on-close-out follows DONE. |
| `docs/inbox.md` | `updated` | Renderer mismatch parked by implementer is explicitly resolved by scoped CI adapter. |
| `docs/refinement-todo.md` | `updated` | Existing live packaging/release summaries now link the Copilot extension; root-policy mirror trigger retained. |
| `docs/memory/learnings.md` | `updated` | Board-format/root false-success failure lessons persisted via memory helper. |
| ADR-0006 / decision index | `no-op` | Accepted decision remains unchanged; index audit is clean. |
| Conventions / `.codex/` / unrelated `.claude/` | `no-op` | No convention edits or runtime migration; untracked runtime metadata is not staged as product source. |
