# Spec 009 implementation plan

Support Copilot CLI with the corrected JIG third-host mechanism while leaving
product behavior and existing host adapters unchanged.

## Delivery order

1. Frame critique and accept ADR-0006. Review both slice frames and move them
   to READY_FOR_REVIEW. Advance each to READY_FOR_IMPLEMENTATION only after its
   Definition of Ready prerequisites hold.
2. Implement 009-01 with tests first: third package, marketplace, installed-root
   resolution, loader/manifest guards, drift, install docs, and real installed
   discovery/helper/live-session evidence. Review and reconcile to DONE.
3. Implement 009-02 with tests first: archive validation, version/release wiring,
   extracted-directory install proof, distribution docs. Review/reconcile to DONE.
4. Audit derived boards/index, run all local gates, verify provisional numbering
   against fetched origin/main, commit/push this feature branch, and open a PR.

## Constraints

- Standard-library Python and existing unittest/tooling contracts.
- Copilot-only render changes; no common runtime import from the sibling JIG.
- Keep target repository paths separate from installed runtime paths.
- No new product hooks, agents, scaffolder, project instructions, or version owner.
- Do not edit conventions or immutable prior ADR/spec records.
- Live Copilot probes use disposable consumer directories and isolated
  `COPILOT_HOME`; never modify the user's normal plugin configuration.
- Record local installation, authenticated live execution, and release/remote
  publication separately; do not substitute one for another.

## Review gates

ADR frame critique; per-slice frame review, compliance, craft, architecture,
and reconciliation. Every required verdict is recorded with `review.py`;
all lifecycle transitions use `workflow.py` without bypass flags.
