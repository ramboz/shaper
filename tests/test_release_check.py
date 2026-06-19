import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_release_plan(
    root: Path,
    slug: str = "release-check",
    *,
    appetite: str = "One maintainer day to ship the JIG-only release-check report.",
    cutline_include: str = "release-check report",
    cutline_defer: str = "",
    risks: str = "- Risk: none identified.",
    no_gos: str = "- No automatic release.",
    handoff: str = "- [Spec 010](../specs/010-release/spec.md)",
    release_check_criteria: str = (
        "- All in-scope JIG work is DONE before recommending ship."
    ),
    extension: str = "",
) -> Path:
    path = root / "docs" / "releases" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = [
        "# Release Plan: Release Check",
        "",
        "## Status",
        "",
        "`committed`",
        "",
        "## Problem / Baseline",
        "",
        "- A maintainer needs an advisory ship/cut/stop call.",
        "",
        "## Appetite",
        "",
        f"- {appetite}",
        "",
        "## Solution Outline",
        "",
        "- Read release criteria and JIG status, then recommend.",
        "",
        "## Risks / Rabbit Holes",
        "",
        risks,
        "",
        "## No-Gos",
        "",
        no_gos,
        "",
        "## Cutline",
        "",
        "### Include",
        "",
        "| Item | Evidence | Rationale |",
        "|---|---|---|",
        f"| {cutline_include} | release plan | current appetite |",
        "",
        "### Defer",
        "",
        "| Item | Evidence | Rationale |",
        "|---|---|---|",
        f"| {cutline_defer or '_None_'} | release plan | outside appetite |",
        "",
        "### Split",
        "",
        "| Item | Evidence | Rationale |",
        "|---|---|---|",
        "| _None_ | _-_ | _-_ |",
        "",
        "### Risk-First",
        "",
        "| Item | Evidence | Rationale |",
        "|---|---|---|",
        "| _None_ | _-_ | _-_ |",
        "",
        "## JIG Handoff",
        "",
        handoff,
        "",
        "## Release-Check Criteria",
        "",
        release_check_criteria,
        "",
    ]
    if extension:
        sections.extend(["## Extension", "", extension, ""])
    path.write_text("\n".join(sections), encoding="utf-8")
    return path


def _write_board(root: Path, rows: list[tuple[str, str, str]]) -> None:
    specs = root / "docs" / "specs"
    specs.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Spec Status Board",
        "",
        "| Spec | Slice | Status | Notes |",
        "|------|-------|--------|-------|",
    ]
    for spec, slice_label, status in rows:
        lines.append(f"| [{spec}]({spec}/spec.md) | {slice_label} | {status} |  |")
    (specs / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_spec(root: Path, slug: str, title: str, body: str) -> Path:
    path = root / "docs" / "specs" / slug / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                "status: DRAFT",
                "---",
                "",
                f"# {title}",
                "",
                body.rstrip(),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


class ReleaseCheckWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-release-check-"))
        self.script = ROOT / "skills" / "release-check" / "scripts" / "release_check.py"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, slug: str = "release-check") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.script), "--repo", str(self.tmp), "--release", slug],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_recommends_ship_when_in_scope_work_done_and_no_open_risks(self):
        _write_release_plan(self.tmp)
        _write_board(self.tmp, [("010-release", "010-01 - release-check report", "DONE")])
        _write_spec(
            self.tmp,
            "010-release",
            "Release Check",
            "## Acceptance Criteria\n\n1. Produce a release-check report.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Recommendation: ship", result.stdout)
        self.assertIn("## Open Risks", result.stdout)
        self.assertIn("JIG files left untouched", result.stdout)

    def test_recommends_cut_scope_when_in_scope_work_partially_done(self):
        _write_release_plan(
            self.tmp,
            handoff=(
                "- [Spec 010](../specs/010-release/spec.md)\n"
                "- [Spec 011](../specs/011-extra/spec.md)"
            ),
        )
        _write_board(
            self.tmp,
            [
                ("010-release", "010-01 - release-check report", "DONE"),
                ("011-extra", "011-01 - extra polish", "IN_PROGRESS"),
            ],
        )
        _write_spec(
            self.tmp,
            "010-release",
            "Release Check",
            "## Acceptance Criteria\n\n1. Produce a release-check report.\n",
        )
        _write_spec(
            self.tmp,
            "011-extra",
            "Extra",
            "## Acceptance Criteria\n\n1. Add extra polish.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Recommendation: cut scope", result.stdout)
        self.assertIn("011-01 - extra polish", result.stdout)

    def test_cut_scope_rationale_also_flags_co_occurring_unresolved_risk(self):
        _write_release_plan(
            self.tmp,
            handoff=(
                "- [Spec 010](../specs/010-release/spec.md)\n"
                "- [Spec 011](../specs/011-extra/spec.md)"
            ),
            risks=(
                "- Risk: data format may shift.\n"
                "  - Retirement path: TBD before implementation."
            ),
        )
        _write_board(
            self.tmp,
            [
                ("010-release", "010-01 - release-check report", "DONE"),
                ("011-extra", "011-01 - extra polish", "IN_PROGRESS"),
            ],
        )
        _write_spec(
            self.tmp,
            "010-release",
            "Release Check",
            "## Acceptance Criteria\n\n1. Produce a release-check report.\n",
        )
        _write_spec(
            self.tmp,
            "011-extra",
            "Extra",
            "## Acceptance Criteria\n\n1. Add extra polish.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Recommendation: cut scope", result.stdout)
        self.assertIn("Unresolved rabbit holes also remain", result.stdout)
        self.assertIn("TBD before implementation", result.stdout)

    def test_recommends_stop_and_reshape_on_no_go_conflict(self):
        _write_release_plan(self.tmp, no_gos="- No issue-system replacement.")
        _write_board(
            self.tmp,
            [("010-release", "010-01 - issue-system replacement", "IN_PROGRESS")],
        )
        _write_spec(
            self.tmp,
            "010-release",
            "Issue System Replacement",
            "## Acceptance Criteria\n\n"
            "1. Build a shaper-managed issue-system replacement.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Recommendation: stop and re-shape", result.stdout)
        self.assertIn("no-go", result.stdout.lower())

    def test_related_but_non_conflicting_no_go_does_not_block_ship(self):
        # A no-go that shares vocabulary with in-scope work ("release") but
        # names a distinct capability ("dashboard") must not spuriously fire a
        # no-go conflict on unrelated DONE work.
        _write_release_plan(self.tmp, no_gos="- No release dashboard.")
        _write_board(self.tmp, [("010-release", "010-01 - release-check report", "DONE")])
        _write_spec(
            self.tmp,
            "010-release",
            "Release Check",
            "## Acceptance Criteria\n\n1. Produce a release-check report.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("No-go conflict", result.stdout)
        self.assertIn("## Recommendation: ship", result.stdout)

    def test_recommends_extend_only_with_explicit_rationale(self):
        _write_release_plan(
            self.tmp,
            handoff=(
                "- [Spec 010](../specs/010-release/spec.md)\n"
                "- [Spec 011](../specs/011-extra/spec.md)"
            ),
            extension=(
                "- Extension approved: the security review must land in this "
                "release and is worth one extra day."
            ),
        )
        _write_board(
            self.tmp,
            [
                ("010-release", "010-01 - release-check report", "DONE"),
                ("011-extra", "011-01 - security review", "IN_PROGRESS"),
            ],
        )
        _write_spec(
            self.tmp,
            "010-release",
            "Release Check",
            "## Acceptance Criteria\n\n1. Produce a release-check report.\n",
        )
        _write_spec(
            self.tmp,
            "011-extra",
            "Security Review",
            "## Acceptance Criteria\n\n1. Complete the security review.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "## Recommendation: extend only with explicit rationale", result.stdout
        )
        self.assertIn("Extension approved", result.stdout)

    def test_reads_release_criteria(self):
        _write_release_plan(
            self.tmp,
            appetite="Two maintainer days for the release-check report.",
            no_gos="- No automatic release.",
            release_check_criteria="- Ship only when risks are retired.",
        )
        _write_board(self.tmp, [("010-release", "010-01 - release-check report", "DONE")])
        _write_spec(
            self.tmp,
            "010-release",
            "Release Check",
            "## Acceptance Criteria\n\n1. Produce a release-check report.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Release Criteria Read", result.stdout)
        self.assertIn("Two maintainer days", result.stdout)
        self.assertIn("No automatic release", result.stdout)
        self.assertIn("Ship only when risks are retired", result.stdout)

    def test_servo_signals_reported_as_not_evaluated(self):
        _write_release_plan(self.tmp)
        _write_board(self.tmp, [("010-release", "010-01 - release-check report", "DONE")])
        _write_spec(
            self.tmp,
            "010-release",
            "Release Check",
            "## Acceptance Criteria\n\n1. Produce a release-check report.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Servo signals: not evaluated", result.stdout)
        self.assertNotIn("servo unavailable", result.stdout.lower())

    def test_open_risks_surfaced_and_block_ship(self):
        _write_release_plan(
            self.tmp,
            risks=(
                "- Risk: data format may not map cleanly.\n"
                "  - Retirement path: TBD before implementation."
            ),
        )
        _write_board(self.tmp, [("010-release", "010-01 - release-check report", "DONE")])
        _write_spec(
            self.tmp,
            "010-release",
            "Release Check",
            "## Acceptance Criteria\n\n1. Produce a release-check report.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Open Risks", result.stdout)
        self.assertIn("TBD before implementation", result.stdout)
        self.assertNotIn("## Recommendation: ship", result.stdout)

    def test_does_not_mutate_jig_lifecycle_state(self):
        _write_release_plan(self.tmp, no_gos="- No issue-system replacement.")
        _write_board(
            self.tmp,
            [("010-release", "010-01 - issue-system replacement", "IN_PROGRESS")],
        )
        _write_spec(
            self.tmp,
            "010-release",
            "Issue System Replacement",
            "---\nstatus: IN_PROGRESS\n---\n\n"
            "## Acceptance Criteria\n\n1. Build an issue-system replacement.\n",
        )
        specs = self.tmp / "docs" / "specs"
        before = {
            path.relative_to(specs).as_posix(): _read(path)
            for path in specs.rglob("*.md")
        }

        result = self._run()

        after = {
            path.relative_to(specs).as_posix(): _read(path)
            for path in specs.rglob("*.md")
        }
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, before)
        self.assertIn("## Advisory Only", result.stdout)
        self.assertIn("JIG files left untouched", result.stdout)
        self.assertNotIn("workflow.py transition", result.stdout)

    def test_no_jig_artifacts_degrades_gracefully(self):
        _write_release_plan(self.tmp)

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No JIG specs/status board were found.", result.stdout)
        self.assertIn("Servo signals: not evaluated", result.stdout)
        self.assertIn("JIG files left untouched", result.stdout)

    def test_release_plan_missing_returns_error(self):
        result = self._run("does-not-exist")

        self.assertEqual(result.returncode, 1)
        self.assertIn("Release plan missing:", result.stdout)

    def test_release_paths_outside_repo_are_not_read(self):
        outside = self.tmp.parent / "outside-release-check.md"
        self.addCleanup(outside.unlink, missing_ok=True)
        outside.write_text(
            "# Release Plan: Outside\n\n## Appetite\n\n- outside secret.\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                str(self.script),
                "--repo",
                str(self.tmp),
                "--release",
                str(outside),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Release plan missing:", result.stdout)
        self.assertNotIn("outside secret", result.stdout)


if __name__ == "__main__":
    unittest.main()
