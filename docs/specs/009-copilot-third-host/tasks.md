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
- [ ] PR opened and interpreter-matrix CI state recorded.

### Landing blocker

The app's native PR creation failed with GitHub HTTP 403: its Enterprise
Managed User connection cannot access `ramboz/shaper`. The personal CLI account
is already `ramboz`, and no PR exists for `copilot-third-host`. The implementation
and all JIG slice gates are complete and pushed; app GitHub identity selection
must be corrected before native PR creation and PR-triggered CI can finish.

Post-closeout checks also passed all 134 tests and local gates on actual
session-isolated Python 3.11.14 and 3.12.12, without changing global interpreters.
See `evidence/post-closeout-python-matrix.json`. The browser route required login.
A documented SDK session-only personal-identity override was verified and then
restored, but the app's native PR API still used its Enterprise Managed User
connection. This requires an app-level account selection, not a CLI auth switch.
