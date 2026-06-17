---
dependencies: []
last_verified: 2026-06-17
---

# ADR-0003: Release plan and no-backlog slate artifact model

## Status

Accepted (2026-06-17)

## Context

shaper's initial language treated shaped work as one artifact and used
version-like release labels as likely file names. A Shape Up review then
suggested separating shaping from commitment. That distinction is useful as
inspiration, but it also asks non-Shape-Up users to learn too much process
vocabulary.

shaper should feel like a small sibling to JIG and servo. JIG users already
think in terms of specs, slices, releases, and readiness. Servo users already
think in terms of quality gates and release signals. For this audience, release
terminology is clearer than exposing Shape Up-native artifact and command names
as the public API.

The artifact model needs to preserve the useful Shape Up mechanics: appetite,
fixed time / variable scope, explicit no-gos, risk retirement, and the refusal
to create a backlog. It should do that through release plans and release
slates.

## Decision Options Considered

### Option A: Keep version-named shaped-work files

- **Pros:** Mirrors the original project prompt and is easy to understand.
- **Cons:** Makes release labels the architecture. It encourages a
  backlog-shaped progression of future versions instead of a current release
  planning surface.

### Option B: Use Shape Up-native shaping and commitment artifacts

- **Pros:** Closely follows the source inspiration and keeps shaping separate
  from commitment.
- **Cons:** Exposes too much Shape Up vocabulary in the public API. The
  Shape Up-native names are less natural for JIG/servo users who are trying to
  plan a release or milestone.

### Option C: Use a roadmap document as the primary overlay

- **Pros:** Familiar to maintainers coming from product-roadmap tools.
- **Cons:** Too likely to become a second status board or an evergreen backlog.
  This violates shaper's non-goal of replacing project-management systems.

### Option D: Use release plans and a compact release slate

- **Pros:** Matches the JIG/servo context while preserving the Shape
  Up-inspired mechanics inside the artifact. One release plan can move through
  candidate, committed, shipping, shipped, and dropped states without splitting
  the concept across separate artifact families.
- **Cons:** The internal distinction between "candidate" and "committed" must
  be explicit in the release plan status instead of encoded by separate
  directories.

## Recommended Decision

Adopt Option D.

Canonical release-plan artifacts live under:

```text
docs/releases/<slug>.md
```

The release slate lives at:

```text
docs/releases/README.md
```

Release-plan files use a status field rather than separate artifact families.
Allowed initial statuses are:

- `candidate` - shaped enough to discuss, not committed;
- `committed` - accepted for implementation handoff;
- `shipping` - implementation is in progress or nearing release;
- `shipped` - released or otherwise complete;
- `dropped` - intentionally not pursued right now.

Release-plan files include:

- status;
- problem and baseline;
- appetite;
- solution outline;
- risks/rabbit holes;
- no-gos;
- cutline;
- JIG handoff;
- release-check criteria.

The release slate is intentionally small and current. It may list active
candidate, committed, shipping, shipped, and currently relevant dropped release
plans. It is not a backlog, priority queue, sprint plan, or duplicate JIG status
board.

Slugs are short, kebab-case, and meaningful to the project. `mvp`, `v1`, and
`v2` remain valid slugs when they naturally fit a project, but they are not
canonical shaper concepts.

The public skill surface follows the same vocabulary:

- `shaper:shape-release` creates or refines `docs/releases/<slug>.md`;
- `shaper:cutline` adds non-mutating include/defer/split/risk-first
  recommendations to a release plan;
- `shaper:release-slate` maintains `docs/releases/README.md`;
- `shaper:scope-audit` checks release plans and JIG specs for scope leakage;
- `shaper:release-check` gives advisory ship/cut-scope/stop/re-shape guidance.

## Consequences

**Becomes easier:**

- shaper's public artifact names match release planning instead of requiring
  Shape Up fluency.
- The first product slice can stay focused on raw idea -> release plan -> JIG
  handoff.
- The project avoids treating `mvp`, `v1`, and `v2` as privileged release
  stages.
- The no-backlog constraint has a concrete home: the release slate is small by
  design.

**Becomes harder:**

- The release-plan status field must make candidate-vs-committed explicit.
- Skills must avoid silently changing a release plan from `candidate` to
  `committed` without an explicit user decision.
- Docs should mention Shape Up as inspiration without turning it into required
  vocabulary.

## Open questions

- The JIG/servo read boundary for `shaper:release-check` remains deferred to a
  later ADR before servo signals are consumed.
