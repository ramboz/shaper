import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

RELEASE_PLEASE_CONFIG = ROOT / ".github" / "release-please-config.json"
RELEASE_PLEASE_MANIFEST = ROOT / ".github" / ".release-please-manifest.json"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
VERSIONED_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "hosts/claude/.claude-plugin/plugin.json",
    "hosts/codex/plugins/shaper/.codex-plugin/plugin.json",
)

PR_TITLE_TYPES = {
    "feat",
    "fix",
    "perf",
    "docs",
    "chore",
    "refactor",
    "test",
    "build",
    "ci",
}


def _pr_title_workflow_text() -> str:
    return (ROOT / ".github" / "workflows" / "pr-title.yml").read_text(
        encoding="utf-8"
    )


def _workflow_subject_pattern(text: str) -> str:
    match = re.search(r"(?m)^          subjectPattern: (.+)$", text)
    if not match:
        raise AssertionError("subjectPattern missing from PR title workflow")
    return match.group(1)


def _valid_pr_title(title: str, workflow_text: str) -> bool:
    commit_type_match = re.match(r"^(?P<type>[a-z]+)\([^)]+\): (?P<subject>.+)$", title)
    if not commit_type_match or commit_type_match.group("type") not in PR_TITLE_TYPES:
        return False
    subject_pattern = _workflow_subject_pattern(workflow_text)
    match = re.match(r"^[a-z]+\(.*\): (?P<subject>.+)$", title)
    if not match:
        return False
    subject = match.group("subject")
    if not re.match(subject_pattern, subject):
        return False
    return True


class WorkflowFileTests(unittest.TestCase):
    def test_ci_workflow_runs_project_quality_gates(self):
        workflow = ROOT / ".github" / "workflows" / "ci.yml"
        text = workflow.read_text(encoding="utf-8")

        self.assertIn("pull_request:", text)
        self.assertIn("branches: [main]", text)
        self.assertIn("actions/checkout@v4", text)
        self.assertIn("actions/setup-python@v5", text)
        self.assertIn("python3 -m unittest discover -s tests", text)
        self.assertIn("python3 scripts/check_python_syntax.py", text)
        self.assertIn("python3 scripts/validate_manifests.py", text)
        self.assertIn("python3 scripts/build_host_packages.py --check", text)
        self.assertIn("workflow.py status-board .", text)
        self.assertIn("git diff --exit-code docs/specs/README.md", text)
        self.assertNotIn("release-please", text)

    def test_pr_title_workflow_enforces_release_language(self):
        text = _pr_title_workflow_text()

        self.assertIn("pull_request:", text)
        self.assertIn("amannn/action-semantic-pull-request@v5", text)
        self.assertIn("requireScope: true", text)
        for commit_type in (
            "feat",
            "fix",
            "perf",
            "docs",
            "chore",
            "refactor",
            "test",
            "build",
            "ci",
        ):
            self.assertRegex(text, rf"(?m)^            {commit_type}$")

    def test_pr_title_examples_demonstrate_passing_and_failing_shapes(self):
        text = _pr_title_workflow_text()
        passing = "feat(release-pipeline): add ci gate"
        failing = "add ci gate"

        self.assertTrue(_valid_pr_title(passing, text), passing)
        self.assertFalse(_valid_pr_title(failing, text), failing)


class ReleasePleasePipelineTests(unittest.TestCase):
    def test_release_workflow_runs_release_please_only(self):
        text = RELEASE_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("push:", text)
        self.assertIn("branches: [main]", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("contents: write", text)
        self.assertIn("pull-requests: write", text)
        self.assertIn("release_created: ${{ steps.release.outputs.release_created }}", text)
        self.assertIn("tag_name: ${{ steps.release.outputs.tag_name }}", text)
        self.assertIn("version: ${{ steps.release.outputs.version }}", text)
        self.assertIn("googleapis/release-please-action@v4", text)
        self.assertIn("config-file: .github/release-please-config.json", text)
        self.assertIn("manifest-file: .github/.release-please-manifest.json", text)
        self.assertNotIn("gh release upload", text)
        self.assertNotIn("build_host_packages.py", text)

    def test_release_please_config_updates_all_versioned_manifests(self):
        config = json.loads(RELEASE_PLEASE_CONFIG.read_text(encoding="utf-8"))

        self.assertEqual(config.get("release-type"), "simple")
        self.assertIs(config.get("include-v-in-tag"), True)
        self.assertIs(config.get("include-component-in-tag"), False)

        package = config.get("packages", {}).get(".")
        self.assertIsInstance(package, dict)
        extra_files = package.get("extra-files", [])
        version_paths = {
            entry.get("path")
            for entry in extra_files
            if isinstance(entry, dict)
            and entry.get("type") == "json"
            and entry.get("jsonpath") == "$.version"
        }
        self.assertEqual(version_paths, set(VERSIONED_MANIFESTS))

    def test_release_please_manifest_is_seeded_to_current_version(self):
        manifest = json.loads(RELEASE_PLEASE_MANIFEST.read_text(encoding="utf-8"))
        versions = {
            json.loads((ROOT / path).read_text(encoding="utf-8"))["version"]
            for path in VERSIONED_MANIFESTS
        }

        self.assertEqual(len(versions), 1)
        self.assertEqual(manifest, {".": versions.pop()})

    def test_release_changelog_seed_exists(self):
        changelog = ROOT / "CHANGELOG.md"
        text = changelog.read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Changelog\n"))

    def test_docs_explain_release_pr_flow_and_dry_run(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("release PR", readme)
        self.assertIn("Do not hand-edit", readme)
        self.assertIn(".github/release-please-config.json", readme)
        self.assertIn("npx release-please release-pr", readme)
        self.assertIn("squash", readme.lower())


class ManifestValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-manifests-"))
        shutil.copytree(ROOT / ".claude-plugin", self.tmp / ".claude-plugin")
        shutil.copytree(ROOT / ".codex-plugin", self.tmp / ".codex-plugin")
        shutil.copytree(ROOT / "hosts", self.tmp / "hosts")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_valid_repo_manifests_pass(self):
        import validate_manifests

        out = io.StringIO()
        code = validate_manifests.validate(root=ROOT, out=out)

        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("manifest(s) valid", out.getvalue())

    def test_missing_root_plugin_name_fails_with_file_and_field(self):
        import validate_manifests

        path = self.tmp / ".claude-plugin" / "plugin.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.pop("name")
        path.write_text(json.dumps(payload), encoding="utf-8")

        out = io.StringIO()
        code = validate_manifests.validate(root=self.tmp, out=out)

        self.assertNotEqual(code, 0)
        self.assertIn(".claude-plugin/plugin.json", out.getvalue())
        self.assertIn("name", out.getvalue())

    def test_malformed_json_fails_with_file_path(self):
        import validate_manifests

        path = self.tmp / ".codex-plugin" / "plugin.json"
        path.write_text("{not json", encoding="utf-8")

        out = io.StringIO()
        code = validate_manifests.validate(root=self.tmp, out=out)

        self.assertNotEqual(code, 0)
        self.assertIn(".codex-plugin/plugin.json", out.getvalue())
        self.assertIn("invalid JSON", out.getvalue())

    def test_host_package_manifest_drift_fails(self):
        import validate_manifests

        path = self.tmp / "hosts" / "codex" / "plugins" / "shaper" / ".codex-plugin" / "plugin.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["version"] = "9.9.9"
        path.write_text(json.dumps(payload), encoding="utf-8")

        out = io.StringIO()
        code = validate_manifests.validate(root=self.tmp, out=out)

        self.assertNotEqual(code, 0)
        self.assertIn("version", out.getvalue())
        self.assertIn("hosts/codex/plugins/shaper/.codex-plugin/plugin.json", out.getvalue())

    def test_invalid_codex_marketplace_source_shape_reports_error(self):
        import validate_manifests

        path = self.tmp / "hosts" / "codex" / ".agents" / "plugins" / "marketplace.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["plugins"][0]["source"] = None
        path.write_text(json.dumps(payload), encoding="utf-8")

        out = io.StringIO()
        code = validate_manifests.validate(root=self.tmp, out=out)

        self.assertNotEqual(code, 0)
        self.assertIn("source.path", out.getvalue())

    def test_failure_summary_counts_valid_manifests_not_errors(self):
        import validate_manifests

        path = self.tmp / ".claude-plugin" / "plugin.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.pop("name")
        payload.pop("version")
        path.write_text(json.dumps(payload), encoding="utf-8")

        out = io.StringIO()
        code = validate_manifests.validate(root=self.tmp, out=out)

        self.assertNotEqual(code, 0)
        self.assertIn("5/6 manifest(s) valid", out.getvalue())


if __name__ == "__main__":
    unittest.main()
