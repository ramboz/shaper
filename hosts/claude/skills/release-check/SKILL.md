---
name: release-check
description: >
  Read a release plan plus JIG specs/status when present, then give an advisory
  ship / cut-scope / stop-and-re-shape / extend-with-rationale recommendation
  from JIG evidence only, without mutating JIG lifecycle state.
user-invocable: true
---

# release-check

Use this skill when a maintainer has a release plan and wants an advisory call
on whether the release is shippable, scope should be cut, work should stop and
be re-shaped, or an extension is explicitly justified.

This is the JIG-only slice. Servo quality signals are reported as not evaluated,
never as a failure. Optional servo signal reads wait for the JIG/servo
read-boundary ADR.

## Read boundary

Read only what is needed:

- the target `docs/releases/<slug>.md` release plan: appetite, cutline, JIG
  handoff, release-check criteria, risks / rabbit holes, and no-gos;
- `docs/specs/README.md`, when present;
- linked or relevant `docs/specs/*` specs and slices, when present.

If `docs/specs/README.md` and relevant `docs/specs/*` files are absent, report
"No JIG specs/status board were found" and give release-plan-only guidance.
Leave JIG files untouched.

## Mutation boundary

- This is a non-mutating analysis skill for JIG artifacts.
- It must not edit JIG spec lifecycle state.
- It must not run `workflow.py transition`.
- It must not rewrite `docs/specs/README.md` or any `docs/specs/*` lifecycle
  field.
- It produces a recommendation and rationale only.

## Recommendation

Output exactly one recommendation:

- `ship`: in-scope JIG work is DONE, no unresolved rabbit holes remain, and no
  active work conflicts with a no-go.
- `cut scope`: a DONE subset is shippable while some in-scope work is
  incomplete; trim or defer the incomplete work to ship within appetite.
- `stop and re-shape`: active work conflicts with a no-go, nothing in scope is
  DONE, or an unresolved rabbit hole has no scope left to cut.
- `extend only with explicit rationale`: recommended only when the release plan
  records an explicit extension rationale (an `## Extension` section). The skill
  never invents an extension on its own.

Always surface open risks — unresolved rabbit holes and no-go conflicts —
before recommending ship.

For a deterministic first pass, run:

```bash
python3 skills/release-check/scripts/release_check.py --repo <repo> --release <slug>
```

The helper reads the release plan and `docs/specs/README.md` plus linked spec
files when present, prints the release criteria read, JIG status, open risks,
and a single recommendation with rationale, and never writes to JIG files. Use
agent judgment to refine the rationale before acting on it.

## Matching notes

The helper is deterministic and advisory; refine its calls with judgment:

- The release argument accepts a slug (resolved to `docs/releases/<slug>.md`), a
  repo-relative path, or an absolute path. All reads are confined to the repo
  root; paths that escape it are reported as missing.
- In-scope JIG work is the set of board rows whose spec is linked from the
  release plan. When the plan links no specs (or none match the board), the
  helper falls back to treating every board row as in-scope.
- No-go conflicts use word-subset and phrase matching, so the match is
  heuristic: it can over-match when a no-go shares vocabulary with legitimate
  work, and under-match across singular/plural wording. Treat a flagged
  conflict as a prompt to confirm, not a verdict.
- A rabbit hole counts as an open risk only when its text carries an unresolved
  marker (e.g. `TBD`, `unresolved`, `needs decision`). All listed rabbit holes
  are still surfaced under "Release Criteria Read".

## Graceful degradation

- If no JIG specs/status board were found, say so and base the recommendation
  on the release plan alone.
- Servo signals are always reported as not evaluated in this slice. Do not block
  or fail when servo artifacts are absent.
- If a release plan is missing appetite, no-gos, or risks, flag that gap before
  making a confident recommendation.

## Output shape

End with:

- release plan inspected;
- JIG files read, or the no-JIG message;
- servo signals reported as not evaluated;
- release criteria read;
- JIG status of in-scope work;
- open risks (rabbit holes and no-go conflicts);
- a single recommendation with rationale;
- confirmation that JIG files were left untouched.
