---
slice: 007-01 - JIG-only release check
pass: arch
verdict: pass
reviewer: arch-review
reviewed_at: 2026-06-19T16:37:02Z
prompt_source: review.py arch-review
---

Change slots cleanly into the documented "Release check" module boundary in
docs/architecture.md, honors the JIG read-only contract surface, and defers
servo reads to the future read-boundary ADR exactly as architecture, spec, and
ADR-0003 require. Helper is fully self-contained (stdlib-only) per the
established skill self-containment pattern (scripts/ is not copied into host
packages; skills/ is) and is confirmed packaged into both hosts/claude and
hosts/codex with a clean drift check. All reads confined to --repo. No public
contract artifact needs a same-changeset update beyond what is present.

Two doc nits (SKILL.md could note repo-relative/absolute release inputs and the
in-scope fallback rule) addressed via the new "Matching notes" section.
