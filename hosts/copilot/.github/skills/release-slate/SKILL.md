---
name: "release-slate"
description: "Read docs/releases/*.md release plans and write or refresh the compact docs/releases/README.md slate without creating a backlog or duplicating JIG lifecycle state."
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

# release-slate

Use this skill when a maintainer wants a compact view of release plans that
matter right now: candidate, committed, shipping, recently shipped, and
currently relevant dropped/no-go plans.

## Read boundary

Read only what is needed:

- `docs/releases/*.md` release plans, excluding `docs/releases/README.md`;
- the existing `docs/releases/README.md`, when present, to know this is an
  update rather than a first write;
- JIG handoff links already present inside each release plan's `## JIG Handoff`
  section.

Do not read `docs/specs/README.md` to copy lifecycle state into the slate. JIG
remains the source of truth for implementation status.

## Mutation boundary

- Write or update `docs/releases/README.md`.
- Do not edit release-plan files.
- Do not edit JIG files.
- Do not run `workflow.py transition`.
- Do not add priority ranks, backlog queues, roadmap sections, or copied JIG
  lifecycle/status columns.

## Slate shape

Keep the slate small and current. It must contain these sections:

- `Candidate`
- `Committed`
- `Shipping`
- `Shipped`
- `Dropped`

Each entry links to the release plan and may include JIG handoff links from the
release plan. Keep the note short; do not copy the full release plan, release
criteria, cutline table, or JIG status-board state.

Dropped plans belong only while they still explain a current no-go or release
decision. If an old idea is present only as a stale row in the existing slate
and no release-plan file backs it, remove it.

For the deterministic first pass, run:

```bash
python3 "$SHAPER_ROOT/skills/release-slate/scripts/release_slate.py" --repo <repo>
```

The helper discovers release plans, rewrites `docs/releases/README.md`, and
prints whether an existing slate was read.

## Graceful empty state

If no release plans exist, create `docs/releases/README.md` with the standard
sections, `_None yet_` rows, and a short empty-state note. Do not invent
example work.

## Output shape

End with:

- slate path;
- number of release plans discovered;
- whether an existing slate was read;
- confirmation that JIG lifecycle state was not copied.
