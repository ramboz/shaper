import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _file_map(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


class RootManifestTests(unittest.TestCase):
    def test_root_manifests_exist_with_shaper_metadata(self):
        claude = _read_json(ROOT / ".claude-plugin" / "plugin.json")
        codex = _read_json(ROOT / ".codex-plugin" / "plugin.json")

        for manifest in (claude, codex):
            self.assertEqual(manifest["name"], "shaper")
            self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
            self.assertIn("release", manifest["description"].lower())
            self.assertEqual(manifest["author"]["name"], "ramboz")

        self.assertNotIn("hooks", codex)
        self.assertNotIn("apps", codex)
        self.assertNotIn("mcpServers", codex)
        self.assertEqual(codex["interface"]["displayName"], "shaper")

    def test_claude_marketplace_points_to_hosts_claude(self):
        marketplace = _read_json(ROOT / ".claude-plugin" / "marketplace.json")
        plugin = marketplace["plugins"][0]

        self.assertEqual(marketplace["name"], "shaper")
        self.assertEqual(marketplace["owner"]["name"], "ramboz")
        self.assertEqual(plugin["name"], "shaper")
        self.assertEqual(plugin["source"]["source"], "git-subdir")
        self.assertEqual(plugin["source"]["path"], "hosts/claude")
        self.assertNotEqual(plugin["source"]["path"], ".")


class HostPackageBuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-hosts-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_all_materializes_both_host_packages(self):
        import build_host_packages

        out = io.StringIO()
        code = build_host_packages.build_all(
            source_root=ROOT,
            hosts_root=self.tmp,
            out=out,
        )

        self.assertEqual(code, 0, out.getvalue())
        self.assertTrue(
            (self.tmp / "claude" / ".claude-plugin" / "plugin.json").is_file()
        )
        self.assertTrue((self.tmp / "claude" / "README.md").is_file())
        self.assertEqual(
            (self.tmp / "claude" / "shaper.jpg").read_bytes(),
            (ROOT / "shaper.jpg").read_bytes(),
        )
        self.assertFalse((self.tmp / "claude" / ".codex-plugin").exists())
        self.assertFalse((self.tmp / "claude" / ".codex").exists())

        marketplace = _read_json(
            self.tmp / "codex" / ".agents" / "plugins" / "marketplace.json"
        )
        plugin = marketplace["plugins"][0]
        self.assertEqual(plugin["name"], "shaper")
        self.assertEqual(plugin["source"]["path"], "./plugins/shaper")
        self.assertEqual(plugin["policy"]["installation"], "AVAILABLE")
        self.assertEqual(plugin["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(plugin["category"], "Engineering")
        self.assertTrue(
            (
                self.tmp
                / "codex"
                / "plugins"
                / "shaper"
                / ".codex-plugin"
                / "plugin.json"
            ).is_file()
        )
        self.assertEqual(
            (
                self.tmp
                / "codex"
                / "plugins"
                / "shaper"
                / "shaper.jpg"
            ).read_bytes(),
            (ROOT / "shaper.jpg").read_bytes(),
        )
        self.assertFalse((self.tmp / "codex" / "plugins" / "shaper" / ".codex").exists())

    def test_drift_check_is_read_only_and_actionable(self):
        import build_host_packages

        hosts = self.tmp / "hosts"
        self.assertEqual(
            build_host_packages.build_all(
                source_root=ROOT, hosts_root=hosts, out=io.StringIO()
            ),
            0,
        )
        before = _file_map(hosts)
        stale = hosts / "claude" / ".claude-plugin" / "plugin.json"
        stale.write_text("stale\n", encoding="utf-8")

        out = io.StringIO()
        code = build_host_packages.check_drift(
            source_root=ROOT,
            hosts_root=hosts,
            out=out,
        )

        self.assertNotEqual(code, 0)
        self.assertEqual(_file_map(hosts), {**before, "claude/.claude-plugin/plugin.json": b"stale\n"})
        self.assertIn("claude/.claude-plugin/plugin.json", out.getvalue())
        self.assertIn("scripts/build_host_packages.py", out.getvalue())

    def test_committed_hosts_match_fresh_build(self):
        import build_host_packages

        out = io.StringIO()
        code = build_host_packages.check_drift(
            source_root=ROOT,
            hosts_root=ROOT / "hosts",
            out=out,
        )

        self.assertEqual(code, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
