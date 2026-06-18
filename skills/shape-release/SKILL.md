---
name: shape-release
description: >
  Create or refine a repo-native release plan in docs/releases/<slug>.md from
  raw product intent, appetite, no-gos, risks, release-check criteria, and JIG
  handoff notes.
user-invocable: true
---

# shape-release

Use this skill when a maintainer wants to turn rough product intent into a
bounded release plan before implementation work moves into JIG or another
spec-driven workflow.

## Boundaries

- Do not invent product intent. If a field is missing, ask for it or mark it as
  `TBD` in the release plan.
- Use the user's words where practical, especially for the problem, appetite,
  no-gos, risks/rabbit holes, and release-check criteria.
- Keep new plans in `candidate` status unless the user explicitly says the
  release is committed, shipping, shipped, or dropped.
- JIG owns implementation workflow and spec lifecycle. This skill may write JIG
  handoff notes, but it must not run lifecycle transitions or edit JIG status.
- If servo signals are absent, do not block. Record release-check criteria as
  desired future evidence rather than pretending signals exist.

## Inputs to gather

Read `templates/release-plan.md` first. Then elicit enough of these fields to
write or update `docs/releases/<slug>.md`:

- `status`: one of `candidate`, `committed`, `shipping`, `shipped`, `dropped`;
- `problem/baseline`: current state, problem, and why now;
- `appetite`: fixed time or attention budget and variable scope;
- `solution outline`: the smallest useful release shape;
- `risks/rabbit holes`: unknowns that could make the release unsafe or too
  large;
- `no-gos`: explicit exclusions;
- `cutline`: include, defer, split, and risk-first notes if known;
- `JIG handoff`: existing specs/slices to link or new specs to draft;
- `release-check criteria`: evidence that should be true before shipping.

Ask at most five focused questions at a time. If the user gives enough
information to start, write the plan and leave precise `TBD` markers for
unanswered fields.

## Writing or refining a plan

1. Choose a short kebab-case slug from the user's language.
2. Create `docs/releases/` if needed.
3. Write or update `docs/releases/<slug>.md` using
   `templates/release-plan.md`. For deterministic create/refine work, use
   `skills/shape-release/scripts/shape_release.py --repo <repo> --slug <slug>`
   with the fields the user supplied; leave omitted fields as `TBD`.
4. Preserve existing user-authored wording when refining a plan. Prefer
   appending clarifying bullets over rewriting the user's intent.
5. Keep the JIG handoff non-mutating: link to specs/slices or propose new JIG
   work, but leave JIG files untouched unless the user separately asks to edit
   a release plan's handoff notes.
6. Call out any absent sibling tools plainly. For example, if servo signals are
   absent, write "No servo signals were found; release-check criteria remain
   advisory."

## Output shape

End with a short summary:

- release plan path;
- status;
- appetite;
- unresolved questions;
- JIG handoff next step;
- whether any servo signals were absent.
