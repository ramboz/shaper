---
name: cutline
description: >
  Read a release plan plus JIG specs/status when present, then recommend
  include, defer, split, and risk-first boundaries without mutating JIG
  lifecycle state.
user-invocable: true
---

# cutline

Use this skill when a maintainer has a release plan and wants a non-mutating
cutline across existing JIG work.

## Read boundary

Read only what is needed:

- the target `docs/releases/<slug>.md` release plan;
- `docs/specs/README.md`, when present;
- relevant `docs/specs/*` files, when present;
- `docs/product-vision.md` and `docs/architecture.md` only when the release
  boundary is unclear.

If `docs/specs/README.md` and relevant `docs/specs/*` files are absent, report
"No JIG specs/status board were found" and still provide release-plan-only
guidance. Leave JIG files untouched.

## Mutation boundary

- This is a non-mutating analysis skill for JIG artifacts.
- It must not edit JIG spec lifecycle state.
- It must not run `workflow.py transition`.
- It must not rewrite `docs/specs/README.md` or any `docs/specs/*` lifecycle
  field.
- It may update the release plan's `## Cutline` section only when the user asks
  for the cutline to be written back. Even then, leave JIG files untouched.

## Recommendation format

Classify each relevant item as one of:

- `include`: belongs inside the current appetite and release criteria;
- `defer`: useful but outside the current appetite or no-gos;
- `split`: too large or mixed; needs a smaller release-facing slice;
- `risk-first`: should not move to implementation until the risk/rabbit hole is
  retired.

Use this table when writing or reporting recommendations:

| Item | Evidence read | Recommendation | Rationale | Non-mutating JIG handoff |
|---|---|---|---|---|
| _spec/slice/idea_ | _release plan + JIG evidence_ | _include/defer/split/risk-first_ | _why_ | _draft/review instructions only_ |

Do not copy JIG lifecycle status into the release slate or turn the output into
a second status board. Link to JIG specs/slices when useful and explain the
release boundary in plain language.

For a deterministic first pass, run:

```bash
python3 skills/cutline/scripts/cutline.py --repo <repo> --release <slug>
```

The helper reads `docs/specs/README.md` and linked spec files when present,
prints include/defer/split/risk-first tables, and never writes to JIG files.
Use agent judgment to refine the rationale before writing recommendations back
to a release plan.

## Graceful degradation

- If no JIG specs/status board were found, say so and produce only
  release-plan-based recommendations.
- If servo signals are absent, do not block. This slice does not consume servo
  release-check signals.
- If a release plan is missing appetite, no-gos, or risks/rabbit holes, flag
  that gap before making confident include/defer calls.

## Output shape

End with:

- release plan inspected;
- JIG files read, or the no-JIG message;
- include/defer/split/risk-first recommendations;
- risks that must be retired before implementation;
- confirmation that JIG files were left untouched.
