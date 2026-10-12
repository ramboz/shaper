"""Locate a complete, manifest-identified Shaper Copilot runtime (stdlib only).

The disclosed active skill takes precedence, even over a newer installation.
Otherwise search COPILOT_HOME's marketplace and _direct install directories.
Never infer runtime paths from the consuming repository.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


SKILLS = ("shape-release", "cutline", "release-slate", "scope-audit", "release-check")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def runtime_manifest(root: Path) -> dict | None:
    try:
        data = json.loads((root.parent / ".plugin/plugin.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("name") != "shaper":
        return None
    if data.get("skills") != ".github/skills" or root.name != ".github":
        return None
    version = data.get("version")
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        return None
    required = ["templates/release-plan.md", "scripts/shaper_root.py"]
    for name in SKILLS:
        required.extend((f"skills/{name}/SKILL.md",
                         f"skills/{name}/scripts/{name.replace('-', '_')}.py"))
    return data if all((root / rel).is_file() for rel in required) else None


def resolve(active_skill: Path | None = None) -> Path | None:
    active = active_skill or os.environ.get("SHAPER_SKILL_DIR")
    if active:
        skill = Path(active).resolve()
        if skill.name == "SKILL.md":
            skill = skill.parent
        root = skill.parent.parent
        if skill.name in SKILLS and skill.parent.name == "skills" and runtime_manifest(root):
            return root
        return None
    home = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot")
    candidates = []
    for root in (home / "installed-plugins").glob("*/*/.github"):
        manifest = runtime_manifest(root)
        if manifest:
            version = tuple(int(part) for part in manifest["version"].split("."))
            candidates.append((version, str(root.resolve()), root.resolve()))
    return max(candidates)[2] if candidates else None


def main(argv: list[str]) -> int:
    root = resolve(Path(argv[1]) if len(argv) > 1 else None)
    if root is None:
        sys.stderr.write("shaper_root: no valid Shaper runtime; install shaper or check "
                         "COPILOT_HOME / SHAPER_SKILL_DIR.\n")
        return 1
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
