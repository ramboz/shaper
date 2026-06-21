> Status: Draft (elicited)
>
> Captures *why* this project exists, *for whom*, and *with what
> principles*. Architectural mechanics live in [architecture.md](architecture.md).
> Update via reconciliation, or via `/jig:vision-elicitation`.

# Vision: shaper

## Identity

<!-- elicited: 2026-06-17 / status: filled -->

- **Vision statement:** shaper is a small sibling plugin to JIG and servo. It
  brings lightweight release and milestone shaping to AI-native projects:
  release plans, appetite, cutlines, explicit no-gos, risk retirement, scope
  audits, release slates, and release checks.
- **Tagline** *(optional)*: shaper gives raw intent a buildable release shape
  before implementation starts.
- **Positioning story** *(optional)*:
  - JIG guides work accurately.
  - Servo measures and corrects feedback loops.
  - Shaper gives raw intent a buildable release shape before implementation
    starts.
  - shaper sits before and above JIG specs: it shapes raw product intent into a
    bounded release plan, then hands implementation-ready work to JIG.

## Target users

<!-- elicited: 2026-06-17 / status: filled -->

- **For:**
  - AI-native project maintainers who need release appetite, cutlines, release
    boundaries, risk retirement, scope audits, and release checks.
  - Users of JIG who need to shape raw product intent before creating
    implementation-ready specs.
  - Users of servo who may later consume release-quality signals, but do not
    want shaper to run loops or define quality oracles itself.
  - Solo maintainers or small teams who want repo-native Markdown first.
- **Not for:**
  - No task board.
  - No sprint planner.
  - No estimation engine.
  - No backlog groomer.
  - No replacement for GitHub Projects, Linear, Jira, or issues.
  - No implementation workflow; JIG owns that.
  - No oracle/eval loop; servo owns that.
  - No web UI in the initial product.
  - No heavyweight agile framework.

## Core problem

<!-- elicited: 2026-06-17 / status: filled -->

- **Problem (2-3 sentences):** In AI-assisted projects, specs can multiply and
  scope can creep until nobody knows what belongs in the current release, what
  should be deferred, and what risks must retire before implementation starts.
  The project needs a lightweight, repo-native release-shaping layer that helps
  decide the appetite, write a release plan, draw a cutline against JIG work,
  and decide whether to ship, cut scope, stop, or re-shape.
- **Today's paths and where they fall short:**
  - Jumping straight to JIG specs - JIG owns supervised spec-driven
    development, but shaper sits before and above JIG specs.
  - Using servo signals as the planning layer - servo owns eval-driven and
    unattended agent loops, but shaper may consume servo signals for release
    checks and must not run loops or define quality oracles itself.
  - Using task boards, sprint planners, estimation engines, GitHub Projects,
    Linear, Jira, or issues - shaper is not a replacement for those systems and
    should not become a heavyweight agile framework.
- **Originating incident / audit** *(optional)*: specs can multiply and scope
  can creep until nobody knows what is in the current release, what is
  explicitly out, and what is merely tempting.

## Competitive landscape

<!-- elicited: 2026-06-17 / status: filled -->

| Option | What it does | Where it falls short for this gap |
|---|---|---|
| JIG | Supervised spec-driven development: product vision, architecture, ADRs, SPIDR slicing, spec lifecycle, independent review, and slice landing. | shaper must not replace or duplicate it; shaper sits before and above JIG specs. |
| servo | Eval-driven and unattended agent loops: project-specific oracles, quality gates, agent loops, hooks, variant races, and scheduled heartbeat discovery. | shaper may consume servo signals for release checks, but it must not run loops or define quality oracles itself. |
| GitHub Projects, Linear, Jira, or issues | Task/status management. | shaper is not a task board, sprint planner, estimation engine, backlog groomer, or replacement for issue systems. |
| Heavyweight agile frameworks | Planning process and scope ceremony. | shaper should be lightweight, repo-native, Markdown first, and Shape Up-inspired without requiring users to know Shape Up vocabulary. |
| Ad-hoc roadmap documents | Easy to start and flexible. | They can become duplicating status boards or evergreen backlogs instead of compact release slates. |

**Where this project fits:** shaper brings Shape Up-inspired release shaping to
AI-native projects before implementation starts, then hands implementation-ready
work to JIG.

## Scope

<!-- elicited: 2026-06-17 / status: filled -->

### Core features (prioritized)

1. A release-plan Markdown template.
2. A `shape-release` skill that elicits problem/baseline, appetite, solution
   outline, risks/rabbit holes, no-gos, release criteria, and JIG handoff.
3. A `cutline` skill that reads existing JIG specs/status board and proposes
   include/defer/split/risk-first recommendations without mutating them.
4. A compact `release-slate` overlay that tracks active release plans without
   becoming a backlog.
5. Clear docs explaining how shaper sits beside JIG and servo.
6. Later `scope-audit` and `release-check` skills.

### Tiers / phases *(optional)*

- First product slice: one useful release-plan-to-JIG handoff loop.
- Next: release-slate overlay.
- Later: scope-audit and release-check skills that can consume JIG status and,
  after a future ADR, optional servo quality signals.

### First product slice

- A release-plan Markdown template.
- A `shape-release` skill that elicits problem/baseline, appetite, solution
  outline, risks/rabbit holes, no-gos, release criteria, and JIG handoff.
- A `cutline` skill that reads existing JIG specs/status board and proposes
  include/defer/split/risk-first recommendations without mutating them.
- A compact `docs/releases/README.md` release slate.
- Clear docs explaining how shaper sits beside JIG and servo.

### Out of scope (deliberately)

- No task board.
- No sprint planner.
- No estimation engine.
- No backlog grooming.
- No replacement for GitHub Projects, Linear, Jira, or issues.
- No implementation workflow; JIG owns that.
- No oracle/eval loop; servo owns that.
- No web UI in the initial product.
- No heavyweight agile framework.
- No silent mutation of JIG spec states.

## Stack

<!-- elicited: 2026-06-17 / status: filled -->

- **Runtime / language:** Python 3 for helper scripts, consistent with
  `/Users/ramboz/Projects/misc/jig` and `/Users/ramboz/Projects/misc/servo`.
- **Platform commitments:**
  - Cloud target: none for the initial product.
  - Deployment shape: plugin surfaces for Claude Code and Codex where practical.
  - Package manager: none yet; standard-library Python is enough for the
    current helper surface.
  - Database: none; repo-native Markdown first.
  - Key external services: JIG docs/specs/status board, optional servo quality
    signals from `docs/servo/release-signals/<slug>.md` under ADR-0004's
    read-only boundary.
- **Locked-in decisions:** repo-native Markdown first, soft coupling to JIG and
  servo, no web UI, the hybrid plugin baseline, host-explicit release archives,
  the release-plan/no-backlog-slate artifact model, and ADR-0004's JIG/servo
  release-signal boundary. The current implementation also uses
  standard-library `unittest` and `.jig` test/lint commands. No stack decision
  is open for the current product surface.

## Design principles & constraints

<!-- elicited: 2026-06-17 / status: filled -->

1. Repo-native Markdown first.
2. Advisory but forceful: shaper should make scope tradeoffs explicit.
3. Non-duplicating overlays: do not create a second status board.
4. Appetite before backlog.
5. Fixed time / variable scope bias, inspired by Shape Up.
6. Release plans before implementation: shaping produces a bounded release
   plan; JIG owns the implementation workflow.
7. Risk retirement before implementation: research spikes and architecture
   decisions should happen early when they unblock the release path.
8. Cross-host from the start: support both Claude Code and Codex plugin
   surfaces where practical.
9. Soft coupling to JIG and servo: detect them if present, degrade gracefully if
   not.

**Non-obvious constraints:** No silent mutation of JIG spec states. shaper can
recommend transitions and generate patch-ready instructions, but JIG remains
the source of truth for spec lifecycle state.

## How new work enters

<!-- elicited: 2026-06-17 / status: filled -->

- **Prioritization model:** Appetite before backlog. Fixed time / variable scope
  bias, inspired by Shape Up.
- **Spec-triggering rules:**
  - A raw product intent needs a buildable release plan before implementation
    starts.
  - A release plan needs JIG handoff.
  - Scope leakage appears against the appetite or cutline.
  - A risk or rabbit hole needs to be retired before implementation.
  - Existing JIG specs or slices need release cutline include/defer/split
    recommendations.
  - A release needs a release check using JIG status and optional servo quality
    signals.

## Resolved Questions

<!-- elicited: 2026-06-17 / status: filled -->

- **JIG detection depth:** Spec 002 shipped shallow status-board and linked-spec
  reads for cutline/handoff. Spec 006 added scope-audit's broader advisory
  checks without mutating JIG lifecycle state.
- **Servo evidence boundary:** ADR-0004 and Spec 007 slice 02 limit
  `release-check` to optional read-only
  `docs/servo/release-signals/<slug>.md` artifacts. Missing or malformed servo
  evidence degrades to "not evaluated".
- **Patch-ready JIG guidance:** `cutline`, `scope-audit`, and `release-check`
  may recommend include/defer/split/risk-first or release decisions with
  evidence and rationale, but they do not run JIG transitions or edit lifecycle
  status.
