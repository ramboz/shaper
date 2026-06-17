> Status: Draft (elicited)
>
> Captures *why* this project exists, *for whom*, and *with what
> principles*. Architectural mechanics live in [architecture.md](architecture.md).
> Update via reconciliation, or via `/jig:vision-elicitation`.

# Vision: shaper

## Identity

<!-- elicited: 2026-06-17 / status: filled -->

- **Vision statement:** shaper is a small sibling plugin to JIG and servo. It brings Shape Up-style release shaping to AI-native projects: appetite, shaped bets, release cutlines, MVP/v1/v2 boundaries, risk retirement, and roadmap overlays.
- **Tagline** *(optional)*: shaper gives raw intent a buildable release shape before implementation starts.
- **Positioning story** *(optional)*:
  - JIG guides work accurately.
  - Servo measures and corrects feedback loops.
  - Shaper gives raw intent a buildable release shape before implementation starts.
  - shaper sits before and above JIG specs: it shapes raw product intent into bounded release bets, then hands implementation-ready work to JIG.

## Target users

<!-- elicited: 2026-06-17 / status: filled -->

- **For:**
  - AI-native project maintainers who need release appetite, shaped bets, release cutlines, MVP/v1/v2 boundaries, risk retirement, and roadmap overlays.
  - Users of JIG who need to shape raw product intent before creating implementation-ready specs.
  - Users of servo who may consume release-readiness signals, but do not want shaper to run loops or define quality oracles itself.
  - Solo maintainers or small teams who want repo-native Markdown first.
- **Not for:**
  - No task board.
  - No sprint planner.
  - No estimation engine.
  - No replacement for GitHub Projects, Linear, Jira, or issues.
  - No implementation workflow; JIG owns that.
  - No oracle/eval loop; servo owns that.
  - No web UI in the initial product.
  - No heavyweight agile framework.

## Core problem

<!-- elicited: 2026-06-17 / status: filled -->

- **Problem (2-3 sentences):** In AI-assisted projects, specs can multiply and scope can creep until nobody knows where MVP, v1, or v2 should be cut. The project needs a lightweight, repo-native release-shaping layer that helps decide what the release appetite is, what is in MVP/v1/v2, what is explicitly out, which risks need to be retired before implementation, which specs are tempting but deferred, and when this release is shippable enough.
- **Today's paths and where they fall short:**
  - Jumping straight to JIG specs - JIG owns supervised spec-driven development, but shaper sits before and above JIG specs.
  - Using servo signals as the planning layer - servo owns eval-driven and unattended agent loops, but shaper may consume servo signals for release readiness and must not run loops or define quality oracles itself.
  - Using task boards, sprint planners, estimation engines, GitHub Projects, Linear, Jira, or issues - shaper is not a replacement for those systems and should not become a heavyweight agile framework.
- **Originating incident / audit** *(optional)*: specs can multiply and scope can creep until nobody knows where MVP, v1, or v2 should be cut.

## Competitive landscape

<!-- elicited: 2026-06-17 / status: filled -->

| Option | What it does | Where it falls short for this gap |
|---|---|---|
| JIG | Supervised spec-driven development: product vision, architecture, ADRs, SPIDR slicing, spec lifecycle, independent review, and slice landing. | shaper must not replace or duplicate it; shaper sits before and above JIG specs. |
| servo | Eval-driven and unattended agent loops: project-specific oracles, quality gates, agent loops, hooks, variant races, and scheduled heartbeat discovery. | shaper may consume servo signals for release readiness, but it must not run loops or define quality oracles itself. |
| GitHub Projects, Linear, Jira, or issues | Task/status management. | shaper is not a task board, sprint planner, estimation engine, or replacement for issue systems. |
| Heavyweight agile frameworks | Planning process and scope ceremony. | shaper should be lightweight, repo-native, Markdown first, and Shape Up-inspired. |
| Ad-hoc roadmap documents | Easy to start and flexible. | They can become duplicating status boards instead of non-duplicating overlays that point to JIG specs. |

**Where this project fits:** shaper brings Shape Up-style release shaping to AI-native projects before implementation starts, then hands implementation-ready work to JIG.

## Scope

<!-- elicited: 2026-06-17 / status: filled -->

### Core features (prioritized)

1. A shaped-bet Markdown template.
2. A `shape-bet` skill that elicits outcome, appetite, must-haves, no-goes, risks, and release criteria.
3. A `cutline` skill that reads existing JIG specs/status board and proposes MVP/v1/v2 include/defer groupings without mutating them.
4. A non-duplicating roadmap/bets overlay.
5. Clear docs explaining how shaper sits beside JIG and servo.

### Tiers / phases *(optional)*

- MVP: one useful vertical slice over a complete agile system.
- v1: maintain a non-duplicating roadmap overlay that points to JIG specs rather than restating their status.
- v2: release-readiness and scope-audit skills that can consume JIG status and optional servo quality signals.

### MVP scope

- A shaped-bet Markdown template.
- A `shape-bet` skill that elicits outcome, appetite, must-haves, no-goes, risks, and release criteria.
- A `cutline` skill that reads existing JIG specs/status board and proposes MVP/v1/v2 include/defer groupings without mutating them.
- A non-duplicating roadmap/bets overlay.
- Clear docs explaining how shaper sits beside JIG and servo.

### Out of scope (deliberately)

- No task board.
- No sprint planner.
- No estimation engine.
- No replacement for GitHub Projects, Linear, Jira, or issues.
- No implementation workflow; JIG owns that.
- No oracle/eval loop; servo owns that.
- No web UI in the initial product.
- No heavyweight agile framework.
- No silent mutation of JIG spec states.

## Stack

<!-- elicited: 2026-06-17 / status: filled -->

- **Runtime / language:** Probably python (python3) as we want this consistent with `/Users/ramboz/Projects/misc/jig` and `/Users/ramboz/Projects/misc/servo`.
- **Platform commitments:**
  - Cloud target: none for the initial product.
  - Deployment shape: plugin surfaces for Claude Code and Codex where practical.
  - Package manager: deferred until implementation needs packaging.
  - Database: none; repo-native Markdown first.
  - Key external services: JIG docs/specs/status board, optional servo quality signals.
- **Locked-in vs. still open:** repo-native Markdown first, soft coupling to JIG and servo, and no web UI in the initial product are locked in. Package manager and exact plugin packaging are still open.

## Design principles & constraints

<!-- elicited: 2026-06-17 / status: filled -->

1. Repo-native Markdown first.
2. Advisory but forceful: shaper should make scope tradeoffs explicit.
3. Non-duplicating overlays: do not create a second status board.
4. Appetite before backlog.
5. Fixed time / variable scope bias, inspired by Shape Up.
6. Risk retirement before implementation: research spikes and architecture decisions should happen early when they unblock the release path.
7. Cross-host from the start: support both Claude Code and Codex plugin surfaces where practical.
8. Soft coupling to JIG and servo: detect them if present, degrade gracefully if not.

**Non-obvious constraints:** No silent mutation of JIG spec states. shaper can recommend transitions and generate patch-ready instructions, but JIG remains the source of truth for spec lifecycle state.

## How new work enters

<!-- elicited: 2026-06-17 / status: filled -->

- **Prioritization model:** Appetite before backlog. Fixed time / variable scope bias, inspired by Shape Up.
- **Spec-triggering rules:**
  - A raw product intent needs a buildable release shape before implementation starts.
  - MVP/v1/v2 leakage appears.
  - A risk needs to be retired before implementation.
  - Existing JIG specs or slices need release cutline include/defer recommendations.
  - A release needs to be judged shippable enough using JIG status and optional servo quality signals.

## Open questions

<!-- elicited: 2026-06-17 / status: filled -->

- What is the exact artifact model for shaped bets: `docs/bets/mvp.md`, `docs/bets/v1.md`, `docs/bets/v2.md`, or another shape?
- Should shaper ship a dedicated `docs/bets/README.md` roadmap overlay, or should each bet carry its own include/defer cutline?
- How much JIG/servo detection belongs in the MVP versus later release-readiness work?
- What should "patch-ready instructions" look like when shaper recommends JIG spec state transitions without mutating them?
