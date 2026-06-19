import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    start = text.index(f"## {heading}")
    next_start = text.find("\n## ", start + 1)
    return text[start:] if next_start == -1 else text[start:next_start]


def _write_plan(
    root: Path,
    slug: str,
    status: str,
    title: str,
    problem: str,
    handoff: str = "",
) -> Path:
    path = root / "docs" / "releases" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# Release Plan: {title}",
                "",
                "## Status",
                "",
                f"`{status}`",
                "",
                "## Problem / Baseline",
                "",
                f"- {problem}",
                "",
                "## JIG Handoff",
                "",
                handoff or "- No JIG handoff linked yet.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


class ReleaseSlateWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-release-slate-"))
        self.script = ROOT / "skills" / "release-slate" / "scripts" / "release_slate.py"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.script), "--repo", str(self.tmp)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_skill_and_helper_discover_release_plans_and_existing_slate(self):
        skill = ROOT / "skills" / "release-slate" / "SKILL.md"
        _write_plan(
            self.tmp,
            "first-slate",
            "candidate",
            "First Slate",
            "A compact slate is needed before release decisions drift.",
        )
        slate = self.tmp / "docs" / "releases" / "README.md"
        slate.write_text("# Old Slate\n\nmanual note\n", encoding="utf-8")

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(skill.is_file(), "missing release-slate skill")
        skill_text = _read(skill)
        self.assertIn("docs/releases/*.md", skill_text)
        self.assertIn("docs/releases/README.md", skill_text)
        self.assertIn("release plans discovered: 1", result.stdout.lower())
        self.assertIn("existing slate read: yes", result.stdout.lower())
        text = _read(slate)
        self.assertIn("[First Slate](first-slate.md)", text)
        self.assertNotIn("manual note", text)

    def test_slate_groups_candidate_committed_shipping_shipped_and_dropped(self):
        plans = {
            "candidate": "Candidate release still needs a decision.",
            "committed": "Committed release is accepted for handoff.",
            "shipping": "Shipping release is being finished.",
            "shipped": "Shipped release remains recent context.",
            "dropped": "Dropped release still explains a no-go.",
        }
        for status, problem in plans.items():
            _write_plan(
                self.tmp,
                f"{status}-plan",
                status,
                f"{status.title()} Plan",
                problem,
            )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        text = _read(self.tmp / "docs" / "releases" / "README.md")
        for heading in ("Candidate", "Committed", "Shipping", "Shipped", "Dropped"):
            self.assertIn(f"## {heading}", text)
        for status in plans:
            section = _section(text, "Shipped" if status == "shipped" else status.title())
            self.assertIn(f"[{status.title()} Plan]({status}-plan.md)", section)

    def test_status_parser_uses_actual_status_not_allowed_status_catalog(self):
        plan = _write_plan(
            self.tmp,
            "catalog-status",
            "committed",
            "Catalog Status",
            "A shape-release style status section includes every allowed status.",
        )
        text = _read(plan)
        text = text.replace(
            "`committed`\n",
            (
                "`committed`\n\n"
                "Allowed statuses: `candidate`, `committed`, `shipping`, "
                "`shipped`, `dropped`.\n"
                "Do not move a plan from `candidate` to `committed` without "
                "an explicit user decision.\n"
            ),
        )
        plan.write_text(text, encoding="utf-8")

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        slate = _read(self.tmp / "docs" / "releases" / "README.md")
        self.assertIn("[Catalog Status](catalog-status.md)", _section(slate, "Committed"))
        self.assertNotIn("[Catalog Status](catalog-status.md)", _section(slate, "Candidate"))

    def test_update_does_not_preserve_backlog_priority_or_status_board_rows(self):
        _write_plan(
            self.tmp,
            "real-candidate",
            "candidate",
            "Real Candidate",
            "The one current release plan should remain.",
        )
        slate = self.tmp / "docs" / "releases" / "README.md"
        slate.write_text(
            "\n".join(
                [
                    "# Release Slate",
                    "",
                    "## Backlog",
                    "",
                    "| Priority | Release plan | JIG status |",
                    "|---|---|---|",
                    "| P1 | stale idea | DONE |",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        text = _read(slate)
        lowered = text.lower()
        self.assertIn("[Real Candidate](real-candidate.md)", text)
        self.assertNotIn("stale idea", lowered)
        self.assertNotIn("## backlog", lowered)
        self.assertNotIn("| priority |", lowered)
        self.assertNotIn("| jig status |", lowered)

    def test_handoff_links_to_jig_notes_without_copying_lifecycle_state(self):
        _write_plan(
            self.tmp,
            "handoff-links",
            "committed",
            "Handoff Links",
            "A release plan should point at JIG notes without mirroring state.",
            "- [Spec 010](../specs/010-core/spec.md) receives the implementation handoff.",
        )
        specs = self.tmp / "docs" / "specs"
        specs.mkdir(parents=True)
        (specs / "README.md").write_text(
            "\n".join(
                [
                    "# Spec Status Board",
                    "",
                    "| Spec | Slice | Status | Notes |",
                    "|---|---|---|---|",
                    "| [010-core](010-core/spec.md) | 010-01 - core | **DONE** |  |",
                    "| [011-later](011-later/spec.md) | 011-01 - later | IN_PROGRESS |  |",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        text = _read(self.tmp / "docs" / "releases" / "README.md")
        self.assertIn("[Spec 010](../specs/010-core/spec.md)", text)
        self.assertNotIn("DONE", text)
        self.assertNotIn("IN_PROGRESS", text)
        self.assertNotIn("| JIG status |", text)

    def test_empty_state_creates_slate_without_invented_work(self):
        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("release plans discovered: 0", result.stdout.lower())
        slate = self.tmp / "docs" / "releases" / "README.md"
        self.assertTrue(slate.is_file(), "missing empty release slate")
        text = _read(slate)
        self.assertIn("No release plans were found.", text)
        for heading in ("Candidate", "Committed", "Shipping", "Shipped", "Dropped"):
            section = _section(text, heading)
            self.assertIn("_None yet_", section)
        self.assertNotIn("TBD", text)
        self.assertNotIn("example", text.lower())


class HostPackageReleaseSlateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-release-slate-hosts-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_all_copies_release_slate_assets_to_both_hosts(self):
        import build_host_packages

        out = io.StringIO()
        code = build_host_packages.build_all(
            source_root=ROOT,
            hosts_root=self.tmp,
            out=out,
        )

        self.assertEqual(code, 0, out.getvalue())
        for base in (
            self.tmp / "claude",
            self.tmp / "codex" / "plugins" / "shaper",
        ):
            with self.subTest(base=base):
                self.assertTrue((base / "skills" / "release-slate" / "SKILL.md").is_file())
                self.assertTrue(
                    (
                        base
                        / "skills"
                        / "release-slate"
                        / "scripts"
                        / "release_slate.py"
                    ).is_file()
                )


if __name__ == "__main__":
    unittest.main()
