"""TDD tests for jig spec slice 008-01 (vertical-scope-outline).

Covers:
  AC1: templates/release-plan.md carries an ordered, thinnest-first vertical
       scope subsection inside "## Solution Outline".
  AC2: skills/shape-release/SKILL.md elicits the vertical-scope decomposition
       and writes it into the plan, leaving a TBD marker when omitted.
  AC3: the skill instructs that each scope must deliver end-to-end value
       (anti-horizontal-phasing) and that "just the data model" / "just the
       parser" scopes must be re-split.
  AC4: skills/shape-release/scripts/shape_release.py round-trips a repeatable
       --vertical-scope argument: TBD on create with none, ordered writes on
       create with scopes, and append-not-overwrite on refine.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    pattern = re.compile(rf"(?ms)^## {re.escape(heading)}\n.*?(?=^## |\Z)")
    match = pattern.search(text)
    assert match, f"missing section: {heading}"
    return match.group(0)


class VerticalScopeTemplateTests(unittest.TestCase):
    """AC1."""

    def test_solution_outline_carries_ordered_thinnest_first_vertical_scopes(self):
        template = ROOT / "templates" / "release-plan.md"
        self.assertTrue(template.is_file(), "missing release-plan template")
        text = _read(template)

        solution_outline = _section(text, "Solution Outline")

        # existing bullets preserved
        self.assertIn("- Proposed shape:", solution_outline)
        self.assertIn("- Main user-facing path:", solution_outline)
        self.assertIn("- Important non-goals:", solution_outline)

        # new subsection nested inside Solution Outline
        self.assertIn("### Vertical Scopes (delivery order)", solution_outline)
        lowered = solution_outline.lower()
        self.assertIn("thinnest", lowered)
        self.assertIn("demoable", lowered)

        # seeded with a TBD marker as an ordered-list entry
        self.assertRegex(solution_outline, r"(?m)^1\.\s+.*TBD")


class VerticalScopeSkillElicitationTests(unittest.TestCase):
    """AC2."""

    def test_inputs_to_gather_lists_vertical_scope_decomposition(self):
        skill = ROOT / "skills" / "shape-release" / "SKILL.md"
        self.assertTrue(skill.is_file(), "missing shape-release skill")
        text = _read(skill)
        lowered = text.lower()

        inputs_match = re.search(
            r"(?ms)^## Inputs to gather\n.*?(?=^## |\Z)", text
        )
        self.assertIsNotNone(inputs_match, "missing 'Inputs to gather' section")
        inputs_lowered = inputs_match.group(0).lower()
        self.assertIn("vertical scope", inputs_lowered)
        self.assertIn("thinnest", inputs_lowered)

        self.assertIn("vertical scope", lowered)

    def test_writing_or_refining_steps_write_scopes_and_leave_tbd_when_omitted(self):
        skill = ROOT / "skills" / "shape-release" / "SKILL.md"
        text = _read(skill)

        steps_match = re.search(
            r"(?ms)^## Writing or refining a plan\n.*?(?=^## |\Z)", text
        )
        self.assertIsNotNone(steps_match, "missing 'Writing or refining a plan' section")
        steps_lowered = steps_match.group(0).lower()

        self.assertIn("vertical scope", steps_lowered)
        self.assertIn("tbd", steps_lowered)
        # never a fabricated ordering
        self.assertIn("fabricated", steps_lowered)


class VerticalScopeAntiHorizontalPhasingTests(unittest.TestCase):
    """AC3."""

    def test_skill_instructs_end_to_end_scopes_and_resplit_horizontal_slices(self):
        skill = ROOT / "skills" / "shape-release" / "SKILL.md"
        text = _read(skill)
        lowered = text.lower()

        self.assertIn("end-to-end", lowered)
        self.assertIn("just the data model", lowered)
        self.assertIn("just the parser", lowered)
        self.assertIn("re-split", lowered)


class VerticalScopeScriptTests(unittest.TestCase):
    """AC4."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-vertical-scope-"))
        self.script = (
            ROOT / "skills" / "shape-release" / "scripts" / "shape_release.py"
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_create_without_vertical_scope_leaves_tbd_marker(self):
        result = self._run(
            [
                "--repo",
                str(self.tmp),
                "--slug",
                "no-scopes",
                "--problem",
                "Something needs shaping.",
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = self.tmp / "docs" / "releases" / "no-scopes.md"
        text = _read(plan)
        solution_outline = _section(text, "Solution Outline")
        self.assertIn("### Vertical Scopes (delivery order)", solution_outline)
        self.assertRegex(solution_outline, r"(?m)^1\.\s+.*TBD")

    def test_create_with_vertical_scopes_writes_ordered_list(self):
        result = self._run(
            [
                "--repo",
                str(self.tmp),
                "--slug",
                "ordered-scopes",
                "--vertical-scope",
                "Walking skeleton: a user can submit and see a raw echo reply.",
                "--vertical-scope",
                "Add real classification behind the same end-to-end path.",
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = self.tmp / "docs" / "releases" / "ordered-scopes.md"
        text = _read(plan)
        solution_outline = _section(text, "Solution Outline")

        self.assertIn(
            "1. Walking skeleton: a user can submit and see a raw echo reply.",
            solution_outline,
        )
        self.assertIn(
            "2. Add real classification behind the same end-to-end path.",
            solution_outline,
        )
        self.assertNotIn("_TBD", solution_outline)
        # order preserved: scope 1 text appears before scope 2 text
        self.assertLess(
            solution_outline.index("Walking skeleton"),
            solution_outline.index("Add real classification"),
        )

    def test_refine_appends_new_scope_and_preserves_user_authored_wording(self):
        create = self._run(
            [
                "--repo",
                str(self.tmp),
                "--slug",
                "refine-scopes",
                "--vertical-scope",
                "Walking skeleton: raw echo end to end.",
            ]
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        refine = self._run(
            [
                "--repo",
                str(self.tmp),
                "--slug",
                "refine-scopes",
                "--vertical-scope",
                "Thicken: real classification behind the same path.",
            ]
        )
        self.assertEqual(refine.returncode, 0, refine.stderr)

        plan = self.tmp / "docs" / "releases" / "refine-scopes.md"
        text = _read(plan)
        solution_outline = _section(text, "Solution Outline")

        self.assertIn(
            "1. Walking skeleton: raw echo end to end.", solution_outline
        )
        self.assertIn(
            "2. Thicken: real classification behind the same path.",
            solution_outline,
        )

    def test_refine_does_not_duplicate_an_already_present_scope(self):
        # Reconciliation (008-01 craft nit 3): re-supplying an existing scope
        # must be a no-op, not a duplicate/renumber.
        scope = "Walking skeleton: raw echo end to end."
        create = self._run(
            ["--repo", str(self.tmp), "--slug", "dedupe-scopes",
             "--vertical-scope", scope]
        )
        self.assertEqual(create.returncode, 0, create.stderr)
        refine = self._run(
            ["--repo", str(self.tmp), "--slug", "dedupe-scopes",
             "--vertical-scope", scope]
        )
        self.assertEqual(refine.returncode, 0, refine.stderr)

        plan = self.tmp / "docs" / "releases" / "dedupe-scopes.md"
        solution_outline = _section(_read(plan), "Solution Outline")
        self.assertEqual(
            solution_outline.count(scope), 1, "scope was duplicated on refine"
        )
        self.assertNotIn("2. ", solution_outline)

    def test_scopes_create_solution_outline_when_section_absent(self):
        # Reconciliation (008-01 craft nit 2): a hand-authored plan with no
        # Solution Outline must not silently swallow --vertical-scope input;
        # the section is created instead.
        releases = self.tmp / "docs" / "releases"
        releases.mkdir(parents=True)
        (releases / "hand-authored.md").write_text(
            "# Release Plan: Hand Authored\n\n## Status\n\n`candidate`\n",
            encoding="utf-8",
        )
        result = self._run(
            ["--repo", str(self.tmp), "--slug", "hand-authored",
             "--vertical-scope", "Walking skeleton: end to end."]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        text = _read(releases / "hand-authored.md")
        self.assertIn("## Solution Outline", text)
        self.assertIn("### Vertical Scopes (delivery order)", text)
        self.assertIn("1. Walking skeleton: end to end.", text)


if __name__ == "__main__":
    unittest.main()
