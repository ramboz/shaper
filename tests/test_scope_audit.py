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
    slug: str = "scope-audit",
    *,
    appetite: str = "One maintainer day for a text scope-audit report only.",
    cutline_include: str = "scope-audit report",
    cutline_defer: str = "",
    risks: str = "- Risk: none identified.",
    no_gos: str = "- No web UI.",
    handoff: str = "- [Spec 010](../specs/010-scope/spec.md)",
) -> Path:
    path = root / "docs" / "releases" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Release Plan: Scope Audit",
                "",
                "## Status",
                "",
                "`committed`",
                "",
                "## Problem / Baseline",
                "",
                "- Scope can drift after a release plan is accepted.",
                "",
                "## Appetite",
                "",
                f"- {appetite}",
                "",
                "## Solution Outline",
                "",
                "- Produce advisory scope recommendations from repo Markdown.",
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
                "- Recommendations identify scope tradeoffs without changing JIG state.",
                "",
            ]
        ),
        encoding="utf-8",
    )
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


def _write_slice(root: Path, slug: str, fragment: str, title: str, body: str) -> Path:
    slice_number = fragment.split("-", 1)[1]
    path = root / "docs" / "specs" / slug / f"slice-{slice_number}-{title}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                "status: DRAFT",
                "---",
                "",
                f"## Slice {fragment} - {title.replace('-', ' ')}",
                "",
                body.rstrip(),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


class ScopeAuditWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="shaper-scope-audit-"))
        self.script = ROOT / "skills" / "scope-audit" / "scripts" / "scope_audit.py"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, slug: str = "scope-audit") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.script), "--repo", str(self.tmp), "--release", slug],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_detects_appetite_leakage_outside_release_plan_boundary(self):
        _write_release_plan(self.tmp)
        _write_board(
            self.tmp,
            [("010-scope", "010-01 - scope-audit web dashboard", "IN_PROGRESS")],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            """
## Acceptance Criteria

1. Generate a text scope-audit report.
2. Build an interactive web dashboard for editing audit findings.
""",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Appetite Leakage", result.stdout)
        self.assertIn("010-01 - scope-audit web dashboard", result.stdout)
        self.assertIn("outside the release appetite or include cutline", result.stdout)
        self.assertIn("JIG files left untouched", result.stdout)

    def test_detects_nice_to_have_creep_in_jig_acceptance_criteria(self):
        _write_release_plan(self.tmp)
        _write_board(
            self.tmp,
            [("010-scope", "010-01 - scope-audit report", "READY_FOR_IMPLEMENTATION")],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            """
## Acceptance Criteria

1. Generate a text scope-audit report.
2. Nice-to-have: add colorized polish and post-release export options.
3. Stretch goal: remember dismissed findings.
""",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Nice-To-Have Creep", result.stdout)
        self.assertIn("010-01 - scope-audit report", result.stdout)
        self.assertIn("nice-to-have", result.stdout.lower())
        self.assertIn("defer optional polish or stretch scope", result.stdout)

    def test_detects_jig_work_that_conflicts_with_release_no_gos(self):
        _write_release_plan(
            self.tmp,
            no_gos="- No issue-system replacement.\n- No sprint planning.",
        )
        _write_board(
            self.tmp,
            [("010-scope", "010-01 - issue-system replacement", "IN_PROGRESS")],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Issue System Replacement",
            """
## Acceptance Criteria

1. Replace issue tracking with a shaper-managed issue-system replacement.
2. Add sprint planning fields to scope recommendations.
""",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Rabbit Holes And No-Gos", result.stdout)
        self.assertIn("010-01 - issue-system replacement", result.stdout)
        self.assertIn("conflicts with release no-go", result.stdout)
        self.assertIn("split out or defer conflicting work", result.stdout)

    def test_detects_short_no_go_terms_like_ui(self):
        _write_release_plan(self.tmp, no_gos="- No UI.")
        _write_board(
            self.tmp,
            [("010-scope", "010-01 - scope-audit UI", "IN_PROGRESS")],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit UI",
            """
## Acceptance Criteria

1. Add a UI for scope-audit findings.
""",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Rabbit Holes And No-Gos", result.stdout)
        self.assertIn("010-01 - scope-audit UI", result.stdout)
        self.assertIn("conflicts with release no-go", result.stdout)

    def test_detects_unresolved_rabbit_holes_in_release_plan(self):
        _write_release_plan(
            self.tmp,
            risks=(
                "- Risk: scope terms may not map cleanly to JIG specs.\n"
                "  - Retirement path: TBD before implementation."
            ),
        )
        _write_board(
            self.tmp,
            [("010-scope", "010-01 - scope-audit report", "READY_FOR_IMPLEMENTATION")],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            """
## Acceptance Criteria

1. Generate a text scope-audit report.
""",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Rabbit Holes And No-Gos", result.stdout)
        self.assertIn("Release plan rabbit hole", result.stdout)
        self.assertIn("retire the rabbit hole before implementation", result.stdout)
        self.assertIn("TBD before implementation", result.stdout)

    def test_detects_active_jig_work_beyond_release_plan_cutline(self):
        _write_release_plan(
            self.tmp,
            cutline_defer="release-check automation",
            handoff=(
                "- [Spec 010](../specs/010-scope/spec.md)\n"
                "- Release-check automation is explicitly deferred."
            ),
        )
        _write_board(
            self.tmp,
            [
                ("010-scope", "010-01 - scope-audit report", "READY_FOR_IMPLEMENTATION"),
                ("011-release-check", "011-01 - release-check automation", "IN_PROGRESS"),
            ],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            "## Acceptance Criteria\n\n1. Generate a text scope-audit report.\n",
        )
        _write_spec(
            self.tmp,
            "011-release-check",
            "Release Check",
            "## Acceptance Criteria\n\n1. Automate release-check readiness guidance.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## JIG Overreach", result.stdout)
        self.assertIn("011-01 - release-check automation", result.stdout)
        self.assertIn("release plan cutline says Defer", result.stdout)
        self.assertIn("move after the cutline or split to a later release", result.stdout)

    def test_detects_overreach_from_linked_slice_file_acceptance_criteria(self):
        _write_release_plan(
            self.tmp,
            cutline_defer="release-check automation",
            handoff="- [Spec 011](../specs/011-release-check/spec.md)",
        )
        _write_board(
            self.tmp,
            [("011-release-check", "011-01 - release-check automation", "IN_PROGRESS")],
        )
        spec = _write_spec(
            self.tmp,
            "011-release-check",
            "Release Check",
            "- [011-01 - release-check automation](slice-01-release-check.md)",
        )
        _write_slice(
            self.tmp,
            "011-release-check",
            "011-01",
            "release-check",
            "## Acceptance Criteria\n\n1. Automate release-check readiness guidance.\n",
        )
        self.assertTrue(spec.is_file())

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## JIG Overreach", result.stdout)
        self.assertIn("011-01 - release-check automation", result.stdout)
        self.assertIn("release plan cutline says Defer", result.stdout)

    def test_detects_relevant_orphan_specs_absent_from_release_plan_and_slate(self):
        _write_release_plan(self.tmp)
        slate = self.tmp / "docs" / "releases" / "README.md"
        slate.write_text(
            "\n".join(
                [
                    "# Release Slate",
                    "",
                    "## Committed",
                    "",
                    "| Release plan | Why it matters now | Handoff notes |",
                    "|---|---|---|",
                    "| [Scope Audit](scope-audit.md) | Scope can drift. | [Spec 010](../specs/010-scope/spec.md) |",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        _write_board(
            self.tmp,
            [
                ("010-scope", "010-01 - scope-audit report", "READY_FOR_IMPLEMENTATION"),
                ("012-telemetry", "012-01 - scope-audit telemetry", "DRAFT"),
            ],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            "## Acceptance Criteria\n\n1. Generate a text scope-audit report.\n",
        )
        _write_spec(
            self.tmp,
            "012-telemetry",
            "Scope Audit Telemetry",
            "## Acceptance Criteria\n\n1. Add scope-audit telemetry to recommendations.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Orphan Specs", result.stdout)
        self.assertIn("012-01 - scope-audit telemetry", result.stdout)
        self.assertIn("not referenced by release plan or release slate", result.stdout)
        self.assertIn("decide include, defer, split, or drop", result.stdout)

    def test_detects_relevant_orphan_specs_absent_from_status_board(self):
        _write_release_plan(self.tmp)
        slate = self.tmp / "docs" / "releases" / "README.md"
        slate.write_text(
            "\n".join(
                [
                    "# Release Slate",
                    "",
                    "## Committed",
                    "",
                    "| Release plan | Why it matters now | Handoff notes |",
                    "|---|---|---|",
                    "| [Scope Audit](scope-audit.md) | Scope can drift. | [Spec 010](../specs/010-scope/spec.md) |",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        _write_board(
            self.tmp,
            [("010-scope", "010-01 - scope-audit report", "READY_FOR_IMPLEMENTATION")],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            "## Acceptance Criteria\n\n1. Generate a text scope-audit report.\n",
        )
        _write_spec(
            self.tmp,
            "012-telemetry",
            "Scope Audit Telemetry",
            "## Acceptance Criteria\n\n1. Add scope-audit telemetry to recommendations.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Orphan Specs", result.stdout)
        self.assertIn("012-telemetry - Scope Audit Telemetry", result.stdout)
        self.assertIn("not referenced by release plan or release slate", result.stdout)

    def test_clean_pass_reports_no_scope_tightening_findings(self):
        _write_release_plan(self.tmp)
        _write_board(
            self.tmp,
            [("010-scope", "010-01 - scope-audit report", "READY_FOR_IMPLEMENTATION")],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            "## Acceptance Criteria\n\n1. Generate a text scope-audit report.\n",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No scope tightening findings detected.", result.stdout)
        self.assertEqual(result.stdout.count("_No findings detected._"), 5)
        self.assertIn("JIG files left untouched", result.stdout)

    def test_clean_pass_ignores_jig_non_goals_that_restate_release_no_gos(self):
        _write_release_plan(self.tmp, no_gos="- No web UI.")
        _write_board(
            self.tmp,
            [("010-scope", "010-01 - scope-audit report", "READY_FOR_IMPLEMENTATION")],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            """
## Acceptance Criteria

1. Generate a text scope-audit report.

## Non-goals

- No web UI.
""",
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No scope tightening findings detected.", result.stdout)
        self.assertEqual(result.stdout.count("_No findings detected._"), 5)

    def test_output_is_advisory_and_does_not_mutate_jig_lifecycle_state(self):
        _write_release_plan(
            self.tmp,
            cutline_defer="release-check automation",
            handoff="- [Spec 010](../specs/010-scope/spec.md)",
        )
        _write_board(
            self.tmp,
            [
                ("010-scope", "010-01 - scope-audit report", "IN_PROGRESS"),
                ("011-release-check", "011-01 - release-check automation", "DRAFT"),
            ],
        )
        _write_spec(
            self.tmp,
            "010-scope",
            "Scope Audit",
            "---\nstatus: IN_PROGRESS\n---\n\n## Acceptance Criteria\n\n1. Generate a report.\n",
        )
        _write_spec(
            self.tmp,
            "011-release-check",
            "Release Check",
            "---\nstatus: DRAFT\n---\n\n## Acceptance Criteria\n\n1. Add release-check automation.\n",
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
        self.assertIn("Patch-ready instructions only", result.stdout)
        self.assertIn("JIG files left untouched", result.stdout)
        self.assertNotIn("workflow.py transition", result.stdout)

    def test_release_plan_gaps_are_reported_when_jig_artifacts_are_absent(self):
        _write_release_plan(
            self.tmp,
            risks=(
                "- Risk: scope terms may not map cleanly to JIG specs.\n"
                "  - Retirement path: TBD before implementation."
            ),
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No JIG specs/status board were found.", result.stdout)
        self.assertIn("## Rabbit Holes And No-Gos", result.stdout)
        self.assertIn("Release plan rabbit hole", result.stdout)
        self.assertIn("retire the rabbit hole before implementation", result.stdout)
        self.assertIn("JIG files left untouched", result.stdout)

    def test_release_paths_outside_repo_are_not_read(self):
        outside = self.tmp.parent / "outside-release.md"
        self.addCleanup(outside.unlink, missing_ok=True)
        outside.write_text(
            "\n".join(
                [
                    "# Release Plan: Outside",
                    "",
                    "## Risks / Rabbit Holes",
                    "",
                    "- Risk: outside secret should not be read.",
                    "",
                ]
            ),
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
