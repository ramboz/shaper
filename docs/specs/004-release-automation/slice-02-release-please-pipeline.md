---
status: DONE
dependencies: [004-01, adr-0002]
last_verified: 2026-06-18
arch_review: true
code_health_review: true
---

## Slice 004-02 - release-please-pipeline

**Goal:** Let release-please own shaper's version bumps, changelog, tags, and
GitHub release creation.

**DoR:**

- [x] Slice 004-01 is DONE.
- [x] ADR-0002 is accepted.
- [x] The implementer has rechecked JIG `origin/v2` Spec 013 and Servo Spec
      010 for release-please configuration details.
- [x] The implementer identifies every manifest or metadata file whose version
      must stay coherent.

**Acceptance Criteria:**

1. **Release-please config exists.** The implementation adds release-please
   configuration using the sibling baseline: `release-type: simple` and
   `include-v-in-tag: true`.
2. **Release metadata is coherent.** Release-please updates the canonical
   shaper version source and every committed plugin manifest that must match
   that version.
3. **CHANGELOG is generated.** Release notes come from conventional commits
   rather than a handwritten changelog ritual.
4. **GitHub releases are release-please-owned.** Merging the release PR creates
   the tag and GitHub release through release-please.
5. **Archive upload is still deferred.** This slice may emit the release event
   that a later package job consumes, but it does not build or upload release
   zips.

**DoD:**

- [x] All ACs pass.
- [x] A dry-run or documented simulation shows how the next release PR would be
      produced.
- [x] Version-coherence checks pass after release-please configuration is
      added.
- [x] Documentation explains the release PR flow and the squash-merge
      expectation.
- [x] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, the project has a
real automated release decision path, even though archive creation waits for
the next slice.

### Deviation log (after reconciliation)

- **Sibling release-please baseline followed, with shaper-specific manifest
  breadth.** The workflow/config shape follows the local JIG Spec 013 and
  Servo Spec 010 precedent: `googleapis/release-please-action@v4`,
  `release-type: simple`, `include-v-in-tag: true`, root package key `.`, and
  release-please-managed changelog/tag/GitHub release ownership. shaper expands
  `extra-files` to all four versioned plugin manifests because committed
  `hosts/claude` and `hosts/codex` packages must stay drift-free when
  release-please bumps the root manifests.
- **Archive upload deliberately stays out of this slice.** The release workflow
  exposes release-please outputs but does not build zips, call
  `gh release upload`, or add a package job. That preserves the 004-03
  boundary for host-explicit release archives.
- **Dry-run evidence is documented rather than live-run.** The README now
  documents a `npx release-please release-pr ... --dry-run` command and the
  release PR file set. A real release PR/tag/GitHub release can only be
  observed after this lands on `main`, which matches the inherent
  release-please model.
- **Reviewer hardening notes are non-blocking.** Craft and architecture review
  both noted that `googleapis/release-please-action@v4` is a mutable major tag
  in a write-permission workflow. This follows the existing local action-pin
  style accepted in 004-01 and sibling precedent; future release hardening can
  SHA-pin actions if the project chooses. Craft also noted that manual
  `workflow_dispatch` should be treated as a main-branch operation.
- **Code-health note: manifest path duplication is intentional test pressure.**
  `tests/test_release_ci_gate.py` repeats the versioned-manifest path set from
  release-please config and manifest validation. That duplication is acceptable
  here because the test guards the release contract directly; if more versioned
  metadata files appear, the project should consider extracting a shared
  manifest inventory.
