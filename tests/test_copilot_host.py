"""Deterministic Copilot contracts; no CLI installation or authentication needed."""

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_host_packages as builder
import validate_manifests


SKILLS = ("shape-release", "cutline", "release-slate", "scope-audit", "release-check")


def file_map(root):
    return builder._file_map(root)


def bootstrap(text):
    return re.search(r"```bash\n(SHAPER_ROOT=.*?)\n```", text, re.S).group(1)


class CopilotHostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="shaper copilot ")
        self.addCleanup(self.temp.cleanup)
        self.tmp = Path(self.temp.name)
        self.hosts = self.tmp / "hosts"
        self.assertEqual(builder.build_all(ROOT, self.hosts, out=io.StringIO()), 0)
        self.package = self.hosts / "copilot"
        self.runtime = self.package / ".github"

    def test_ac1_package_marketplace_and_unchanged_existing_runtime(self):
        manifest_path = self.package / ".plugin/plugin.json"
        self.assertTrue(manifest_path.is_file(), "missing Copilot package")
        manifest = json.loads(manifest_path.read_text())
        canonical = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(manifest["version"], canonical["version"])
        self.assertEqual(manifest["skills"], ".github/skills")
        self.assertNotIn("agents", manifest)
        self.assertNotIn("hooks", manifest)
        marketplace = json.loads((ROOT / ".github/plugin/marketplace.json").read_text())
        self.assertEqual(marketplace["plugins"][0]["source"], "./hosts/copilot")
        expected = {".plugin/plugin.json", "README.md", "shaper.jpg",
                    ".github/templates/release-plan.md", ".github/scripts/shaper_root.py"}
        for name in SKILLS:
            expected.add(f".github/skills/{name}/SKILL.md")
            expected.add(f".github/skills/{name}/scripts/{name.replace('-', '_')}.py")
        self.assertEqual(set(file_map(self.package)), expected)
        for host, prefix in (("claude", ""), ("codex", "plugins/shaper/")):
            for rel, data in file_map(ROOT / "skills").items():
                self.assertEqual((self.hosts / host / prefix / "skills" / rel).read_bytes(), data)
            self.assertEqual(
                (self.hosts / host / prefix / "templates/release-plan.md").read_bytes(),
                (ROOT / "templates/release-plan.md").read_bytes(),
            )

    def test_ac2_self_contained_prose_and_byte_identical_products(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                source = ROOT / "skills" / name
                target = self.runtime / "skills" / name
                text = (target / "SKILL.md").read_text()
                self.assertIn("COPILOT_HOME", text)
                self.assertIn("SHAPER_SKILL_DIR", text)
                self.assertIn("shaper_root.py", text)
                self.assertIn(f'"$SHAPER_ROOT/skills/{name}/scripts/', text)
                self.assertNotRegex(text, r"(?<!SHAPER_ROOT/)`skills/[^`]+")
                self.assertIn("docs/", text)
                for script in (source / "scripts").glob("*.py"):
                    self.assertEqual((target / "scripts" / script.name).read_bytes(), script.read_bytes())
                self.assertIn('||', bootstrap(text))
        self.assertIn('"$SHAPER_ROOT/templates/release-plan.md"',
                      (self.runtime / "skills/shape-release/SKILL.md").read_text())
        self.assertEqual((self.runtime / "templates/release-plan.md").read_bytes(),
                         (ROOT / "templates/release-plan.md").read_bytes())

    def _install(self, home, layout):
        package = home / "installed-plugins" / layout
        shutil.copytree(self.package, package)
        return package / ".github"

    def _resolve(self, home, active=None):
        env = {**os.environ, "COPILOT_HOME": str(home)}
        env.pop("SHAPER_SKILL_DIR", None)
        if active:
            env["SHAPER_SKILL_DIR"] = str(active)
        text = (self.runtime / "skills/shape-release/SKILL.md").read_text()
        return subprocess.run(["bash", "-c", bootstrap(text) + '\nprintf "%s\\n" "$SHAPER_ROOT"'],
                              cwd=self.tmp, env=env, text=True, capture_output=True)

    def test_ac2_bootstrap_honors_home_spaces_both_layouts_and_active_skill(self):
        home = self.tmp / "isolated home"
        direct = self._install(home, "_direct/ramboz--shaper--hosts-copilot")
        marketplace = self._install(home, "shaper/shaper")
        manifest = marketplace.parent / ".plugin/plugin.json"
        data = json.loads(manifest.read_text())
        data["version"] = "99.0.0"
        manifest.write_text(json.dumps(data))
        result = self._resolve(home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), str(marketplace.resolve()))
        for runtime in (direct, marketplace, self.runtime):
            result = self._resolve(home, runtime / "skills/shape-release")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), str(runtime.resolve()))

    def test_ac2_missing_wrong_identity_or_incomplete_runtime_fails_explicitly(self):
        home = self.tmp / "empty home"
        result = self._resolve(home)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no valid Shaper runtime", result.stderr)
        runtime = self._install(home, "shaper/shaper")
        manifest = runtime.parent / ".plugin/plugin.json"
        original = manifest.read_text()
        for content in ("[]", "{bad", original.replace('"shaper"', '"other"')):
            manifest.write_text(content)
            result = self._resolve(home)
            self.assertNotEqual(result.returncode, 0)
        manifest.write_text(original)
        (runtime / "templates/release-plan.md").unlink()
        self.assertNotEqual(self._resolve(home).returncode, 0)
        self.assertNotEqual(self._resolve(home, runtime / "skills/shape-release").returncode, 0)

    def test_packaged_locator_matches_bootstrap_and_reports_missing_runtime(self):
        home = self.tmp / "isolated home"
        runtime = self._install(home, "_direct/copilot")
        env = {**os.environ, "COPILOT_HOME": str(home)}
        env.pop("SHAPER_SKILL_DIR", None)
        command = [sys.executable, str(runtime / "scripts/shaper_root.py")]
        result = subprocess.run(command, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self._resolve(home).stdout)
        env["SHAPER_SKILL_DIR"] = str(runtime / "skills/cutline")
        result = subprocess.run(command, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), str(runtime.resolve()))
        (runtime / "templates/release-plan.md").unlink()
        result = subprocess.run(command, env=env, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no valid Shaper runtime", result.stderr)

    def test_bootstrap_does_not_execute_foreign_installed_locators(self):
        home = self.tmp / "isolated home"
        foreign = home / "installed-plugins/aaa/other"
        (foreign / ".plugin").mkdir(parents=True)
        (foreign / ".plugin/plugin.json").write_text(json.dumps({"name": "other"}))
        locator = foreign / ".github/scripts/shaper_root.py"
        locator.parent.mkdir(parents=True)
        marker = self.tmp / "foreign-locator-executed"
        locator.write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
            "raise RuntimeError('foreign locator must not execute')\n"
        )
        runtime = self._install(home, "shaper/shaper")
        result = self._resolve(home)
        self.assertFalse(marker.exists(), "bootstrap executed another plugin's locator")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), str(runtime.resolve()))

    def test_renderer_rejects_malformed_or_unsupported_auxiliary_metadata(self):
        for field in (
            "user-invocable: [unterminated", 'user-invocable: "unterminated',
            "user-invocable: null", "user-invocable: []", "unknown: value",
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "metadata"):
                builder.render_copilot_skill_md(
                    f"---\nname: test-skill\ndescription: Valid description\n{field}\n---\n"
                )

    def test_single_quoted_metadata_requires_doubled_interior_quotes(self):
        with self.assertRaisesRegex(ValueError, "metadata"):
            builder.render_copilot_skill_md(
                "---\nname: test-skill\ndescription: 'it's broken'\n---\n"
            )
        rendered = builder.render_copilot_skill_md(
            "---\nname: test-skill\ndescription: 'It''s valid'\n---\n"
        )
        metadata, _ = builder.skill_metadata(rendered)
        self.assertEqual(metadata["description"], "It's valid")

    def test_ac3_loader_limits_full_description_and_explicit_bad_metadata(self):
        for description in ("short text", "é" * 1100):
            source = f'---\nname: test-skill\ndescription: >\n  {description}\n---\n\n# Test\n'
            rendered = builder.render_copilot_skill_md(source)
            metadata, _ = builder.skill_metadata(rendered)
            self.assertLessEqual(len(metadata["description"]), 1024)
            self.assertIn(description, rendered)
        invalid = (
            "# No frontmatter", "---\nname: x\n---\nbody",
            "---\nname: shaper:x\ndescription: fine\n---\n",
            "---\nname: x\ndescription: []\n---\n",
            "---\nname: x\ndescription: # missing\n---\n",
            "---\nname: x\ndescription: *undefined\n---\n",
            "---\nname: x\ndescription: &anchor\n---\n",
            "---\nname: x\ndescription: !custom value\n---\n",
            "---\nname: x\nname: y\ndescription: text\n---\n",
        )
        for text in invalid:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "metadata|name|description"):
                builder.render_copilot_skill_md(text)

    def test_ac3_drift_missing_extra_stale_is_read_only(self):
        target = self.runtime / "skills/cutline/SKILL.md"
        self.assertTrue(target.is_file(), "missing generated Copilot skill")
        target.unlink()
        (self.runtime / "extra.txt").write_text("extra")
        (self.runtime / "templates/release-plan.md").write_text("stale")
        before = file_map(self.hosts)
        out = io.StringIO()
        self.assertEqual(builder.check_drift(ROOT, self.hosts, out), 1)
        self.assertEqual(file_map(self.hosts), before)
        for rel in ("skills/cutline/SKILL.md", "extra.txt", "templates/release-plan.md"):
            self.assertIn("copilot/.github/" + rel, out.getvalue())

    def test_ac3_validator_checks_actual_components_identity_metadata_and_versions(self):
        source = self.tmp / "source"
        for directory in (".claude-plugin", ".codex-plugin", ".github/plugin"):
            shutil.copytree(ROOT / directory, source / directory)
        shutil.copytree(self.hosts, source / "hosts")
        out = io.StringIO()
        self.assertEqual(validate_manifests.validate(source, out), 0, out.getvalue())
        path = source / "hosts/copilot/.plugin/plugin.json"
        data = json.loads(path.read_text())
        for field, value in (("skills", ".github/missing"), ("skills", "../outside"),
                             ("name", "other"), ("version", "99.0.0"), ("version", []),
                             ("description", None), ("agents", ".github/agents")):
            with self.subTest(field=field, value=value):
                path.write_text(json.dumps({**data, field: value}))
                out = io.StringIO()
                self.assertEqual(validate_manifests.validate(source, out), 1)
                self.assertIn("hosts/copilot", out.getvalue())
        path.write_text(json.dumps(data))
        (source / "hosts/copilot/.github/skills/cutline/SKILL.md").unlink()
        out = io.StringIO()
        self.assertEqual(validate_manifests.validate(source, out), 1)
        self.assertIn("cutline", out.getvalue())

    def test_ac3_marketplace_metadata_sources_and_package_exclusions(self):
        source = self.tmp / "source"
        for directory in (".claude-plugin", ".codex-plugin", ".github/plugin"):
            shutil.copytree(ROOT / directory, source / directory)
        shutil.copytree(self.hosts, source / "hosts")
        path = source / ".github/plugin/marketplace.json"
        data = json.loads(path.read_text())
        invalid = (
            {**data, "name": "other"},
            {**data, "owner": {"name": []}},
            {**data, "plugins": [{"name": "shaper", "source": {"path": "./hosts/copilot"}}]},
        )
        for payload in invalid:
            with self.subTest(payload=payload):
                path.write_text(json.dumps(payload))
                out = io.StringIO()
                self.assertEqual(validate_manifests.validate(source, out), 1)
                self.assertIn(".github/plugin/marketplace.json", out.getvalue())
        path.write_text(json.dumps(data))
        extra = source / "hosts/copilot/docs/internal.md"
        extra.parent.mkdir()
        extra.write_text("must not ship")
        out = io.StringIO()
        self.assertEqual(validate_manifests.validate(source, out), 1)
        self.assertIn("excluded/unexpected file", out.getvalue())

    def test_ac4_installed_documented_helpers_template_and_read_only_boundaries(self):
        home = self.tmp / "isolated home"
        runtime = self._install(home, "shaper/shaper")
        consumer = self.tmp / "consumer repo"
        consumer.mkdir()
        for rel, text in (
            ("docs/specs/README.md", "# Board\n\n| Spec | Slice | Status | Notes |\n"
             "|---|---|---|---|\n| [010-probe](010-probe/spec.md) | 010-01 | DONE | |\n"),
            ("docs/specs/010-probe/spec.md", "---\nstatus: DONE\n---\n# Probe\nSmall probe.\n"),
            ("docs/servo/release-signals/probe.md", "---\nstatus: pass\n---\n# Signal\nGood.\n"),
        ):
            path = consumer / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        before = file_map(consumer)
        env = {**os.environ, "COPILOT_HOME": str(home)}
        env.pop("SHAPER_SKILL_DIR", None)
        for name in SKILLS:
            text = (runtime / "skills" / name / "SKILL.md").read_text()
            helper = f'python3 "$SHAPER_ROOT/skills/{name}/scripts/{name.replace("-", "_")}.py"'
            self.assertIn(helper, text)
            args = '--repo "."'
            if name == "shape-release":
                args += (' --slug probe --problem "Need a probe" --appetite "One day"'
                         ' --solution "Small probe" --risk "None identified" --no-go "No automation"'
                         ' --jig-handoff "[Probe](../specs/010-probe/spec.md)"'
                         ' --vertical-scope "Create a useful plan" --criterion "Helper works"')
            elif name != "release-slate":
                args += ' --release probe'
            command = bootstrap(text) + "\n" + helper + " " + args
            result = subprocess.run(["bash", "-c", command], cwd=consumer, text=True,
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            if name == "cutline":
                self.assertIn("include", result.stdout.lower())
            elif name == "scope-audit":
                self.assertIn("advisory", result.stdout.lower())
            elif name == "release-check":
                self.assertIn("recommendation", result.stdout.lower())
        for rel, data in before.items():
            self.assertEqual((consumer / rel).read_bytes(), data)
        plan = (consumer / "docs/releases/probe.md").read_text()
        self.assertIn("### Architecture appetite", plan)
        self.assertIn("Create a useful plan", plan)
        self.assertIn("probe.md", (consumer / "docs/releases/README.md").read_text())

    def test_ac5_adopter_docs_cli_boundary_install_and_discovery(self):
        readme = (ROOT / "README.md").read_text()
        for text in ("copilot plugin marketplace add ramboz/shaper",
                     "copilot plugin install shaper@shaper",
                     "copilot plugin install ramboz/shaper:hosts/copilot",
                     "copilot skill list --json", "Copilot CLI", "IDE", "COPILOT_HOME"):
            self.assertIn(text, readme)

    def test_ac4_probe_requires_all_enabled_plugin_skills_at_declared_paths(self):
        import smoke_copilot_install

        rows = [{"name": name, "enabled": True, "source": "plugin",
                 "path": str(self.runtime / "skills" / name)} for name in SKILLS]
        self.assertEqual(set(smoke_copilot_install.discovered_skills(rows, self.package)), set(SKILLS))
        for bad in ([], rows[:-1], [{**row, "source": "builtin"} for row in rows],
                    [{**row, "enabled": False} for row in rows],
                    [{**row, "path": "/consumer/skills/" + row["name"]} for row in rows]):
            with self.subTest(bad=bad), self.assertRaisesRegex(RuntimeError, "discovery"):
                smoke_copilot_install.discovered_skills(bad, self.package)

    def test_ac4_probe_runs_two_isolated_modes_without_requiring_cli_in_ci(self):
        import smoke_copilot_install as smoke

        base = self.tmp / "probe fixture"
        base.mkdir()
        original_run = smoke.run

        def fake_cli(command, cwd, env, evidence):
            if command[0] == "bash":
                return original_run(command, cwd, env, evidence)
            evidence.append({"command": command, "exit_code": 0, "cwd": str(cwd)})
            if command[-1] == "--version":
                return "Test CLI\n"
            if command[-2:] == ["list", "--json"]:
                package = base / "marketplace/hosts/copilot"
                if "direct" in cwd.parts:
                    package = Path(env["COPILOT_HOME"]) / "installed-plugins/_direct/copilot"
                return json.dumps([{"name": name, "enabled": True, "source": "plugin",
                                    "path": str(package / ".github/skills" / name)}
                                   for name in SKILLS])
            if command[1:3] == ["plugin", "install"] and command[-1] != "shaper@shaper":
                shutil.copytree(command[-1], Path(env["COPILOT_HOME"]) / "installed-plugins/_direct/copilot")
            return "Test installation successful\n"

        out = io.StringIO()
        with mock.patch.object(smoke.shutil, "which", return_value="/fake/copilot"), \
                mock.patch.object(smoke.tempfile, "mkdtemp", return_value=str(base)), \
                mock.patch.object(smoke, "run", side_effect=fake_cli), \
                mock.patch("sys.stdout", out):
            self.assertEqual(smoke.main(["--copilot", "/fake/copilot"]), 0)
        evidence = json.loads(out.getvalue())
        self.assertEqual([item["mode"] for item in evidence["installs"]], ["marketplace", "direct"])
        for install in evidence["installs"]:
            self.assertTrue(install["helpers"]["jig_servo_unchanged"])
            self.assertEqual(len(install["helpers"]["commands"]), 5)


if __name__ == "__main__":
    unittest.main()
