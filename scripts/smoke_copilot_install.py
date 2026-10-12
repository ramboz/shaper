"""Optional real-CLI install/discovery/helper probe; never runs in ordinary CI.

Retains disposable fixtures for a separate authenticated live session. Prints
JSON evidence to stdout; never touches the user's normal Copilot configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from build_host_packages import _file_map
from shaper_root import SKILLS


ROOT = Path(__file__).resolve().parent.parent


def discovered_skills(data: object, package: Path) -> dict[str, Path]:
    if not isinstance(data, list):
        raise RuntimeError("skill discovery: CLI JSON must be a list")
    found = {}
    for row in data:
        if not isinstance(row, dict) or row.get("name") not in SKILLS:
            continue
        name = row["name"]
        expected = (package / ".github/skills" / name).resolve()
        if (row.get("source") != "plugin" or row.get("enabled") is not True
                or not isinstance(row.get("path"), str) or Path(row["path"]).resolve() != expected
                or name in found):
            raise RuntimeError(f"skill discovery: invalid/disabled/duplicate plugin skill {name}")
        found[name] = expected
    if set(found) != set(SKILLS):
        raise RuntimeError(f"skill discovery: missing {sorted(set(SKILLS) - set(found))}")
    return found


def run(command: list[str], cwd: Path, env: dict, evidence: list) -> str:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=120)
    record = {"command": command, "cwd": str(cwd), "exit_code": result.returncode}
    if result.returncode:
        record["error"] = result.stderr.strip() or result.stdout.strip()
    evidence.append(record)
    if result.returncode:
        raise RuntimeError(f"{shlex.join(command)}: {record['error']}")
    return result.stdout


def fixture_files(consumer: Path) -> dict[str, str]:
    fixtures = {
        "docs/specs/README.md": "# Spec Status Board\n\n| Spec | Slice | Status | Notes |\n"
        "|---|---|---|---|\n| [010-probe](010-probe/spec.md) | 010-01 | DONE | |\n",
        "docs/specs/010-probe/spec.md": "---\nstatus: DONE\n---\n# Probe\nSmall probe.\n",
        "docs/servo/release-signals/probe.md": "---\nstatus: pass\n---\n# Signal\nGood.\n",
    }
    for rel, content in fixtures.items():
        path = consumer / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return {rel: hashlib.sha256((consumer / rel).read_bytes()).hexdigest() for rel in fixtures}


def helper_probe(skills: dict[str, Path], consumer: Path, env: dict) -> dict:
    before = fixture_files(consumer)
    commands = []
    for name in SKILLS:
        skill = skills[name]
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"```bash\n(SHAPER_ROOT=.*?)\n```", text, re.S)
        if match is None:
            raise RuntimeError(f"missing documented root bootstrap: {name}")
        helper = f'python3 "$SHAPER_ROOT/skills/{name}/scripts/{name.replace("-", "_")}.py"'
        if helper not in text:
            raise RuntimeError(f"missing documented helper: {name}")
        args = ["--repo", "."]
        if name == "shape-release":
            args += ["--slug", "probe", "--problem", "Need a probe", "--appetite", "One day",
                     "--solution", "Small probe", "--vertical-scope", "Create a useful plan",
                     "--risk", "None identified", "--no-go", "No automation",
                     "--jig-handoff", "[Probe](../specs/010-probe/spec.md)",
                     "--criterion", "Helper works"]
        elif name != "release-slate":
            args += ["--release", "probe"]
        command = match[1] + "\n" + helper + " " + shlex.join(args)
        output = run(["bash", "-c", command], consumer,
                     {**env, "SHAPER_SKILL_DIR": str(skill)}, commands)
        # Keep exact executed commands; this is deterministic helper use,
        # never an authenticated live-agent transcript.
        commands[-1]["bootstrap_from"] = str(skill / "SKILL.md")
        commands[-1]["SHAPER_SKILL_DIR"] = str(skill)
        if name in ("cutline", "scope-audit", "release-check"):
            token = {"cutline": "include", "scope-audit": "advisory",
                     "release-check": "recommendation"}[name]
            if token not in output.lower():
                raise RuntimeError(f"missing {name} advice")
        commands[-1]["result"] = output.strip().splitlines()[-1]
    after = {rel: hashlib.sha256((consumer / rel).read_bytes()).hexdigest() for rel in before}
    if after != before:
        raise RuntimeError("JIG/servo fixtures changed")
    plan = (consumer / "docs/releases/probe.md").read_text(encoding="utf-8")
    if "### Architecture appetite" not in plan or "Create a useful plan" not in plan:
        raise RuntimeError("bundled template lookup or plan creation failed")
    if "probe.md" not in (consumer / "docs/releases/README.md").read_text(encoding="utf-8"):
        raise RuntimeError("release slate refresh failed")
    return {"commands": commands, "fixture_sha256_before_and_after": before,
            "jig_servo_unchanged": True, "bundled_template": True,
            "artifacts": ["docs/releases/probe.md", "docs/releases/README.md"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--copilot", default="copilot", help="CLI executable; must already be available")
    args = parser.parse_args(argv)
    cli = shutil.which(args.copilot)
    if cli is None:
        parser.error("Copilot CLI unavailable; required probe cannot be skipped")
    base = Path(tempfile.mkdtemp(prefix="shaper installed probe ")).resolve()
    package = base / "marketplace/hosts/copilot"
    shutil.copytree(ROOT / "hosts/copilot", package)
    marketplace = base / "marketplace/.github/plugin"
    marketplace.mkdir(parents=True)
    shutil.copy2(ROOT / ".github/plugin/marketplace.json", marketplace)
    evidence = {"fixture": str(base), "live_session": "not run; separate parent-owned AC5",
                "installs": []}
    try:
        for mode in ("marketplace", "direct"):
            consumer = base / mode / "consumer"
            consumer.mkdir(parents=True)
            home = base / mode / "home"
            env = {**os.environ, "COPILOT_HOME": str(home),
                   "PATH": str(Path(cli).parent) + os.pathsep + os.environ.get("PATH", "")}
            env.pop("SHAPER_SKILL_DIR", None)
            install = {"mode": mode, "COPILOT_HOME": str(home), "consumer": str(consumer), "commands": []}
            evidence["installs"].append(install)
            commands = install["commands"]
            evidence["cli_version"] = run([cli, "--version"], consumer, env, commands).splitlines()[0]
            if mode == "marketplace":
                run([cli, "plugin", "marketplace", "add", str(base / "marketplace")], consumer, env, commands)
                source = "shaper@shaper"
            else:
                source = str(package)
            install["installation_result"] = run([cli, "plugin", "install", source], consumer, env, commands).strip()
            installed = package
            if mode == "direct":
                copies = [path.parent.parent for path in (home / "installed-plugins").glob("*/*/.plugin/plugin.json")
                          if _file_map(path.parent.parent) == _file_map(package)]
                if len(copies) != 1:
                    raise RuntimeError("direct installation: no unique byte-identical installed package")
                installed = copies[0]
            install["installed_package"] = str(installed)
            install["payload_byte_identical"] = _file_map(installed) == _file_map(package)
            data = json.loads(run([cli, "skill", "list", "--json"], consumer, env, commands))
            skills = discovered_skills(data, installed)
            install["discovered"] = {name: str(path) for name, path in sorted(skills.items())}
            install["helpers"] = helper_probe(skills, consumer, env)
        evidence["result"] = "pass"
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        evidence.update(result="fail", error=str(exc))
    print(json.dumps(evidence, indent=2))
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
