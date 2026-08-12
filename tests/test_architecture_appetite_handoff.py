"""TDD tests for jig spec slice 008-02 (architecture-appetite-handoff).

Covers:
  AC1: templates/release-plan.md "## JIG Handoff" carries an
       "### Architecture appetite" subsection with the three ceiling-shaped
       elements (investment posture as a strict upper bound, over-investment
       no-gos, spike pointer) and no "proposed shape" / "leanest architecture"
       slot, while preserving the existing handoff bullets.
  AC2: skills/shape-release/SKILL.md elicits architecture appetite in
       "Inputs to gather" and states the load-bearing guardrail in
       "## Boundaries": appetite/no-gos/spike-pointer only, upper-bound-only
       posture, and no ADR / module boundary / mechanism / positive design.
  AC3: the field degrades safely -- TBD when nothing is supplied, never
       fabricated, never escalated into a design.
  AC4: a cross-reference records that architecture appetite is the
       prospective half and jig's leanness/YAGNI review lens is the
       retrospective complement, enforced at jig review, not by shaper.
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


class ArchitectureAppetiteTemplateTests(unittest.TestCase):
    """AC1."""

    def test_jig_handoff_carries_three_element_architecture_appetite(self):
        template = ROOT / "templates" / "release-plan.md"
        self.assertTrue(template.is_file(), "missing release-plan template")
        text = _read(template)

        handoff = _section(text, "JIG Handoff")

        # existing bullets preserved
        self.assertIn("- Candidate JIG specs or slices:", handoff)
        self.assertIn("- New JIG work to draft:", handoff)
        self.assertIn("- Patch-ready instructions, if any:", handoff)
        self.assertIn("- Non-mutating notes:", handoff)

        # new nested subsection
        self.assertIn("### Architecture appetite", handoff)
        lowered = handoff.lower()

        # (i) investment posture -- strict upper bound, never a floor
        self.assertIn("investment posture", lowered)
        self.assertIn("upper bound", lowered)
        self.assertIn('"at most"', lowered)
        self.assertIn('never "at least"', lowered)

        # (ii) over-investment no-gos
        self.assertIn("over-investment no-gos", lowered)
        self.assertIn("over-builds to refuse", lowered)

        # (iii) spike pointer
        self.assertIn("spike", lowered)
        self.assertIn("retire early", lowered)

        # seeded with TBD markers, no fabricated content
        self.assertRegex(handoff, r"Investment posture.*_TBD_")
        self.assertRegex(handoff, r"Over-investment no-gos.*_TBD_")
        self.assertRegex(handoff, r"Spike.*_TBD_")

    def test_jig_handoff_has_no_positive_shape_slot(self):
        template = ROOT / "templates" / "release-plan.md"
        text = _read(template)
        handoff = _section(text, "JIG Handoff")
        lowered = handoff.lower()

        self.assertNotIn("leanest architecture", lowered)
        self.assertNotIn("proposed shape", lowered)


class ArchitectureAppetiteSkillElicitationTests(unittest.TestCase):
    """AC2."""

    def test_inputs_to_gather_lists_architecture_appetite(self):
        skill = ROOT / "skills" / "shape-release" / "SKILL.md"
        self.assertTrue(skill.is_file(), "missing shape-release skill")
        text = _read(skill)

        inputs_match = re.search(
            r"(?ms)^## Inputs to gather\n.*?(?=^## |\Z)", text
        )
        self.assertIsNotNone(inputs_match, "missing 'Inputs to gather' section")
        inputs_lowered = inputs_match.group(0).lower()
        self.assertIn("architecture appetite", inputs_lowered)
        self.assertIn("investment posture", inputs_lowered)

    def test_boundaries_states_upper_bound_only_and_no_design_rule(self):
        skill = ROOT / "skills" / "shape-release" / "SKILL.md"
        text = _read(skill)

        boundaries_match = re.search(
            r"(?ms)^## Boundaries\n.*?(?=^## |\Z)", text
        )
        self.assertIsNotNone(boundaries_match, "missing '## Boundaries' section")
        boundaries_lowered = boundaries_match.group(0).lower()

        self.assertIn("architecture appetite", boundaries_lowered)
        self.assertIn("upper bound", boundaries_lowered)
        self.assertIn("never a floor or a minimum", boundaries_lowered)
        self.assertIn("must not write an adr", boundaries_lowered)
        self.assertIn("name a module boundary", boundaries_lowered)
        self.assertIn("name a mechanism", boundaries_lowered)
        self.assertIn("positive design", boundaries_lowered)


class ArchitectureAppetiteCrossReferenceTests(unittest.TestCase):
    """AC4."""

    def test_template_or_skill_cross_references_jig_retrospective_lens(self):
        template = ROOT / "templates" / "release-plan.md"
        skill = ROOT / "skills" / "shape-release" / "SKILL.md"
        combined = (_read(template) + "\n" + _read(skill)).lower()

        self.assertIn("prospective", combined)
        self.assertIn("retrospective", combined)
        self.assertIn("leanness/yagni", combined)
        self.assertIn("jig review", combined)


class ArchitectureAppetiteScriptTests(unittest.TestCase):
    """AC3."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-arch-appetite-"))
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

    def test_create_without_arch_flags_leaves_tbd_markers(self):
        result = self._run(
            [
                "--repo",
                str(self.tmp),
                "--slug",
                "no-arch-appetite",
                "--problem",
                "Something needs shaping.",
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = self.tmp / "docs" / "releases" / "no-arch-appetite.md"
        handoff = _section(_read(plan), "JIG Handoff")
        self.assertIn("### Architecture appetite", handoff)
        self.assertRegex(handoff, r"Investment posture.*_TBD_")
        self.assertRegex(handoff, r"Over-investment no-gos.*_TBD_")
        self.assertRegex(handoff, r"Spike.*_TBD_")

    def test_create_with_arch_flags_writes_values(self):
        result = self._run(
            [
                "--repo",
                str(self.tmp),
                "--slug",
                "with-arch-appetite",
                "--arch-posture",
                "thin-and-deletable",
                "--arch-no-go",
                "no general conflict engine",
                "--arch-spike",
                "whether offline writes can replay without data loss",
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = self.tmp / "docs" / "releases" / "with-arch-appetite.md"
        handoff = _section(_read(plan), "JIG Handoff")
        self.assertIn("thin-and-deletable", handoff)
        self.assertIn("no general conflict engine", handoff)
        self.assertIn(
            "whether offline writes can replay without data loss", handoff
        )
        self.assertNotIn("_TBD_", handoff)

    def test_refine_appends_no_go_preserving_prior_wording(self):
        create = self._run(
            [
                "--repo",
                str(self.tmp),
                "--slug",
                "refine-arch-appetite",
                "--arch-posture",
                "thin-and-deletable",
                "--arch-no-go",
                "no general conflict engine",
            ]
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        refine = self._run(
            [
                "--repo",
                str(self.tmp),
                "--slug",
                "refine-arch-appetite",
                "--arch-no-go",
                "no pluggable-backend abstraction",
            ]
        )
        self.assertEqual(refine.returncode, 0, refine.stderr)

        plan = self.tmp / "docs" / "releases" / "refine-arch-appetite.md"
        handoff = _section(_read(plan), "JIG Handoff")
        # prior wording preserved
        self.assertIn("thin-and-deletable", handoff)
        self.assertIn("no general conflict engine", handoff)
        # new no-go appended
        self.assertIn("no pluggable-backend abstraction", handoff)

    def test_refine_jig_handoff_and_arch_flag_together_preserves_both(self):
        # Reconciliation (008-02 craft blocker): a refine that passes a plain
        # --jig-handoff bullet AND an arch flag must preserve BOTH. The handoff
        # bullet must be inserted before the nested ### Architecture appetite
        # subsection, so the subsequent arch-appetite rewrite cannot delete it.
        create = self._run(
            ["--repo", str(self.tmp), "--slug", "combined-refine",
             "--arch-posture", "thin-and-deletable"]
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        refine = self._run(
            ["--repo", str(self.tmp), "--slug", "combined-refine",
             "--jig-handoff", "Draft spec 099 after the cutline is accepted.",
             "--arch-no-go", "no second persistence store"]
        )
        self.assertEqual(refine.returncode, 0, refine.stderr)

        text = _read(self.tmp / "docs" / "releases" / "combined-refine.md")
        handoff = _section(text, "JIG Handoff")
        self.assertIn("Draft spec 099 after the cutline is accepted.", handoff)
        self.assertIn("no second persistence store", handoff)
        self.assertIn("thin-and-deletable", handoff)
        # the handoff bullet precedes the arch subsection (not swallowed by it)
        self.assertLess(
            handoff.index("Draft spec 099"),
            handoff.index("### Architecture appetite"),
        )


if __name__ == "__main__":
    unittest.main()
