"""The CI board check is read-only and preserves newer advisory sections."""

import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_spec_board


class SpecBoardCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="shaper-board-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.specs = self.root / "docs/specs"
        directory = self.specs / "001-test"
        directory.mkdir(parents=True)
        self.spec = directory / "spec.md"
        self.spec.write_text("---\nstatus: DONE\n---\n# Spec 001\n")
        self.slice = directory / "slice-01-test.md"
        self.slice.write_text("---\nstatus: DONE\n---\n## Slice 001-01 - test\n")
        self.board = self.specs / "README.md"
        self.board.write_text("# Spec Status Board\n\n| Spec | Slice | Status | Notes |\n")
        subprocess.run(
            [sys.executable, str(check_spec_board.HELPER), "status-board", str(self.root)],
            check=True, capture_output=True, text=True,
        )

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_current_board_with_newer_advisory_footer_passes_without_mutation(self):
        self.board.write_text(self.board.read_text() + check_spec_board.AUDIT_MARKER + "\nAdvisory only.\n")
        before = self.snapshot()
        out = io.StringIO()
        self.assertEqual(check_spec_board.check(self.root, out), 0, out.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_stale_lifecycle_table_fails_without_mutation(self):
        self.slice.write_text(self.slice.read_text().replace("DONE", "IN_PROGRESS"))
        before = self.snapshot()
        out = io.StringIO()
        self.assertEqual(check_spec_board.check(self.root, out), 1)
        self.assertIn("README.md", out.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_stale_spec_rollup_fails_without_mutation(self):
        self.spec.write_text(self.spec.read_text().replace("DONE", "DRAFT"))
        before = self.snapshot()
        out = io.StringIO()
        self.assertEqual(check_spec_board.check(self.root, out), 1)
        self.assertIn("001-test/spec.md", out.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_missing_table_or_audit_before_table_fails_without_mutation(self):
        original = self.board.read_text()
        for text in (
            "# Spec Status Board\n" + check_spec_board.AUDIT_MARKER + "\nAdvisory only.\n",
            check_spec_board.AUDIT_MARKER + "\nAdvisory only.\n" + original,
        ):
            with self.subTest(text=text):
                self.board.write_text(text)
                before = self.snapshot()
                out = io.StringIO()
                self.assertEqual(check_spec_board.check(self.root, out), 1)
                self.assertIn("README.md", out.getvalue())
                self.assertEqual(self.snapshot(), before)

    def test_nonlocking_review_owner_hints_are_compatible_but_active_claims_are_checked(self):
        original = self.board.read_text()
        self.spec.write_text("---\nstatus: IN_PROGRESS\n---\n# Spec 001\n")
        for status in ("READY_FOR_REVIEW", "REVIEWED", "RECONCILED"):
            with self.subTest(status=status):
                self.slice.write_text(
                    f"---\nstatus: {status}\nclaimed_by: owner\n---\n## Slice 001-01 - test\n"
                )
                self.board.write_text(original.replace("**DONE**", f"{status} (owner)"))
                before = self.snapshot()
                out = io.StringIO()
                self.assertEqual(check_spec_board.check(self.root, out), 0, out.getvalue())
                self.assertEqual(self.snapshot(), before)
        self.slice.write_text(
            "---\nstatus: IN_PROGRESS\nclaimed_by: owner\n---\n## Slice 001-01 - test\n"
        )
        self.board.write_text(original.replace("**DONE**", "IN_PROGRESS (other)"))
        self.assertEqual(check_spec_board.check(self.root, io.StringIO()), 1)

    def test_invalid_source_status_is_not_normalized_into_valid_board_status(self):
        self.spec.write_text("---\nstatus: IN_PROGRESS\n---\n# Spec 001\n")
        self.slice.write_text(
            "---\nstatus: REVIEWED (other)\n---\n## Slice 001-01 - test\n"
        )
        self.board.write_text(self.board.read_text().replace("**DONE**", "REVIEWED"))
        self.assertEqual(check_spec_board.check(self.root, io.StringIO()), 1)

    def test_deferred_resolution_trigger_is_not_treated_as_owner_display(self):
        (self.spec.parent / "slice-02-later.md").write_text(
            "---\nstatus: DEFERRED\n---\n## Slice 001-02 - later\n\n"
            "**Resolution trigger:** REVIEWED\n"
        )
        subprocess.run(
            [sys.executable, str(check_spec_board.HELPER), "status-board", str(self.root)],
            check=True, capture_output=True, text=True,
        )
        text = self.board.read_text()
        self.assertIn("| REVIEWED |", text)
        self.board.write_text(text.replace("| REVIEWED |", "| REVIEWED (owner) |"))
        self.assertEqual(check_spec_board.check(self.root, io.StringIO()), 1)


if __name__ == "__main__":
    unittest.main()
