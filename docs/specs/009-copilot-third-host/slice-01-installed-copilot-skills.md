---
status: DONE
dependencies: [adr-0006]
last_verified: 2026-10-12
arch_review: true
frame_review: true
---

## Slice 009-01 - installed-copilot-skills

**Goal:** A Copilot CLI user installs Shaper and runs its existing release
shaping skills from a consuming repository without copying runtime files.

**DoR:**
- [x] ADR-0006 accepted after frame critique.
- [x] The spec/slice frame review passes.
- [x] Existing five skills, helpers, template, builder, and unittest runner exist.

**Acceptance Criteria:**

1. **Generated package and native marketplace.** The unified builder emits
   `hosts/copilot/.plugin/plugin.json` declaring `skills: ".github/skills"`,
   all five skill/helper trees, `.github/templates/release-plan.md`, the root
   locator, README and image. The root `.github/plugin/marketplace.json`
   declares Shaper with `source: "./hosts/copilot"`. No product hooks, agents,
   project instructions, JIG development runtime, tests, or repository docs
   ship. Existing Claude/Codex runtime files remain unchanged.
2. **Runnable, self-contained skill prose.** Every generated skill's documented
   helper uses a quoted absolute installed-runtime root, with instructions to
   resolve that root. Template references resolve to the packaged template.
   Consumer `docs/` paths remain consumer-relative. Executable product helpers
   and the template remain byte-identical to source. Root resolution honors
   `COPILOT_HOME`, works with spaces and direct/marketplace install layouts,
   prefers the invoked skill's disclosed runtime when available, and produces
   a nonzero exit plus diagnostic when no valid Shaper runtime exists.
3. **Loader and manifest contracts.** Copilot frontmatter names contain no
   colon; descriptions fit 1,024 characters (retain full descriptions in body
   if shortened). Reject malformed/missing metadata or component paths
   explicitly. All versioned manifests agree, with Copilot's generated version
   derived from the existing canonical source. The drift guard detects missing,
   extra, and stale Copilot files without mutating committed packages.
4. **Installed discovery and helper behavior.** An isolated `COPILOT_HOME`
   marketplace/local-package install and `copilot skill list --json` from a
   separate empty consumer directory discover all five Shaper skills. Execute
   their documented helper commands against that installed package: create a
   release plan, refresh the slate, and obtain cutline/scope/release advice.
   Verify bundled template lookup and that JIG/servo fixtures remain unchanged.
   Record CLI version and command evidence; plugin-list presence alone fails
   this criterion.
5. **Live skill use and adopter docs.** Run a live Copilot session in the
   isolated consumer fixture that uses Shaper to create a release plan and
   refresh the slate through its installed skills. Record the transcript/result
   honestly, separate from deterministic discovery/helper evidence. README
   documents marketplace add/install and direct subdirectory installation,
   skill verification, and the supported CLI-only boundary.

## Assumptions

- A1: JIG's corrected legacy plugin/marketplace layout remains accepted by
  CLI 1.0.93-1. AC4 verifies this, not a static manifest assertion.

**DoD:**
- [x] ACs covered by witnessed failing-then-passing tests/probes.
- [x] Existing unit suite and syntax/manifest/drift checks pass.
- [x] Independent compliance, craft, and architecture reviews pass.
- [x] Deviation log and reconciliation sweep completed.
- [x] Reconciliation review passes; memory and derived boards reconciled.

### Close-out (post-DONE)

- [x] Status board regenerated and audited.
- [x] Primer retains only in-flight slice 009-02.

**Anti-horizontal-phasing check:** A user can install the package and produce
usable release-plan/slate artifacts through Copilot after this slice.

### Deviation log (after reconciliation)

1. **No product scope deviation.** Copilot metadata/prose/root adaptation is
   host-only. Product helpers and the release-plan template remain byte-identical;
   Claude/Codex runtime files are unchanged except generated shared READMEs.
2. **Current CLI proof.** Initial marketplace/direct discovery and a live agent
   run passed on 1.0.93-1. The CLI available later reported 1.0.96-2; the repaired
   package was reinstalled in isolated homes and both deterministic helper
   modes plus an authenticated two-skill workflow passed on that version.
   Evidence separates those runs and does not assert remote publication.
3. **Compliance blockers repaired with witnessed regression tests.** Discovery
   now reads data only rather than executing foreign installed locators.
   The owned frontmatter subset rejects malformed auxiliary fields, YAML
   comment/alias/anchor/tag forms, and undoubled single-quoted escapes.
   Successive reviews confirmed these fixes; see `slice-01-review-fixes.json`.
4. **Craft nits addressed.** The packaged standalone locator is now exercised
   directly, including incomplete-runtime failure, and fixture helper tests
   clear ambient `SHAPER_SKILL_DIR`. Focused suite: 16 tests pass.
5. **Architecture nits reconciled.** Install-contract and hybrid-baseline prose
   now name the Copilot adapter. Data-only bootstrap and standalone locator
   retain a small two-entry-point policy mirror; parity tests guard them.
   Consolidation is deferred until a root-policy change gives it signal,
   rather than adding code-generation/introspection machinery to this port.
6. **Release scope stays next.** Copilot archive/release-please changes belong
   to 009-02 and are not claimed by this slice.

### Reconciliation sweep

| Artifact | Disposition | Rationale |
|---|---|---|
| `README.md` / generated host READMEs | `updated` | Copilot install commands, skill discovery, runtime-root use, and CLI-only scope. |
| `docs/architecture.md` | `updated` | Third package, native metadata, host-only prose adapter and install inventory. |
| `docs/product-vision.md` | `updated` | Stack/principles now reflect existing UC-7's third host without new product scope. |
| `AGENTS.md` / scaffold templates | `updated` | Primer tracks in-flight Spec 009; no consuming-project instruction file ships. |
| `docs/specs/README.md` / `.jig/spec-ref` | `updated` | Generated lifecycle board and JIG transition-owned active reference. |
| Spec 009 `spec.md`, `plan.md`, `tasks.md` | `updated` | UC-7/8 trace, grounded historical/final CLI distinction, prerequisite-aware delivery plan and completed implementation tasks. |
| Former `slice-01-tbd.md` | `updated` | Reservation stub replaced/renamed to this filled vertical slice; no closed record rewritten. |
| Spec 009 `evidence/` and `reviews/` | `updated` | Witnessed TDD, installed/live proofs, blocker repair history and actual reviewer verdicts; temporary handoff removed after live proof. |
| `docs/decisions/README.md` / ADR-0006 | `updated` | Decision accepted through recorded frame critique; index regenerated. Prior ADRs untouched. |
| `docs/refinement-todo.md` | `updated` | Small bootstrap/locator policy mirror has an explicit future-change trigger. |
| `docs/memory/learnings.md` | `updated` | Installed-root and foreign-locator failure lessons persisted with memory helper. |
| `docs/inbox.md` / conventions | `no-op` | No parked ideas resolved; no convention changes required. |
| CI / `.jig/lint-command` | `updated` | Owned Python and tests remain covered by existing standard-library syntax gate. |
| `.codex/` / unrelated `.claude/` | `no-op` | Development runtime and pre-existing untracked files are outside product port scope. |
| Release archive/workflow | `deferred` | Owned by dependent slice 009-02. |
