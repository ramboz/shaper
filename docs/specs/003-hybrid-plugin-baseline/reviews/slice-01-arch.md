---
slice: 003-01 - hybrid-plugin-baseline
pass: arch
verdict: pass
reviewer: jig-reviewer
reviewed_at: 2026-06-17T23:22:54Z
prompt_source: review.py arch-review docs/specs/003-hybrid-plugin-baseline/spec.md 003-01 <deliverables>
---

VERDICT: pass

REASONING:
The refreshed baseline preserves the documented architecture: root plugin manifests remain canonical, host-specific packages are committed generated payloads, and `.codex/` stays scoped to the project-local JIG runtime. Public install-contract docs were updated alongside the manifests and builder, and release automation/product skills remain cleanly deferred rather than leaking into this slice.

SPECIFIC ISSUES:
- [strength] docs/architecture.md:178 - The plugin install contract explicitly names the source manifests, committed host packages, and drift guard as the contract surface.
- [strength] scripts/build_host_packages.py:213 - Drift checking rebuilds into a scratch directory, preserving the committed `hosts/` tree during read-only verification.
- [strength] README.md:112 - The distribution docs clearly state that the current install surfaces are intentionally metadata/README-only and defer product skills and release archives to later specs.
- [nit] scripts/build_host_packages.py:23 - The generic future copy list includes `agents` and `hooks`; harmless while absent, but future hook/agent slices should revisit host-specific trust/discovery rules before relying on this blanket copy path.

RECONCILIATION NOTES:
Record the nit as a future-design watchpoint, not a blocker: when hooks or agents are introduced, the package builder may need host-specific rendering or explicit trust documentation rather than generic directory copying.
