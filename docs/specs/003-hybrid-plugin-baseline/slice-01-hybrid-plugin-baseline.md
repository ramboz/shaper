---
status: DRAFT
dependencies: [adr-0001]
last_verified:
arch_review: true
code_health_review: true
---

## Slice 003-01 - hybrid-plugin-baseline

**Goal:** Establish shaper's Codex / Claude Code hybrid plugin baseline without
implementing product skills, so future slices can add `shape-bet` and
`cutline` against the correct package layout.

**DoR:**

- [ ] ADR-0001 is accepted.
- [ ] The implementer has rechecked JIG `origin/v2` for Spec 033, Spec 059,
      Spec 061, and ADR-0018.
- [ ] The implementer confirms whether to copy JIG builders directly or write
      smaller shaper-specific builders.

**Acceptance Criteria:**

1. **Root source manifests exist.** The implementation adds
   `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and
   `.codex-plugin/plugin.json` with shaper metadata.
2. **Claude remote install points at `hosts/claude`.** The root Claude
   marketplace pointer resolves to the committed Claude package, not to the
   repository root.
3. **Codex marketplace package exists under `hosts/codex`.** The package uses
   a Codex marketplace descriptor with `policy.installation`,
   `policy.authentication`, and `category`, and the plugin manifest avoids
   unsupported fields.
4. **Root source and host packages are distinct.** The implementation does not
   treat project-local `.codex/` jig scaffold files as shaper's canonical
   plugin source.
5. **Drift guard exists.** A command can regenerate host packages and a
   read-only check can fail when committed packages differ from source.
6. **Docs explain the baseline.** README or equivalent docs explain root
   source, committed host packages, Codex marketplace install semantics, and
   Claude Code install semantics.
7. **Product skills remain deferred.** `shape-bet`, `cutline`, roadmap,
   release-readiness, and scope-audit implementation remain out of scope for
   this slice.
8. **Release automation remains deferred.** CI/CD workflows, release-please,
   and release zip generation remain out of scope for this slice and are
   covered by Spec 004.

**DoD:**

- [ ] All ACs pass.
- [ ] Drift guard check passes.
- [ ] Any builder tests or smoke checks pass.
- [ ] `docs/architecture.md` is reconciled with the final package layout.
- [ ] `docs/refinement-todo.md` is reconciled for resolved packaging questions.
- [ ] `docs/specs/002-shaper-mvp` is updated only to depend on the baseline,
      not to absorb baseline implementation details.
- [ ] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [ ] Implementation review passed.
- [ ] Deviation log produced under this slice heading.
- [ ] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, a maintainer can
install or inspect shaper through the same host-package shape future skills
will ship in. The product behavior is intentionally deferred, but the external
plugin interface is end-to-end and usable as a baseline.

### Deviation log (after reconciliation)

_(Filled during reconciliation.)_
