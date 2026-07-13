import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_release_zip  # noqa: E402


HOSTS_ROOT = ROOT / "hosts"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def _host_version(host: str) -> str:
    if host == "claude":
        manifest = HOSTS_ROOT / "claude" / ".claude-plugin" / "plugin.json"
    elif host == "codex":
        manifest = (
            HOSTS_ROOT
            / "codex"
            / "plugins"
            / "shaper"
            / ".codex-plugin"
            / "plugin.json"
        )
    else:
        raise ValueError(host)
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def _build_once(host: str, hosts_root: Path = HOSTS_ROOT) -> tuple[Path, str]:
    version = _host_version(host)
    tmp = Path(tempfile.mkdtemp(prefix=f"shaper-{host}-zip-"))
    zip_path = tmp / f"shaper-{host}-v{version}.zip"
    out = io.StringIO()
    code = build_release_zip.build(
        host=host,
        hosts_root=hosts_root,
        version=version,
        output_path=zip_path,
        out=out,
    )
    if code != 0:
        raise AssertionError(out.getvalue())
    return zip_path, out.getvalue()


class ReleaseArchiveShapeTests(unittest.TestCase):
    def test_default_output_names_are_host_explicit(self):
        self.assertEqual(
            build_release_zip.default_output_path(ROOT, "claude", "1.2.3"),
            ROOT / "dist" / "shaper-claude-v1.2.3.zip",
        )
        self.assertEqual(
            build_release_zip.default_output_path(ROOT, "codex", "1.2.3"),
            ROOT / "dist" / "shaper-codex-v1.2.3.zip",
        )

    def test_claude_zip_is_flat_plugin_package(self):
        zip_path, _output = _build_once("claude")
        self.addCleanup(shutil.rmtree, zip_path.parent, ignore_errors=True)

        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())

        self.assertIn(".claude-plugin/plugin.json", names)
        self.assertIn("shaper.jpg", names)
        self.assertIn("skills/shape-release/SKILL.md", names)
        self.assertIn("skills/shape-release/scripts/shape_release.py", names)
        self.assertIn("skills/cutline/SKILL.md", names)
        self.assertIn("skills/cutline/scripts/cutline.py", names)
        self.assertIn("skills/release-slate/SKILL.md", names)
        self.assertIn("skills/release-slate/scripts/release_slate.py", names)
        self.assertIn("skills/scope-audit/SKILL.md", names)
        self.assertIn("skills/scope-audit/scripts/scope_audit.py", names)
        self.assertIn("skills/release-check/SKILL.md", names)
        self.assertIn("skills/release-check/scripts/release_check.py", names)
        self.assertNotIn("hosts/claude/.claude-plugin/plugin.json", names)
        self.assertFalse(any(name.startswith("hosts/") for name in names))
        self.assertFalse(any(name.startswith("docs/") for name in names))
        self.assertFalse(any(name.startswith(".github/") for name in names))
        self.assertFalse(any(name.startswith(".codex-plugin/") for name in names))

    def test_codex_zip_is_marketplace_bundle(self):
        zip_path, _output = _build_once("codex")
        self.addCleanup(shutil.rmtree, zip_path.parent, ignore_errors=True)

        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())

        self.assertIn(".agents/plugins/marketplace.json", names)
        self.assertIn("plugins/shaper/.codex-plugin/plugin.json", names)
        self.assertIn("plugins/shaper/shaper.jpg", names)
        self.assertIn("plugins/shaper/skills/shape-release/SKILL.md", names)
        self.assertIn("plugins/shaper/skills/shape-release/scripts/shape_release.py", names)
        self.assertIn("plugins/shaper/skills/cutline/SKILL.md", names)
        self.assertIn("plugins/shaper/skills/cutline/scripts/cutline.py", names)
        self.assertIn("plugins/shaper/skills/release-slate/SKILL.md", names)
        self.assertIn(
            "plugins/shaper/skills/release-slate/scripts/release_slate.py",
            names,
        )
        self.assertIn("plugins/shaper/skills/scope-audit/SKILL.md", names)
        self.assertIn(
            "plugins/shaper/skills/scope-audit/scripts/scope_audit.py",
            names,
        )
        self.assertIn("plugins/shaper/skills/release-check/SKILL.md", names)
        self.assertIn(
            "plugins/shaper/skills/release-check/scripts/release_check.py",
            names,
        )
        self.assertFalse(any(name.startswith("hosts/") for name in names))
        self.assertFalse(any(name.startswith("docs/") for name in names))
        self.assertFalse(any(name.startswith(".github/") for name in names))


class VersionCoherenceTests(unittest.TestCase):
    def test_version_mismatch_refuses_to_write_zip(self):
        tmp = Path(tempfile.mkdtemp(prefix="shaper-version-mismatch-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        zip_path = tmp / "shaper-claude-v9.9.9.zip"
        out = io.StringIO()

        code = build_release_zip.build(
            host="claude",
            hosts_root=HOSTS_ROOT,
            version="9.9.9",
            output_path=zip_path,
            out=out,
        )

        self.assertEqual(code, 2)
        self.assertIn("mislabeled", out.getvalue())
        self.assertFalse(zip_path.exists())

    def test_output_filename_must_match_host_and_version(self):
        tmp = Path(tempfile.mkdtemp(prefix="shaper-output-name-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        zip_path = tmp / "shaper-v0.1.0.zip"
        out = io.StringIO()

        code = build_release_zip.build(
            host="claude",
            hosts_root=HOSTS_ROOT,
            version=_host_version("claude"),
            output_path=zip_path,
            out=out,
        )

        self.assertEqual(code, 2)
        self.assertIn("shaper-claude-v", out.getvalue())
        self.assertFalse(zip_path.exists())


class DeterministicArchiveTests(unittest.TestCase):
    def test_repeated_claude_builds_are_byte_identical(self):
        first, _first_output = _build_once("claude")
        second, _second_output = _build_once("claude")
        self.addCleanup(shutil.rmtree, first.parent, ignore_errors=True)
        self.addCleanup(shutil.rmtree, second.parent, ignore_errors=True)

        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_repeated_codex_builds_are_byte_identical(self):
        first, _first_output = _build_once("codex")
        second, _second_output = _build_once("codex")
        self.addCleanup(shutil.rmtree, first.parent, ignore_errors=True)
        self.addCleanup(shutil.rmtree, second.parent, ignore_errors=True)

        self.assertEqual(first.read_bytes(), second.read_bytes())


class ArchiveSmokeTests(unittest.TestCase):
    def test_claude_smoke_passes_and_names_host(self):
        zip_path, _output = _build_once("claude")
        self.addCleanup(shutil.rmtree, zip_path.parent, ignore_errors=True)
        out = io.StringIO()

        code = build_release_zip.smoke_test("claude", zip_path, out=out)

        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("claude", out.getvalue().lower())

    def test_codex_smoke_uses_extract_then_add_language(self):
        zip_path, _output = _build_once("codex")
        self.addCleanup(shutil.rmtree, zip_path.parent, ignore_errors=True)
        out = io.StringIO()

        code = build_release_zip.smoke_test("codex", zip_path, out=out)

        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("codex", out.getvalue().lower())
        self.assertIn("extract-then-add", out.getvalue())

    def test_smoke_fails_when_zip_name_version_disagrees_with_manifest(self):
        zip_path, _output = _build_once("claude")
        self.addCleanup(shutil.rmtree, zip_path.parent, ignore_errors=True)
        renamed = zip_path.parent / "shaper-claude-v9.9.9.zip"
        shutil.copyfile(zip_path, renamed)
        out = io.StringIO()

        code = build_release_zip.smoke_test("claude", renamed, out=out)

        self.assertNotEqual(code, 0)
        self.assertIn("version mismatch", out.getvalue())

    def test_smoke_fails_when_required_file_is_missing(self):
        tmp = Path(tempfile.mkdtemp(prefix="shaper-bad-zip-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        bad_zip = tmp / "shaper-codex-v1.2.3.zip"
        with zipfile.ZipFile(bad_zip, "w") as zf:
            zf.writestr(
                "plugins/shaper/.codex-plugin/plugin.json",
                json.dumps({"version": "1.2.3"}),
            )
        out = io.StringIO()

        code = build_release_zip.smoke_test("codex", bad_zip, out=out)

        self.assertNotEqual(code, 0)
        self.assertIn(".agents/plugins/marketplace.json", out.getvalue())

    def test_smoke_fails_cleanly_for_corrupt_zip(self):
        tmp = Path(tempfile.mkdtemp(prefix="shaper-corrupt-zip-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        bad_zip = tmp / "shaper-claude-v0.1.0.zip"
        bad_zip.write_text("not a zip", encoding="utf-8")
        out = io.StringIO()

        code = build_release_zip.smoke_test("claude", bad_zip, out=out)

        self.assertNotEqual(code, 0)
        self.assertIn("invalid zip archive", out.getvalue())


class ReleaseWorkflowArchiveTests(unittest.TestCase):
    def test_release_workflow_builds_smokes_and_uploads_archives_only_on_release(self):
        text = RELEASE_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("package:", text)
        self.assertIn("needs: release-please", text)
        self.assertIn(
            "if: needs.release-please.outputs.release_created == 'true'",
            text,
        )
        self.assertIn("ref: ${{ needs.release-please.outputs.tag_name }}", text)
        self.assertIn("python3 scripts/build_host_packages.py --check", text)
        self.assertIn("shaper-claude-v${{ needs.release-please.outputs.version }}.zip", text)
        self.assertIn("shaper-codex-v${{ needs.release-please.outputs.version }}.zip", text)
        self.assertIn("python3 scripts/build_release_zip.py", text)
        self.assertIn("--host claude", text)
        self.assertIn("--host codex", text)
        self.assertIn("--smoke-test", text)
        self.assertIn("gh release upload", text)
        self.assertIn("extract-then-add Codex marketplace bundle", text)
        self.assertIn("grep -q \"^## Install artifacts$\"", text)
        self.assertRegex(text, r"(?ms)release-please:.*permissions:.*contents: write.*pull-requests: write")
        self.assertRegex(text, r"(?ms)package:.*permissions:.*contents: write")
        self.assertNotIn("shaper-v${{ needs.release-please.outputs.version }}.zip", text)


class IgnoreRulesTests(unittest.TestCase):
    def test_dist_and_zip_files_are_ignored(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertRegex(text, r"(?m)^dist/$")
        self.assertRegex(text, r"(?m)^\*.zip$")


if __name__ == "__main__":
    unittest.main()
