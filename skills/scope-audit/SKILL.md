---
name: scope-audit
description: >
  Read a release plan plus JIG specs/status when present, then flag appetite
  leakage, creep, unresolved rabbit holes, no-go conflicts, overreach, and
  orphan specs without mutating JIG lifecycle state.
user-invocable: true
---

# scope-audit

Use this skill when a maintainer has a release plan and wants advisory scope
recommendations against current JIG work.

## Read boundary

Read only what is needed:

- the target `docs/releases/<slug>.md` release plan;
- `docs/releases/README.md`, when present;
- `docs/specs/README.md`, when present;
- linked or relevant `docs/specs/*` files, when present.

If JIG artifacts are absent, say so and still report release-plan gaps such as
missing appetite, unresolved rabbit holes, or no-gos. Leave JIG files untouched.

## Mutation boundary

- This is a non-mutating analysis skill for JIG artifacts.
- It must not edit JIG spec lifecycle state.
- It must not run `workflow.py transition`.
- It must not rewrite `docs/specs/README.md` or any `docs/specs/*` lifecycle
  field.
- It writes recommendations or patch-ready instructions only.

For a deterministic first pass, run:

```bash
python3 skills/scope-audit/scripts/scope_audit.py --repo <repo> --release <slug>
```

The helper reads release-plan, release-slate, and JIG Markdown when present,
prints advisory findings, and never writes JIG files. Use agent judgment to
refine the rationale before turning findings into follow-up specs or JIG
workflow commands.

## Output shape

End with:

- release plan inspected;
- JIG files read, or the no-JIG message;
- scope findings grouped by appetite leakage, nice-to-have creep, rabbit holes
  and no-gos, JIG overreach, and orphan specs;
- patch-ready instructions only;
- confirmation that JIG files were left untouched.
