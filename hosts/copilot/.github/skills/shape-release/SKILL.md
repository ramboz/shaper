---
name: "shape-release"
description: "Create or refine a repo-native release plan in docs/releases/<slug>.md from raw product intent, appetite, no-gos, risks, release-check criteria, and JIG handoff notes."
user-invocable: true
---

## Installed runtime (Copilot CLI)

Run helpers from the consuming repository; `docs/` paths belong to that
repository, not this plugin. Python 3 is required. Do not copy runtime files.
If Copilot discloses this invoked skill's absolute directory, set
`SHAPER_SKILL_DIR` to that directory (the parent of its `SKILL.md`) in the
shell below; prefer it over other installations. Do not guess a project path.
Otherwise leave `SHAPER_SKILL_DIR` unset. This bootstrap honors `COPILOT_HOME`
(default `~/.copilot`), including marketplace and direct installs, and paths
with spaces. Run it in the same shell as each helper, including fresh shells:

```bash
SHAPER_ROOT="$(python3 - <<'PY'
import json
import os
import re
import sys
from pathlib import Path
skills = ('shape-release', 'cutline', 'release-slate', 'scope-audit', 'release-check')
def manifest(root):
    try:
        data = json.loads((root.parent / ".plugin/plugin.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if (not isinstance(data, dict) or data.get("name") != "shaper"
            or data.get("skills") != ".github/skills" or root.name != ".github"
            or not isinstance(data.get("version"), str)
            or not re.fullmatch(r"\d+\.\d+\.\d+", data["version"])):
        return None
    required = ["templates/release-plan.md", "scripts/shaper_root.py"]
    for name in skills:
        required.extend((f"skills/{name}/SKILL.md",
                         f"skills/{name}/scripts/{name.replace('-', '_')}.py"))
    return data if all((root / rel).is_file() for rel in required) else None
active = os.environ.get("SHAPER_SKILL_DIR")
roots = []
if active:
    skill = Path(active).resolve()
    if skill.name == "SKILL.md":
        skill = skill.parent
    if skill.name in skills and skill.parent.name == "skills":
        roots.append(skill.parent.parent)
else:
    home = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot")
    roots = (home / "installed-plugins").glob("*/*/.github")
candidates = []
for root in roots:
    data = manifest(root)
    if data:
        candidates.append((tuple(int(part) for part in data["version"].split(".")),
                           str(root.resolve()), root.resolve()))
if not candidates:
    sys.exit("shaper_root: no valid Shaper runtime; install shaper or check COPILOT_HOME / SHAPER_SKILL_DIR")
print(max(candidates)[2])
PY
)" || { echo "Shaper runtime unavailable; stop rather than use consumer-relative helpers." >&2; exit 1; }
export SHAPER_ROOT
```

`SHAPER_ROOT` is the absolute installed `.github` runtime. Keep every helper
and template path quoted. If resolution fails, stop explicitly; do not run
a similarly named file from the consuming repository.

# shape-release

Use this skill when a maintainer wants to turn rough product intent into a
bounded release plan before implementation work moves into JIG or another
spec-driven workflow.

## Boundaries

- Do not invent product intent. If a field is missing, ask for it or mark it as
  `TBD` in the release plan.
- Use the user's words where practical, especially for the problem, appetite,
  no-gos, risks/rabbit holes, and release-check criteria.
- Keep new plans in `candidate` status unless the user explicitly says the
  release is committed, shipping, shipped, or dropped.
- JIG owns implementation workflow and spec lifecycle. This skill may write JIG
  handoff notes, but it must not run lifecycle transitions or edit JIG status.
- Architecture appetite records appetite only, never architecture decisions
  (ADR-0005): capture investment posture, over-investment no-gos, and a spike
  pointer — nothing else. The investment posture is a strict **upper bound**
  ("at most" / "permitted up to"), never "at least" — never a floor or a minimum.
  This skill must not write an ADR, name a module boundary, name a mechanism,
  or specify any positive design — completing "the leanest architecture is X"
  is jig's decision, not this skill's, full stop. This ceiling is the
  prospective half; jig's leanness/YAGNI review lens is the retrospective
  complement, enforced at jig review, not here.
- If servo signals are absent, do not block. Record release-check criteria as
  desired future evidence rather than pretending signals exist.

## Inputs to gather

Read `"$SHAPER_ROOT/templates/release-plan.md"` first. Then elicit enough of these fields to
write or update `docs/releases/<slug>.md`:

- `status`: one of `candidate`, `committed`, `shipping`, `shipped`, `dropped`;
- `problem/baseline`: current state, problem, and why now;
- `appetite`: fixed time or attention budget and variable scope;
- `solution outline`: the smallest useful release shape;
- `vertical scopes`: the new work decomposed into an ordered list of thin,
  end-to-end vertical scopes, thinnest walking-skeleton path first (see
  "Vertical scope discipline" below);
- `risks/rabbit holes`: unknowns that could make the release unsafe or too
  large;
- `no-gos`: explicit exclusions;
- `cutline`: include, defer, split, and risk-first notes if known;
- `JIG handoff`: existing specs/slices to link or new specs to draft;
- `architecture appetite`: a leanness ceiling for the JIG handoff --
  investment posture (upper bound only), over-investment no-gos, and a spike
  pointer for architectural risk worth retiring early (see the architecture
  appetite entry in `## Boundaries`);
- `release-check criteria`: evidence that should be true before shipping.

Ask at most five focused questions at a time. If the user gives enough
information to start, write the plan and leave precise `TBD` markers for
unanswered fields.

## Vertical scope discipline

Each vertical scope must deliver end-to-end, demoable value on its own. A
scope that is "just the data model" or "just the parser" is a horizontal
slice, not a vertical one — re-split it until every scope crosses the whole
stack and something demoable comes out the other end. This mirrors JIG's
SPIDR anti-horizontal-phasing rule, applied one altitude higher (release
work, not spec slices).

## Writing or refining a plan

1. Choose a short kebab-case slug from the user's language.
2. Create `docs/releases/` if needed.
3. Write or update `docs/releases/<slug>.md` using
   `"$SHAPER_ROOT/templates/release-plan.md"`. For deterministic create/refine work, use
   `python3 "$SHAPER_ROOT/skills/shape-release/scripts/shape_release.py" --repo <repo> --slug <slug>`
   with the fields the user supplied; leave omitted fields as `TBD`.
4. Write the vertical-scope decomposition into the "Vertical Scopes (delivery
   order)" subsection of `## Solution Outline`, ordered thinnest-demoable-path
   first (use `--vertical-scope` on the script, repeatable, once per scope in
   delivery order). If scopes are omitted, leave the `TBD` marker in place —
   never a fabricated ordering.
5. Preserve existing user-authored wording when refining a plan. Prefer
   appending clarifying bullets over rewriting the user's intent; the same
   applies to vertical scopes — append new ones after existing ones rather
   than overwriting them.
6. Keep the JIG handoff non-mutating: link to specs/slices or propose new JIG
   work, but leave JIG files untouched unless the user separately asks to edit
   a release plan's handoff notes.
7. Write the architecture-appetite subsection into `## JIG Handoff` using
   `--arch-posture`, `--arch-no-go` (repeatable), and `--arch-spike` on the
   script. Leave the `_TBD_` markers in place when a maintainer gives none --
   never fabricate a posture, no-go, or spike, and never fill in what the
   leanest architecture would be; that decision belongs to jig.
8. Call out any absent sibling tools plainly. For example, if servo signals are
   absent, write "No servo signals were found; release-check criteria remain
   advisory."

## Output shape

End with a short summary:

- release plan path;
- status;
- appetite;
- unresolved questions;
- JIG handoff next step;
- whether any servo signals were absent.
