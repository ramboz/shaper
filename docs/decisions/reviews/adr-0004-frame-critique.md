---
adr: 0004
pass: frame-critique
verdict: pass
reviewer: codex
reviewed_at: 2026-06-21T01:01:10Z
prompt_source: review.py frame-critique docs/decisions/adr-0004-jig-servo-read-boundary.md
---

VERDICT: pass

REASONING:
The highest-risk assumption is that servo can publish, or already has enough
information to publish, a repo-local release-scoped Markdown signal artifact.
That assumption is not proven here, but the ADR names it directly, limits
implementation to a read-only allowlist, and gives kill criteria that stop
slice 007-02 if servo standardizes on a different artifact.

SPECIFIC ISSUES:
- servo can publish `docs/servo/release-signals/<release-slug>.md` — this could
  be wrong if servo's durable output is not release-scoped, not Markdown, or
  not repo-local. If so, implementing the parser would be misdirected, but the
  ADR's assumption and kill criteria make that failure cheap to catch before
  implementation rather than after.
