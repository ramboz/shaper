---
slice: 004-03 - host-explicit-release-zips
pass: craft
verdict: pass
reviewer: jig-reviewer
reviewed_at: 2026-06-18T23:23:57Z
prompt_source: "'review.py pr-review docs/specs/004-release-automation/spec.md 004-03 <deliverables>'"
---

VERDICT: pass

REASONING:
The slice is cleanly scoped to release packaging: workflow gating, archive builder, smoke tests, ignore rules, and docs are aligned without broad product creep. No blockers remain after hardening corrupt-zip diagnostics, output-name validation, job-level permissions, and idempotent release-note append behavior.

SPECIFIC ISSUES:
- [nit] tests/test_release_archives.py:217 - This repeats much of the release workflow package-job checking already covered in tests/test_release_ci_gate.py:113, so future workflow edits may need duplicate test updates.
- [strength] scripts/build_release_zip.py:94 - Zip entry creation centralizes deterministic timestamp, compression, mode, and platform metadata.
- [strength] scripts/build_release_zip.py:138 - The builder refuses version and output-name mismatches before writing artifacts.
- [strength] .github/workflows/release.yml:29 - The package job is release-gated, checks out the tag, builds, smoke-tests, uploads, and appends install notes in one readable flow.
- [strength] README.md:143 - Docs give concrete local build/smoke commands and preserve the Claude flat-zip versus Codex extract-then-add distinction.

RECONCILIATION NOTES:
Record the duplicated workflow assertion as a low-priority cleanup candidate. Record deterministic archive writing, mislabeled-artifact guards, gated release job, and host-explicit install language as strengths.
