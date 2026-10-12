---
name: "cutline"
description: "Read a release plan plus JIG specs/status when present, then recommend include, defer, split, and risk-first boundaries without mutating JIG lifecycle state."
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

# cutline

Use this skill when a maintainer has a release plan and wants a non-mutating
cutline across existing JIG work.

## Read boundary

Read only what is needed:

- the target `docs/releases/<slug>.md` release plan;
- `docs/specs/README.md`, when present;
- relevant `docs/specs/*` files, when present;
- `docs/product-vision.md` and `docs/architecture.md` only when the release
  boundary is unclear.

If `docs/specs/README.md` and relevant `docs/specs/*` files are absent, report
"No JIG specs/status board were found" and still provide release-plan-only
guidance. Leave JIG files untouched.

## Mutation boundary

- This is a non-mutating analysis skill for JIG artifacts.
- It must not edit JIG spec lifecycle state.
- It must not run `workflow.py transition`.
- It must not rewrite `docs/specs/README.md` or any `docs/specs/*` lifecycle
  field.
- It may update the release plan's `## Cutline` section only when the user asks
  for the cutline to be written back. Even then, leave JIG files untouched.

## Recommendation format

Classify each relevant item as one of:

- `include`: belongs inside the current appetite and release criteria;
- `defer`: useful but outside the current appetite or no-gos;
- `split`: too large or mixed; needs a smaller release-facing slice;
- `risk-first`: should not move to implementation until the risk/rabbit hole is
  retired.

Use this table when writing or reporting recommendations:

| Item | Evidence read | Recommendation | Rationale | Non-mutating JIG handoff |
|---|---|---|---|---|
| _spec/slice/idea_ | _release plan + JIG evidence_ | _include/defer/split/risk-first_ | _why_ | _draft/review instructions only_ |

Do not copy JIG lifecycle status into the release slate or turn the output into
a second status board. Link to JIG specs/slices when useful and explain the
release boundary in plain language.

For a deterministic first pass, run:

```bash
python3 "$SHAPER_ROOT/skills/cutline/scripts/cutline.py" --repo <repo> --release <slug>
```

The helper reads `docs/specs/README.md` and linked spec files when present,
prints include/defer/split/risk-first tables, and never writes to JIG files.
Use agent judgment to refine the rationale before writing recommendations back
to a release plan.

## Graceful degradation

- If no JIG specs/status board were found, say so and produce only
  release-plan-based recommendations.
- If servo signals are absent, do not block. This slice does not consume servo
  release-check signals.
- If a release plan is missing appetite, no-gos, or risks/rabbit holes, flag
  that gap before making confident include/defer calls.

## Output shape

End with:

- release plan inspected;
- JIG files read, or the no-JIG message;
- include/defer/split/risk-first recommendations;
- risks that must be retired before implementation;
- confirmation that JIG files were left untouched.
