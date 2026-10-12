---
status: READY_FOR_REVIEW
dependencies: [009-01, adr-0006]
last_verified:
arch_review: true
frame_review: true
claimed_by: copilot-third-host
---

## Slice 009-02 - copilot-release-artifact

**Goal:** A Shaper release publishes a version-coherent Copilot archive that a
user can extract, install, and use with the same skill behavior.

**DoR:**
- [ ] Slice 009-01 DONE.
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
- [ ] Archive/release tests have a witnessed red-to-green run.
- [ ] Full unit suite and syntax/manifest/drift/board/index checks pass.
- [ ] Independent compliance, craft, and architecture reviews pass.
- [ ] Deviation log and reconciliation sweep completed.
- [ ] Reconciliation review passes; memory and primers reconciled.

### Close-out (post-DONE)

- [ ] Status board regenerated and audited.
- [ ] Active-spec primer compressed after both slices DONE.

**Anti-horizontal-phasing check:** A user can download/extract/install the
release artifact and run Shaper, completing the released distribution path.

### Deviation log (after reconciliation)

Pending implementation and reviews.

### Reconciliation sweep

Pending implementation and reviews.
