---
name: release-slate
description: >
  Read docs/releases/*.md release plans and write or refresh the compact
  docs/releases/README.md slate without creating a backlog or duplicating JIG
  lifecycle state.
user-invocable: true
---

# release-slate

Use this skill when a maintainer wants a compact view of release plans that
matter right now: candidate, committed, shipping, recently shipped, and
currently relevant dropped/no-go plans.

## Read boundary

Read only what is needed:

- `docs/releases/*.md` release plans, excluding `docs/releases/README.md`;
- the existing `docs/releases/README.md`, when present, to know this is an
  update rather than a first write;
- JIG handoff links already present inside each release plan's `## JIG Handoff`
  section.

Do not read `docs/specs/README.md` to copy lifecycle state into the slate. JIG
remains the source of truth for implementation status.

## Mutation boundary

- Write or update `docs/releases/README.md`.
- Do not edit release-plan files.
- Do not edit JIG files.
- Do not run `workflow.py transition`.
- Do not add priority ranks, backlog queues, roadmap sections, or copied JIG
  lifecycle/status columns.

## Slate shape

Keep the slate small and current. It must contain these sections:

- `Candidate`
- `Committed`
- `Shipping`
- `Shipped`
- `Dropped`

Each entry links to the release plan and may include JIG handoff links from the
release plan. Keep the note short; do not copy the full release plan, release
criteria, cutline table, or JIG status-board state.

Dropped plans belong only while they still explain a current no-go or release
decision. If an old idea is present only as a stale row in the existing slate
and no release-plan file backs it, remove it.

For the deterministic first pass, run:

```bash
python3 skills/release-slate/scripts/release_slate.py --repo <repo>
```

The helper discovers release plans, rewrites `docs/releases/README.md`, and
prints whether an existing slate was read.

## Graceful empty state

If no release plans exist, create `docs/releases/README.md` with the standard
sections, `_None yet_` rows, and a short empty-state note. Do not invent
example work.

## Output shape

End with:

- slate path;
- number of release plans discovered;
- whether an existing slate was read;
- confirmation that JIG lifecycle state was not copied.
