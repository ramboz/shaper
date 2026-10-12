# Spec 009 tasks

## Framing

- [x] ADR-0006 frame critique recorded and decision accepted.
- [x] Both slice frames reviewed; readiness advancement waits for prerequisites.

## 009-01

- [x] Witness new package/root/discovery tests fail.
- [x] Implement Copilot package, marketplace, prose adapter, locator, and guards.
- [x] Prove isolated installed discovery, helper behavior, and live skill use.
- [x] Run compliance, craft, architecture, and reconciliation reviews.
- [x] Reconcile documentation/memory and close slice DONE.

## 009-02

- [x] Witness new archive/release tests fail.
- [x] Implement archive, version, and release workflow integration.
- [x] Prove extracted-package discovery and helper behavior.
- [x] Run compliance, craft, architecture, and reconciliation reviews.
- [x] Reconcile documentation/memory and close slice DONE.

## Landing

- [x] Full unit suite, syntax, manifests, package drift, board and ADR index pass.
- [x] Provisional numbers remain free on fetched origin/main.
- [x] Scoped commits pushed; remote feature-branch head verified.
- [x] PR opened and interpreter-matrix CI state recorded.

### Landing result

[PR #6](https://github.com/ramboz/shaper/pull/6) is open against `main`.
Native PR creation succeeded on the resumed attempt after earlier HTTP 403
account failures. No global CLI account switch or browser login was performed.
The initial published head, `9538c18b345fdb1e5071d3a1e1d6feaed17bdeed`,
passed both GitHub CI interpreter jobs and the conventional-commit title gate.
See `evidence/pr-ci.json` for check URLs and timestamps.

Post-closeout checks also passed all 134 tests and local gates on actual
session-isolated Python 3.11.14 and 3.12.12, without changing global interpreters.
See `evidence/post-closeout-python-matrix.json`. The final landing-record commit
is checked again after push. The PR is intentionally not merged; release-please
still owns subsequent versioning and publication.
