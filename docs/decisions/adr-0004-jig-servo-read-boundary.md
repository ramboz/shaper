---
status: Accepted
dependencies: []
last_verified: 2026-06-20
frame_review: true
---

# ADR-0004: JIG/servo read boundary

## Status

Accepted (2026-06-20)

## Context

shaper can only consume servo quality signals safely if the read boundary is
explicit and narrow.

Spec 007 slice 007-01 intentionally shipped `shaper:release-check` as a
JIG-only advisory check. It reads release plans, JIG status, and related specs
without mutating JIG lifecycle state, then reports servo signals as "not
evaluated". Slice 007-02 is blocked until shaper decides what, if anything,
counts as an accepted servo signal.

The boundary matters because servo owns eval/oracle loops, quality gates, agent
loops, hooks, and heartbeat-style automation. shaper should be allowed to
include already-produced release evidence, but it must not become a servo
runtime, infer private servo state from implementation details, or make release
decisions look more certain than the underlying evidence supports.

The decision also needs to preserve graceful degradation. Many shaper target
repos will have no servo artifacts. In those repos, release-check should still
produce useful JIG/release-plan guidance and say that servo signals were not
evaluated.

## Decision Options Considered

### Option A: Keep release-check permanently JIG-only

- **Pros:** Simple, already implemented, and avoids accidental coupling to
  servo.
- **Cons:** Leaves no path for release-check to use quality evidence already
  produced by servo, even when a project has intentionally adopted it.

### Option B: Read only accepted servo release-signal artifacts

- **Pros:** Lets release-check include useful servo evidence while preserving
  ownership boundaries. The implementation can be deterministic, read-only,
  and fixture-testable.
- **Cons:** Requires servo-producing projects to write or expose a stable
  artifact. Signals outside the accepted artifact shape remain invisible until
  a later ADR expands the boundary.

### Option C: Discover servo state by scanning servo directories broadly

- **Pros:** Could surface more real-world signal without requiring a normalized
  artifact first.
- **Cons:** Couples shaper to servo internals, makes false confidence more
  likely, and turns absence or partial state into ambiguous release guidance.

### Option D: Invoke servo checks from release-check

- **Pros:** Could generate fresh signal at decision time.
- **Cons:** Violates shaper's non-goal of running eval/oracle loops, introduces
  runtime side effects, and makes release-check slower and less predictable.

## Recommended Decision

Adopt Option B.

`shaper:release-check` may read optional servo quality signals only from
explicit, repo-local release-signal artifacts. The accepted initial artifact
shape is:

```text
docs/servo/release-signals/<release-slug>.md
```

The `<release-slug>` segment must match the release plan slug being checked.
For example, `docs/releases/mvp.md` may be paired with
`docs/servo/release-signals/mvp.md`.

The artifact is Markdown with a small YAML frontmatter summary:

```yaml
---
release: mvp
status: pass
generated_at: YYYY-MM-DD
source: servo
---
```

Allowed `status` values are `pass`, `fail`, `mixed`, and `not-evaluated`.

The Markdown body may include human-readable sections such as `## Summary`,
`## Passing signals`, `## Failing signals`, `## Not evaluated`, and
`## Notes`. shaper treats the frontmatter status and body as advisory evidence;
it does not parse or execute embedded commands, links, scripts, or logs.

The read boundary is intentionally an allowlist:

- shaper may read the matching `docs/servo/release-signals/<release-slug>.md`
  file when it exists;
- shaper may report the artifact frontmatter and summarize body evidence;
- shaper may compare JIG/release-plan evidence and servo evidence, then call out
  agreement or disagreement;
- shaper must report missing servo artifacts as "not evaluated";
- shaper must not read arbitrary servo work directories, runtime state,
  heartbeats, queues, logs, caches, or generated reports outside this path;
- shaper must not run servo commands, loops, hooks, evaluators, oracle code, or
  heartbeat dispatch;
- shaper must not create, update, delete, normalize, or repair servo artifacts;
- shaper must not mutate JIG lifecycle state based on servo evidence.

Release-check recommendations remain advisory and JIG/release-plan grounded.
Servo evidence can strengthen the rationale, flag disagreement, or add caution,
but it cannot by itself override JIG status, no-gos, release appetite, or an
explicit release-plan extension requirement.

If JIG evidence and servo signals disagree, release-check should surface the
disagreement and recommend a human decision. It should not flatten disagreement
into a confident `ship` or `stop and re-shape` verdict unless the JIG/release
plan evidence independently supports that recommendation.

## Consequences

**Becomes easier:**

- Spec 007 slice 007-02 can implement optional servo signal reads without
  depending on servo internals.
- Fixtures can cover absent servo artifacts, pass signals, fail signals, mixed
  signals, malformed frontmatter, and JIG/servo disagreement.
- shaper stays useful in repos that have not adopted servo.
- The ownership line stays legible: servo produces quality signals; shaper reads
  them as release-planning evidence.

**Becomes harder:**

- Projects with existing servo outputs must add a release-signal artifact before
  shaper can consume them.
- Some potentially useful servo evidence is intentionally ignored until it is
  represented in the accepted artifact path.
- The first parser must be conservative around malformed frontmatter and body
  content, because shaper is not the owner of the artifact producer.

## Assumptions

<!-- Spec 064-02 / ADR-0020 §1–§2 — grounding-by-probe (risk-gated). -->

_Load-bearing factual claims about runnable surfaces (library/API capability,
version/perf behavior, behavior of existing code) must be backed by an executed
probe (run a command, read source/`node_modules`) or a citation — or listed
here explicitly as an assumption. Never assert an unverified claim as fact._

_Risk-gated: omit this section (or write "None") when the decision has no
unverified load-bearing assumptions — do not pad with boilerplate._

- servo can publish or already has enough information to publish a repo-local,
  release-scoped Markdown signal artifact.
- release slugs are stable enough to serve as the join key between
  `docs/releases/<slug>.md` and `docs/servo/release-signals/<slug>.md`.

## Kill criteria

_What would make this decision wrong? List the conditions that, if observed,
should reverse or shelve it. Risk-gated like Assumptions — write "None" or omit
when there is no meaningful kill condition; do not invent ceremonial ones._

- servo adopts a different stable, repo-local release-signal artifact before
  slice 007-02 starts.
- release-scoped Markdown cannot represent the signal families that release
  decisions actually need.
- consuming this path would force shaper to run servo code, trust live servo
  runtime state, or mutate servo-owned artifacts.

## Open questions

- Should a later ADR allow a project-level index, such as
  `docs/servo/release-signals/README.md`, or is one file per release enough?
- Should shaper eventually recognize machine-readable JSON alongside Markdown,
  or is Markdown frontmatter sufficient for the first implementation slice?
