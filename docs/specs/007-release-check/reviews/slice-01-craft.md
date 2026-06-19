---
slice: 007-01 - JIG-only release check
pass: craft
verdict: pass
reviewer: pr-review
reviewed_at: 2026-06-19T16:37:02Z
prompt_source: review.py pr-review
---

Well-crafted single-purpose non-mutating helper mirroring scope_audit.py/
cutline.py patterns: repo-root path containment with a leak-proof test, honest
servo-absent reporting, clear ordered recommendation decision tree with explicit
rationale per branch. 13 behavior-named tests cover all four recommendation
paths plus degradation, missing-plan, and outside-repo cases.

Initial verdict was needs-changes with one blocker: release_check.py and
tests/test_release_check.py were missing from CI's explicit check_python_syntax
list (.github/workflows/ci.yml) and a Python 3.11 SyntaxError (backslash inside
f-string expression). Both fixed: CI syntax list updated, the f-string escape
extracted to a plain statement. Nits addressed: softened "Active JIG work"
rationale wording (release-check intentionally flags DONE no-go conflicts too).
Remaining nits (helper duplication across three skills; EMPTY_MARKERS vs
"none listed" duplication; stop-and-reshape rationale not folding co-occurring
risks) logged as deviations — non-blocking.
