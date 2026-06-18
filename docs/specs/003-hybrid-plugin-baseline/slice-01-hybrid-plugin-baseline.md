---
status: DONE
dependencies: [adr-0001]
last_verified: 2026-06-18
arch_review: true
code_health_review: true
---

## Slice 003-01 - hybrid-plugin-baseline

**Goal:** Establish shaper's Codex / Claude Code hybrid plugin baseline without
implementing product skills, so future slices can add `shape-release` and
`cutline` against the correct package layout.

**DoR:**

- [x] ADR-0001 is accepted.
- [x] The implementer has rechecked JIG `origin/v2` for Spec 033, Spec 059,
      Spec 061, and ADR-0018.
- [x] The implementer confirms whether to copy JIG builders directly or write
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
7. **Product skills remain deferred.** `shape-release`, `cutline`,
   `release-slate`, `release-check`, and `scope-audit` implementation remain out
   of scope for this slice.
8. **Release automation remains deferred.** CI/CD workflows, release-please,
   and release zip generation remain out of scope for this slice and are
   covered by Spec 004.

**DoD:**

- [x] All ACs pass.
- [x] Drift guard check passes.
- [x] Any builder tests or smoke checks pass.
- [x] `docs/architecture.md` is reconciled with the final package layout.
- [x] `docs/refinement-todo.md` is reconciled for resolved packaging questions.
- [x] `docs/specs/002-release-plan-handoff` is updated only to depend on the
      baseline, not to absorb baseline implementation details.
- [x] No additional ADR is written unless implementation makes a new
      hard-to-reverse decision.
- [x] Reviewed by `reviewer` subagent. Reviewer prompt built by `review.py`.
- [x] Implementation review passed.
- [x] Deviation log produced under this slice heading.
- [x] Reconciliation review passed.

**Anti-horizontal-phasing check:** After this slice lands, a maintainer can
install or inspect shaper through the same host-package shape future skills
will ship in. The product behavior is intentionally deferred, but the external
plugin interface is end-to-end and usable as a baseline.

### Deviation log (after reconciliation)

- Implemented a smaller shaper-specific host-package builder instead of copying
  JIG's full host-rendering machinery. JIG `origin/v2` remains the precedent
  for the committed `hosts/<host>/` model, but shaper's initial baseline only
  needs metadata/README packages plus a drift guard because product skills,
  hooks, agents, and release archives are deferred.
- Added `.jig/test-command` with standard-library `unittest`, plus
  `.jig/lint-command` and `scripts/check_python_syntax.py` for no-bytecode
  syntax checking. This resolved the first testing/linting choices without a
  package-manager dependency.
- Added `.gitignore` entries for Python bytecode and `.ruff_cache/` after
  review surfaced generated cache churn from verification commands.
- Updated README and architecture to spell out current Claude and Codex install
  semantics. Claude uses the root `.claude-plugin/marketplace.json`
  `git-subdir` pointer to `hosts/claude`; Codex uses `hosts/codex` as a
  marketplace root pointing at `./plugins/shaper`.
- Reconciled reviewer follow-ups into `docs/refinement-todo.md`: host-package
  README rewriting, future hook/agent host rendering, and broader lint file
  discovery remain deferred until a later slice has real signal.
- Updated Spec 002's DoR to show that the hybrid plugin baseline is now
  established. Spec 002 remains otherwise scoped to product behavior and does
  not absorb packaging details.
- Review strengths to preserve: the drift guard rebuilds into a scratch tree
  before comparing committed `hosts/`, and tests verify both actionable drift
  output and non-mutating drift checks.
