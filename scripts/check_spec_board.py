"""Read-only CI lifecycle-board check using the repository's vendored JIG.

Newer JIG adds an advisory richer-skill audit that the vendored renderer does
not know. Check lifecycle rows and spec rollups in a scratch copy without
discarding or treating that advisory section as lifecycle drift.
"""

from __future__ import annotations

import argparse
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / ".codex/skills/jig-spec-workflow/workflow.py"
AUDIT_MARKER = "\n## Richer-skill selection audit (spec 096-05)"


def _lifecycle_text(text: str, *, display_owners: bool = False) -> str:
    header = re.compile(r"(?m)^\|\s*Spec\s*\|\s*Slice\s*\|\s*Status\s*\|\s*Notes\s*\|")
    table = header.search(text)
    if table is None:
        raise ValueError("missing lifecycle table")
    start = text.find(AUDIT_MARKER)
    if start >= 0:
        if start < table.start():
            raise ValueError("advisory audit precedes lifecycle table")
        end = text.find("\n## ", start + len(AUDIT_MARKER))
        text = text[:start] + (text[end:] if end >= 0 else "")
    if display_owners:
        # Normalize only the committed board's lifecycle Status cells.
        # Regenerated source truth and deferred triggers stay untouched.
        lines = []
        in_table = False
        for line in text.splitlines(keepends=True):
            if header.match(line):
                in_table = True
            elif not line.startswith("|"):
                in_table = False
            if in_table:
                fields = line.split("|")
                if len(fields) >= 5:
                    fields[3] = re.sub(
                        r"^(\s*(?:READY_FOR_REVIEW|REVIEWED|RECONCILED))"
                        r"\s+\([^|\n]*\)(\s*)$", r"\1\2", fields[3],
                    )
                    line = "|".join(fields)
            lines.append(line)
        text = "".join(lines)
    return text.rstrip("\n") + "\n"


def check(root: Path = ROOT, out=None) -> int:
    if out is None:
        out = sys.stdout
    source = root.resolve() / "docs/specs"
    if not HELPER.is_file() or not (source / "README.md").is_file():
        out.write("ERROR: missing vendored JIG helper or spec status board.\n")
        return 1
    with tempfile.TemporaryDirectory(prefix="shaper-board-check-") as temporary:
        scratch = Path(temporary)
        target = scratch / "docs/specs"
        shutil.copytree(source, target)
        result = subprocess.run(
            [sys.executable, str(HELPER), "status-board", str(scratch)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode:
            out.write(f"ERROR: vendored board generation failed: {result.stderr or result.stdout}")
            return 1
        drift = False
        for path in sorted(source.rglob("*.md")):
            relative = path.relative_to(source)
            before = path.read_text(encoding="utf-8")
            after = (target / relative).read_text(encoding="utf-8")
            if relative == Path("README.md"):
                try:
                    before = _lifecycle_text(before, display_owners=True)
                    after = _lifecycle_text(after)
                except ValueError as exc:
                    out.write(f"ERROR: docs/specs/README.md: {exc}.\n")
                    return 1
            if before != after:
                drift = True
                out.writelines(difflib.unified_diff(
                    before.splitlines(keepends=True), after.splitlines(keepends=True),
                    fromfile=f"docs/specs/{relative}", tofile=f"regenerated/{relative}",
                ))
        if drift:
            out.write("ERROR: stale lifecycle board or spec rollup; regenerate with JIG.\n")
            return 1
    out.write("OK: lifecycle board and spec rollups match vendored JIG; advisory audit preserved.\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=ROOT)
    return check(parser.parse_args().project_dir)


if __name__ == "__main__":
    raise SystemExit(main())
