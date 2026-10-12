"""Archive/release contracts; the real Copilot CLI probe is explicitly local."""

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_host_packages as packages
import build_release_zip as archives
import smoke_copilot_install as boundary


class CopilotReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="shaper archive ")
        self.addCleanup(self.temp.cleanup)
        self.tmp = Path(self.temp.name)
        self.hosts = self.tmp / "hosts"
        # Copy committed packages, not regenerated root source.
        shutil.copytree(ROOT / "hosts/copilot", self.hosts / "copilot")
        self.package = self.hosts / "copilot"
        self.manifest = self.package / ".plugin/plugin.json"
        self.payload = json.loads(self.manifest.read_text())
        self.version = self.payload["version"]
        self.archive = self.tmp / f"shaper-copilot-v{self.version}.zip"

    def build(self, **kwargs):
        out = io.StringIO()
        code = archives.build(**{
            "host": "copilot", "hosts_root": self.hosts,
            "version": self.version, "output_path": self.archive, "out": out,
            **kwargs,
        })
        return code, out.getvalue()

    def smoke(self, path=None, version=None):
        out = io.StringIO()
        code = archives.smoke_test("copilot", path or self.archive, version, out)
        return code, out.getvalue()

    def raw_archive(self):
        """Make invalid payloads without the build-time guard."""
        with zipfile.ZipFile(self.archive, "w") as zf:
            for rel, data in packages._file_map(self.package).items():
                zf.writestr(rel, data)

    def test_ac1_committed_payload_determinism_and_native_manifest(self):
        self.assertEqual(self.build()[0], 0, "Copilot host must build")
        first = self.archive.read_bytes()
        with zipfile.ZipFile(self.archive) as zf:
            self.assertEqual(
                {name: zf.read(name) for name in zf.namelist()},
                packages._file_map(self.package),
            )
            self.assertIn(".plugin/plugin.json", zf.namelist())
            self.assertIn(".github/scripts/shaper_root.py", zf.namelist())
        self.assertEqual(self.build()[0], 0)
        self.assertEqual(self.archive.read_bytes(), first)
        code, output = self.smoke()
        self.assertEqual(code, 0, output)
        self.assertIn("extract-then-install", output)
        self.assertIn("copilot", archives.HOSTS)
        with mock.patch("sys.stdout", new=io.StringIO()):
            self.assertEqual(archives.main([
                "build_release_zip.py", "--host", "copilot", "--version", self.version,
                "--hosts-root", str(self.hosts), "--output", str(self.archive),
            ]), 0)

    def test_ac1_rejects_unknown_missing_and_mislabeled_artifacts(self):
        for kwargs, diagnostic in (
            ({"host": "unknown"}, "unknown host"),
            ({"hosts_root": self.tmp / "missing"}, "package missing"),
            ({"version": "99.0.0"}, "version mismatch"),
            ({"output_path": self.tmp / "shaper.zip"}, "output filename"),
        ):
            with self.subTest(kwargs=kwargs):
                code, output = self.build(**kwargs)
                self.assertNotEqual(code, 0)
                self.assertIn(diagnostic, output)
                self.assertFalse(self.archive.exists())
        self.assertEqual(self.build()[0], 0)
        for filename, version in (
            ("shaper-copilot-v99.0.0.zip", None),
            ("shaper-copilot-v99.0.0.zip", self.version),
            (f"shaper-claude-v{self.version}.zip", self.version),
            ("shaper.zip", None),
        ):
            with self.subTest(filename=filename, version=version):
                renamed = self.tmp / filename
                shutil.copyfile(self.archive, renamed)
                code, output = self.smoke(renamed, version)
                self.assertNotEqual(code, 0, output)

    def test_ac1_build_and_smoke_reuse_declared_component_validation(self):
        # Includes files outside simple forbidden-prefix checks and discovery
        # metadata that cannot be detected by counting payload files.
        mutations = (
            ("manifest", "skills", ".github/missing", "skills component path"),
            ("manifest", "skills", "../outside", "skills component path"),
            ("manifest", "skills", [], "skills component path"),
            ("manifest", "name", "other", "name must be shaper"),
            ("manifest", "agents", ".github/agents", "unsupported component"),
            ("missing", ".github/scripts/shaper_root.py", None, "missing required file"),
            ("missing", ".github/templates/release-plan.md", None, "missing required file"),
            ("missing", ".github/skills/cutline/scripts/cutline.py", None, "missing required file"),
            ("extra", "docs/internal.md", "repo only", "excluded/unexpected file"),
            ("extra", ".github/workflows/internal.yml", "repo only", "excluded/unexpected file"),
            ("extra", "AGENTS.md", "repo only", "excluded/unexpected file"),
            ("replace", ".github/skills/cutline/SKILL.md",
             "---\nname: shaper:cutline\ndescription: invalid\n---\n", "metadata"),
        )
        original = packages._file_map(self.package)
        for kind, field, value, diagnostic in mutations:
            with self.subTest(kind=kind, field=field, value=value):
                shutil.rmtree(self.package)
                shutil.copytree(ROOT / "hosts/copilot", self.package)
                if kind == "manifest":
                    self.manifest.write_text(json.dumps({**self.payload, field: value}))
                else:
                    path = self.package / field
                    if kind == "missing":
                        path.unlink()
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(value)
                if self.archive.exists():
                    self.archive.unlink()
                with mock.patch.object(archives, "copilot_package_errors",
                                       wraps=packages.copilot_package_errors) as guard:
                    code, output = self.build()
                    self.assertNotEqual(code, 0, output)
                    self.assertIn(diagnostic, output)
                    guard.assert_called_once()
                self.assertFalse(self.archive.exists())
                self.raw_archive()
                with mock.patch.object(archives, "copilot_package_errors",
                                       wraps=packages.copilot_package_errors) as guard:
                    code, output = self.smoke()
                    self.assertNotEqual(code, 0, output)
                    self.assertIn(diagnostic, output)
                    guard.assert_called_once()
        self.assertIn(".github/skills/cutline/SKILL.md", original)

    def test_ac1_malformed_manifest_errors_are_diagnostic_and_type_safe(self):
        for payload, diagnostic in (
            (b"{bad", "invalid JSON"),
            (b"\xff", "UTF-8"),
            (b"[]", "object"),
            (b"null", "object"),
            (b'"string"', "object"),
            (b"42", "object"),
            (json.dumps({**self.payload, "version": []}).encode(), "string version"),
            (json.dumps({**self.payload, "version": 123}).encode(), "string version"),
        ):
            with self.subTest(payload=payload):
                self.manifest.write_bytes(payload)
                code, output = self.build()
                self.assertNotEqual(code, 0)
                self.assertIn(diagnostic, output)
                self.assertIn(".plugin/plugin.json", output)
                self.raw_archive()
                code, output = self.smoke()
                self.assertNotEqual(code, 0)
                self.assertIn(diagnostic, output)
                self.assertIn(".plugin/plugin.json", output)

    def test_ac1_smoke_rejects_unsafe_archive_members_before_extraction(self):
        self.raw_archive()
        with zipfile.ZipFile(self.archive, "a") as zf:
            zf.writestr("../escaped.txt", "must not extract")
        code, output = self.smoke()
        self.assertNotEqual(code, 0)
        self.assertIn("unsafe archive", output)

    def test_ac2_version_inventory_gated_tagged_release_and_additive_notes(self):
        config = json.loads((ROOT / ".github/release-please-config.json").read_text())
        paths = {entry["path"] for entry in config["packages"]["."]["extra-files"]}
        self.assertIn("hosts/copilot/.plugin/plugin.json", paths)
        self.assertEqual(len(paths), 5)
        text = (ROOT / ".github/workflows/release.yml").read_text()
        self.assertIn("if: needs.release-please.outputs.release_created == 'true'", text)
        self.assertIn("ref: ${{ needs.release-please.outputs.tag_name }}", text)
        self.assertLess(text.index("build_host_packages.py --check"), text.index("--host copilot"))
        self.assertEqual(text.count("--host copilot"), 2)
        name = "shaper-copilot-v${{ needs.release-please.outputs.version }}.zip"
        self.assertEqual(text.count(name), 3, "build, smoke, upload")
        self.assertIn("extract-then-install Copilot CLI", text)
        self.assertIn('.plugin/plugin.json', text)
        self.assertIn('grep -q "^## Install artifacts$"', text)
        self.assertIn('--notes "${existing}${note}"', text)
        self.assertNotIn("smoke_copilot_archive.py", text, "CI must not require a real CLI")

    def test_ac3_extracted_probe_reuses_boundary_and_refines_installed_plan(self):
        # A mocked installation exercises the deterministic probe mechanics,
        # NOT the required real CLI discovery (recorded separately as evidence).
        import smoke_copilot_archive as probe

        self.assertEqual(self.build()[0], 0)
        original_run = boundary.run

        def fake_cli(command, cwd, env, evidence):
            if command[0] != "fake-copilot":
                return original_run(command, cwd, env, evidence)
            self.assertNotEqual(env["COPILOT_HOME"], os.environ.get("COPILOT_HOME"))
            installed = Path(env["COPILOT_HOME"]) / "installed-plugins/_direct/shaper"
            evidence.append({"command": command, "exit_code": 0, "cwd": str(cwd)})
            if command[1:] == ["--version"]:
                return "test-cli\n"
            if command[1:3] == ["plugin", "install"]:
                source = Path(command[3])
                self.assertNotEqual(source, ROOT / "hosts/copilot")
                self.assertNotEqual(source, cwd)
                shutil.copytree(source, installed)
                return "Installed\n"
            self.assertEqual(command[1:], ["skill", "list", "--json"])
            return json.dumps([
                {"name": name, "source": "plugin", "enabled": True,
                 "path": str(installed / ".github/skills" / name)}
                for name in boundary.SKILLS
            ])

        with mock.patch.object(probe, "run", side_effect=fake_cli), \
                mock.patch.object(boundary, "run", side_effect=fake_cli), \
                mock.patch.object(probe, "helper_probe", wraps=boundary.helper_probe) as helpers:
            evidence = probe.probe(self.archive, "fake-copilot", self.tmp / "probe")
        helpers.assert_called_once()
        self.assertEqual(evidence["result"], "pass", evidence)
        self.assertEqual(len(evidence["discovered"]), 5)
        self.assertTrue(evidence["payload_byte_identical"])
        self.assertTrue(evidence["refined_plan"])
        self.assertTrue(evidence["jig_servo_unchanged"])
        self.assertEqual(evidence["fixture_sha256_before"], evidence["fixture_sha256_after"])
        plan = (Path(evidence["consumer"]) / "docs/releases/probe.md").read_text()
        self.assertIn("Refined archive plan", plan)
        self.assertIn("Create a useful plan", plan)

    def test_ac4_distribution_docs_and_owned_python_inventory(self):
        for rel in ("README.md", "docs/architecture.md", "docs/product-vision.md"):
            text = (ROOT / rel).read_text()
            self.assertIn("shaper-copilot-vX.Y.Z.zip", text, rel)
            self.assertIn("extract-then-install", text, rel)
            self.assertIn("CLI", text, rel)
        readme = (ROOT / "README.md").read_text()
        self.assertIn('copilot plugin install "/absolute/path/to/extracted/shaper"', readme)
        self.assertIn("smoke_copilot_archive.py", readme)
        for rel in (".jig/lint-command", ".github/workflows/ci.yml"):
            text = (ROOT / rel).read_text()
            self.assertIn("scripts/smoke_copilot_archive.py", text, rel)
            self.assertIn("tests/test_copilot_release.py", text, rel)


if __name__ == "__main__":
    unittest.main()
