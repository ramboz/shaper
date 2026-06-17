---
status: DRAFT
dependencies: [004-01, adr-0002]
last_verified:
arch_review: true
code_health_review: true
---

## Slice 004-02 - release-please-pipeline

**Goal:** Let release-please own shaper's version bumps, changelog, tags, and
GitHub release creation.

**DoR:**

- [ ] Slice 004-01 is DONE.
- [ ] ADR-0002 is accepted.
- [ ] The implementer has rechecked JIG `origin/v2` Spec 013 and Servo Spec
      010 for release-please configuration details.
- [ ] The implementer identifies every manifest or metadata file whose version
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

- [ ] All ACs pass.
- [ ] A dry-run or documented simulation shows how the next release PR would be
      produced.
- [ ] Version-coherence checks pass after release-please configuration is
      added.
- [ ] Documentation explains the release PR flow and the squash-merge
      expectation.
- [ ] `docs/architecture.md` and `docs/refinement-todo.md` are reconciled.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, the project has a
real automated release decision path, even though archive creation waits for
the next slice.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
