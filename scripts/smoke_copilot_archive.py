"""Optional real extracted-archive install probe; not an authenticated CI gate."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from build_host_packages import _file_map
from build_release_zip import smoke_test
from smoke_copilot_install import discovered_skills, helper_probe, run


def probe(archive: Path, cli: str, base: Path) -> dict:
    """Use the installed-package boundary helpers, adding archive/refine proof."""
    evidence = {"archive": str(archive.resolve()), "fixture": str(base),
                "commands": [], "publication": "not performed",
                "live_agent_session": "not performed; deterministic installed helpers only"}
    commands = evidence["commands"]
    try:
        out = io.StringIO()
        if smoke_test("copilot", archive, out=out):
            raise RuntimeError(out.getvalue().strip())
        evidence["archive_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        package = base / "extracted/shaper"
        package.mkdir(parents=True)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(package)
        consumer = base / "consumer"
        consumer.mkdir()
        home = base / "home"
        env = {**os.environ, "COPILOT_HOME": str(home)}
        env.pop("SHAPER_SKILL_DIR", None)
        evidence.update(consumer=str(consumer), COPILOT_HOME=str(home),
                        extracted_package=str(package))
        evidence["cli_version"] = run([cli, "--version"], consumer, env, commands).splitlines()[0]
        evidence["installation_result"] = run(
            [cli, "plugin", "install", str(package)], consumer, env, commands
        ).strip()
        copies = [
            path.parent.parent
            for path in (home / "installed-plugins").glob("*/*/.plugin/plugin.json")
            if _file_map(path.parent.parent) == _file_map(package)
        ]
        if len(copies) != 1:
            raise RuntimeError("no unique byte-identical installed archive payload")
        installed = copies[0]
        evidence.update(installed_package=str(installed), payload_byte_identical=True)
        data = json.loads(run([cli, "skill", "list", "--json"], consumer, env, commands))
        skills = discovered_skills(data, installed)
        evidence["discovered"] = {name: {"path": str(path), "enabled": True}
                                  for name, path in sorted(skills.items())}
        evidence["helpers"] = helper_probe(skills, consumer, env)
        # Retain command provenance without repeating each long, identical
        # documented bootstrap in the release evidence.
        for record in evidence["helpers"]["commands"]:
            shell = record.pop("command")[2]
            record["helper_command"] = shell.splitlines()[-1]
            record["shell_command_sha256"] = hashlib.sha256(shell.encode()).hexdigest()
        before = evidence["helpers"]["fixture_sha256_before_and_after"]
        evidence["fixture_sha256_before"] = before
        runtime = installed / ".github"
        run([sys.executable, str(runtime / "skills/shape-release/scripts/shape_release.py"),
             "--repo", ".", "--slug", "probe", "--solution", "Refined archive plan"],
            consumer, env, commands)
        plan = (consumer / "docs/releases/probe.md").read_text(encoding="utf-8")
        if "Refined archive plan" not in plan or "Create a useful plan" not in plan:
            raise RuntimeError("installed plan refinement did not preserve vertical scope")
        evidence["refined_plan"] = True
        run([sys.executable, str(runtime / "skills/release-slate/scripts/release_slate.py"),
             "--repo", "."], consumer, env, commands)
        if "probe.md" not in (consumer / "docs/releases/README.md").read_text(encoding="utf-8"):
            raise RuntimeError("refined release slate missing plan")
        after = {rel: hashlib.sha256((consumer / rel).read_bytes()).hexdigest() for rel in before}
        evidence["fixture_sha256_after"] = after
        if after != before:
            raise RuntimeError("JIG/servo fixtures changed after refinement/slate")
        evidence.update(result="pass", jig_servo_unchanged=True)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        evidence.update(result="fail", error=str(exc))
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--copilot", default="copilot")
    parser.add_argument("--evidence", type=Path, help="save local probe JSON evidence")
    args = parser.parse_args(argv)
    cli = shutil.which(args.copilot)
    if cli is None:
        parser.error("Copilot CLI unavailable; required probe cannot be skipped")
    base = Path(tempfile.mkdtemp(prefix="shaper archive probe ")).resolve()
    evidence = probe(args.archive, cli, base)
    text = json.dumps(evidence, indent=2) + "\n"
    if args.evidence:
        args.evidence.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
