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


def _squash(text: str) -> str:
    return " ".join(text.lower().replace("`", "").split())


class ReleasePlanHandoffContractTests(unittest.TestCase):
    def test_release_plan_template_covers_required_sections(self):
        template = ROOT / "templates" / "release-plan.md"

        self.assertTrue(template.is_file(), "missing release-plan template")
        text = _read(template)

        for heading in (
            "## Status",
            "## Problem / Baseline",
            "## Appetite",
            "## Solution Outline",
            "## Risks / Rabbit Holes",
            "## No-Gos",
            "## Cutline",
            "## JIG Handoff",
            "## Release-Check Criteria",
        ):
            self.assertIn(heading, text)
        for status in ("candidate", "committed", "shipping", "shipped", "dropped"):
            self.assertIn(status, text)

    def test_shape_release_skill_elicits_fields_without_inventing_intent(self):
        skill = ROOT / "skills" / "shape-release" / "SKILL.md"

        self.assertTrue(skill.is_file(), "missing shape-release skill")
        text = _read(skill)
        lowered = text.lower()

        self.assertIn("docs/releases/<slug>.md", text)
        self.assertIn("do not invent product intent", lowered)
        self.assertIn("use the user's words", lowered)
        for field in (
            "problem/baseline",
            "appetite",
            "solution outline",
            "risks/rabbit holes",
            "no-gos",
            "release-check criteria",
            "jig handoff",
        ):
            self.assertIn(field, lowered)

    def test_cutline_skill_reads_jig_without_mutating_lifecycle_state(self):
        skill = ROOT / "skills" / "cutline" / "SKILL.md"

        self.assertTrue(skill.is_file(), "missing cutline skill")
        text = _read(skill)
        lowered = text.lower()
        squashed = _squash(text)

        self.assertIn("docs/specs/README.md", text)
        self.assertIn("docs/specs/*", text)
        for recommendation in ("include", "defer", "split", "risk-first"):
            self.assertIn(recommendation, lowered)
        for boundary in (
            "must not edit jig spec lifecycle state",
            "must not run workflow.py transition",
            "non-mutating",
        ):
            self.assertIn(boundary, squashed)

    def test_missing_sibling_tools_degrade_gracefully(self):
        cutline = ROOT / "skills" / "cutline" / "SKILL.md"
        shape_release = ROOT / "skills" / "shape-release" / "SKILL.md"

        self.assertTrue(cutline.is_file(), "missing cutline skill")
        self.assertTrue(shape_release.is_file(), "missing shape-release skill")
        combined = f"{_read(cutline)}\n{_read(shape_release)}".lower()

        self.assertIn("no jig specs/status board were found", combined)
        self.assertIn("leave jig files untouched", combined)
        self.assertIn("servo signals are absent", combined)
        self.assertIn("do not block", combined)

    def test_release_slate_is_compact_current_and_not_a_backlog(self):
        slate = ROOT / "docs" / "releases" / "README.md"

        self.assertTrue(slate.is_file(), "missing release slate")
        text = _read(slate)
        lowered = text.lower()
        squashed = _squash(text)

        for heading in (
            "## Candidate",
            "## Committed",
            "## Shipping",
            "## Shipped",
            "## Dropped",
        ):
            self.assertIn(heading, text)
        self.assertIn("not a backlog", squashed)
        self.assertIn("not a second jig status board", squashed)
        self.assertNotIn("| priority |", lowered)
        self.assertNotIn("| jig status |", lowered)

    def test_relationship_docs_explain_sibling_boundaries(self):
        readme = _read(ROOT / "README.md")
        lowered = _squash(readme)

        for phrase in (
            "owns implementation workflow and spec lifecycle",
            "owns eval/oracle loops",
            "owns release shaping before implementation starts",
        ):
            self.assertIn(phrase, lowered)
        self.assertNotIn("product skills are not yet implemented", lowered)

    def test_deferred_work_is_explicit_without_creating_a_backlog(self):
        readme = _read(ROOT / "README.md")
        refinement = _read(ROOT / "docs" / "refinement-todo.md")
        combined = _squash(f"{readme}\n{refinement}")

        self.assertIn("scope-audit", combined)
        self.assertIn("implemented by spec 006", combined)
        for deferred in (
            "release-check automation",
            "servo signal consumption",
            "web ui",
            "task boards",
            "sprint planning",
            "estimation",
            "backlog grooming",
            "issue-system replacement",
        ):
            self.assertIn(deferred, combined)


class ReleasePlanHandoffWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-release-flow-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_shape_release_creates_and_refines_plan_from_user_words(self):
        script = ROOT / "skills" / "shape-release" / "scripts" / "shape_release.py"

        result = self._run(
            [
                str(script),
                "--repo",
                str(self.tmp),
                "--slug",
                "handoff-loop",
                "--title",
                "Release plan handoff loop",
                "--status",
                "committed",
                "--problem",
                "Specs multiply before anyone agrees what belongs in release scope.",
                "--appetite",
                "Two focused days, with scope allowed to shrink.",
                "--solution",
                "Create one release plan, draw a cutline, then hand off to JIG.",
                "--risk",
                "The slate turns into a backlog.",
                "--no-go",
                "No task boards or sprint planning.",
                "--cutline",
                "Include only the first non-mutating handoff path.",
                "--cutline",
                "Defer release-check automation.",
                "--criterion",
                "A maintainer can see include/defer/risk-first guidance.",
                "--jig-handoff",
                "Draft implementation specs only after the cutline is accepted.",
            ]
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        plan = self.tmp / "docs" / "releases" / "handoff-loop.md"
        text = _read(plan)
        self.assertIn("`committed`", text)
        self.assertIn("Specs multiply before anyone agrees", text)
        self.assertIn("Two focused days", text)
        self.assertIn("No task boards or sprint planning.", text)
        self.assertIn("### Include", text)
        self.assertIn("### Defer", text)
        self.assertIn("### Split", text)
        self.assertIn("### Risk-First", text)
        self.assertIn("Include only the first non-mutating handoff path.", text)
        self.assertIn("Defer release-check automation.", text)
        self.assertIn("Draft implementation specs only after the cutline", text)

        refine = self._run(
            [
                str(script),
                "--repo",
                str(self.tmp),
                "--slug",
                "handoff-loop",
                "--appetite",
                "One day if JIG specs already exist.",
            ]
        )

        self.assertEqual(refine.returncode, 0, refine.stderr)
        refined = _read(plan)
        self.assertIn("Specs multiply before anyone agrees", refined)
        self.assertIn("Two focused days, with scope allowed to shrink.", refined)
        self.assertIn("One day if JIG specs already exist.", refined)
        self.assertIn("`committed`", refined)
        self.assertNotIn("`candidate`\n\nAllowed statuses", refined)

    def test_happy_path_fixture_covers_plan_cutline_and_slate(self):
        shape_script = ROOT / "skills" / "shape-release" / "scripts" / "shape_release.py"
        cutline_script = ROOT / "skills" / "cutline" / "scripts" / "cutline.py"
        result = self._run(
            [
                str(shape_script),
                "--repo",
                str(self.tmp),
                "--slug",
                "first-handoff",
                "--problem",
                "Raw intent needs a bounded release before specs multiply.",
                "--appetite",
                "One maintainer day.",
                "--solution",
                "Shape the plan, inspect JIG work, and keep the slate compact.",
                "--risk",
                "The release slate becomes a backlog.",
                "--no-go",
                "No issue-system replacement.",
                "--criterion",
                "Cutline recommendations are visible before implementation.",
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        specs = self.tmp / "docs" / "specs"
        specs.mkdir(parents=True)
        (specs / "README.md").write_text(
            "\n".join(
                [
                    "# Spec Status Board",
                    "",
                    "| Spec | Slice | Status | Notes |",
                    "|------|-------|--------|-------|",
                    "| [010-core](010-core/spec.md) | 010-01 - core handoff | **DONE** |  |",
                    "| [011-later](011-later/spec.md) | 011-01 - release check | DRAFT |  |",
                    "| [012-no-go](012-no-go/spec.md) | 012-01 - issue-system replacement | **DONE** |  |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        cutline = self._run(
            [
                str(cutline_script),
                "--repo",
                str(self.tmp),
                "--release",
                "first-handoff",
            ]
        )

        self.assertEqual(cutline.returncode, 0, cutline.stderr)
        self.assertIn("010-01 - core handoff", cutline.stdout)
        self.assertIn("include", cutline.stdout)
        self.assertIn("011-01 - release check", cutline.stdout)
        self.assertIn("defer", cutline.stdout)
        self.assertIn("012-01 - issue-system replacement", cutline.stdout)
        self.assertIn("Matches release no-gos.", cutline.stdout)
        self.assertIn("Release plan inspected: docs/releases/first-handoff.md", cutline.stdout)

        slate_dir = self.tmp / "docs" / "releases"
        slate = _read(ROOT / "docs" / "releases" / "README.md")
        slate = slate.replace(
            "| _None yet_ | _-_ | _-_ |",
            "| [first-handoff](first-handoff.md) | Raw intent needs a bounded release before specs multiply. | Cutline recommends include/defer/no-go boundaries. |",
            1,
        )
        (slate_dir / "README.md").write_text(slate, encoding="utf-8")
        slate = _read(slate_dir / "README.md")
        self.assertIn("## Candidate", slate)
        self.assertIn("## Committed", slate)
        self.assertIn("## Shipping", slate)
        self.assertIn("## Shipped", slate)
        self.assertIn("## Dropped", slate)
        self.assertIn("[first-handoff](first-handoff.md)", slate)
        self.assertNotIn("| Priority |", slate)
        self.assertNotIn("| JIG status |", slate)

    def test_cutline_degrades_without_jig_specs_and_does_not_create_them(self):
        script = ROOT / "skills" / "cutline" / "scripts" / "cutline.py"
        before = sorted(path.relative_to(self.tmp).as_posix() for path in self.tmp.rglob("*"))

        result = self._run([str(script), "--repo", str(self.tmp)])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No JIG specs/status board were found", result.stdout)
        self.assertIn("JIG files left untouched", result.stdout)
        after = sorted(path.relative_to(self.tmp).as_posix() for path in self.tmp.rglob("*"))
        self.assertEqual(after, before)

    def test_cutline_reports_missing_release_plan(self):
        script = ROOT / "skills" / "cutline" / "scripts" / "cutline.py"
        specs = self.tmp / "docs" / "specs"
        specs.mkdir(parents=True)
        (specs / "README.md").write_text(
            "\n".join(
                [
                    "# Spec Status Board",
                    "",
                    "| Spec | Slice | Status | Notes |",
                    "|------|-------|--------|-------|",
                    "| [001-done](001-done/spec.md) | 001-01 - done slice | **DONE** |  |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        result = self._run(
            [str(script), "--repo", str(self.tmp), "--release", "missing-plan"]
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Release plan missing:", result.stdout)
        self.assertIn("docs/releases/missing-plan.md", result.stdout)

    def test_cutline_reads_jig_board_and_leaves_lifecycle_state_untouched(self):
        script = ROOT / "skills" / "cutline" / "scripts" / "cutline.py"
        specs = self.tmp / "docs" / "specs"
        specs.mkdir(parents=True)
        (specs / "README.md").write_text(
            "\n".join(
                [
                    "# Spec Status Board",
                    "",
                    "| Spec | Slice | Status | Notes |",
                    "|------|-------|--------|-------|",
                    "| [001-done](001-done/spec.md) | 001-01 - done slice | **DONE** |  |",
                    "| [002-risk](002-risk/spec.md) | 002-01 - risky slice | IN_PROGRESS (codex/example) |  |",
                    "| [003-draft](003-draft/spec.md) | 003-01 - future slice | DRAFT |  |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        for slug in ("001-done", "002-risk", "003-draft"):
            spec_dir = specs / slug
            spec_dir.mkdir()
            (spec_dir / "spec.md").write_text(
                f"---\nstatus: DRAFT\n---\n# {slug}\n", encoding="utf-8"
            )
        before = {
            path.relative_to(specs).as_posix(): path.read_text(encoding="utf-8")
            for path in specs.rglob("*.md")
        }

        result = self._run([str(script), "--repo", str(self.tmp)])

        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout
        self.assertIn("## Include", output)
        self.assertIn("001-01 - done slice", output)
        self.assertIn("## Risk-First", output)
        self.assertIn("002-01 - risky slice", output)
        self.assertIn("## Defer", output)
        self.assertIn("003-01 - future slice", output)
        self.assertIn("JIG files left untouched", output)
        after = {
            path.relative_to(specs).as_posix(): path.read_text(encoding="utf-8")
            for path in specs.rglob("*.md")
        }
        self.assertEqual(after, before)

    def test_cutline_ignores_jig_board_links_outside_specs_dir(self):
        script = ROOT / "skills" / "cutline" / "scripts" / "cutline.py"
        specs = self.tmp / "docs" / "specs"
        specs.mkdir(parents=True)
        (specs / "README.md").write_text(
            "\n".join(
                [
                    "# Spec Status Board",
                    "",
                    "| Spec | Slice | Status | Notes |",
                    "|------|-------|--------|-------|",
                    "| [escape](../../outside.md) | 999-01 - escape | **DONE** |  |",
                    "| [absolute](/etc/passwd) | 999-02 - absolute | **DONE** |  |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (self.tmp / "outside.md").write_text("outside\n", encoding="utf-8")

        result = self._run([str(script), "--repo", str(self.tmp)])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("JIG files read: docs/specs/README.md", result.stdout)
        self.assertNotIn("outside.md", result.stdout)
        self.assertNotIn("/etc/passwd", result.stdout)


class HostPackageReleaseHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-handoff-hosts-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_all_copies_release_handoff_assets_to_both_hosts(self):
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
                self.assertTrue((base / "skills" / "shape-release" / "SKILL.md").is_file())
                self.assertTrue((base / "skills" / "cutline" / "SKILL.md").is_file())
                self.assertTrue(
                    (
                        base
                        / "skills"
                        / "shape-release"
                        / "scripts"
                        / "shape_release.py"
                    ).is_file()
                )
                self.assertTrue(
                    (base / "skills" / "cutline" / "scripts" / "cutline.py").is_file()
                )
                self.assertTrue((base / "templates" / "release-plan.md").is_file())


if __name__ == "__main__":
    unittest.main()
