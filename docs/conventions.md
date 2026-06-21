> Status: Draft (wizard-generated)
>
> **Changes to this file require explicit human approval.**
> Set `JIG_CONVENTIONS_APPROVED=1` in your shell session before editing, or the
> spec-gate hook will block the edit.

# Conventions: shaper

> Each rule below uses the format: **Rule** → **Why:** → **How to apply:**.
> Add rules as the project encounters real decisions worth recording.

## Documentation

**Rule:** Every wizard-generated doc carries a `Status: Draft (wizard-generated)` marker at the top.
**Why:** Distinguishes generated stubs from deliberate content, so reviewers and agents know what is authoritative.
**How to apply:** scaffold-init adds this marker. Flip it to `Status: Stable` after 3–5 reconciled specs have validated the doc structure (via a `scaffold-stable` ADR).

**Rule:** Deferred decisions are explicit, not silent.
**Why:** Silent gaps get forgotten. Explicit `Deferred` markers turn unknowns into trackable items.
**How to apply:** Use a `> **Deferred — <reason>.**` blockquote in the section. Add a corresponding entry to `docs/refinement-todo.md` with a resolution trigger.

## Specs

**Rule:** Every non-trivial change starts with a spec, SPIDR-split into vertical slices.
**Why:** Specs as contracts at the right granularity let humans and agents work in parallel without constant re-alignment.
**How to apply:** Run `/jig:spec-workflow` (when implemented), or write `docs/specs/NNN-<slug>/spec.md` by hand using the SPIDR template. Each slice must touch the user-facing layer (no horizontal phasing).

## Code style

**Rule:** Product helpers are standard-library Python unless a slice explicitly
justifies a dependency.
**Why:** shaper ships as a small host-neutral plugin, so low-dependency helpers
keep host packages easy to inspect, test, and archive.
**How to apply:** Put executable helper logic under the relevant `skills/*/`
tree or `scripts/`, prefer table-driven code over framework setup, and record a
new ADR/spec decision before adding a package manager or runtime dependency.

**Rule:** Static checks use the repo-local `.jig/lint-command` contract.
**Why:** A single checked command gives CI, agents, and humans the same syntax
baseline without introducing third-party lint tooling before it is needed.
**How to apply:** When a slice adds an owned Python helper, update
`.jig/lint-command` and focused tests in the same change.

## Testing

**Rule:** Tests use standard-library `unittest` through `.jig/test-command`.
**Why:** This matches the current helper style and keeps the project runnable in
plain Python environments.
**How to apply:** Add focused tests under `tests/` for helper behavior,
non-mutation boundaries, and host-package/archive contracts touched by the
slice. Broaden the test command only when a slice introduces a new executable
surface.

## Git

**Rule:** Pull-request titles use scoped conventional-commit syntax.
**Why:** Squash-merged PR titles become commit subjects on `main`, and
release-please uses those subjects to decide changelog entries and version
bumps.
**How to apply:** Use `type(scope): subject`, with one of the supported types in
`README.md`. Keep subjects lowercase and without a trailing period. Branch names
have no project-specific automation contract yet.
