"""Generate a non-mutating cutline from a shaper release plan and JIG board."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CATEGORIES = ("include", "defer", "split", "risk-first")


def _strip_markdown(value: str) -> str:
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", value)
    return value.strip()


def _parse_board(board: Path) -> list[dict[str, str]]:
    rows = []
    for line in board.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 4 or cells[0].lower() == "spec":
            continue
        rows.append(
            {
                "spec": _strip_markdown(cells[0]),
                "slice": _strip_markdown(cells[1]),
                "status": _strip_markdown(cells[2]),
                "notes": _strip_markdown(cells[3]),
                "spec_path": _extract_link_target(cells[0]),
            }
        )
    return rows


def _resolve_release(repo: Path, release: str | None) -> tuple[Path | None, str | None]:
    if not release:
        return None, None
    raw = Path(release)
    candidates = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.append(repo / raw)
        if raw.suffix != ".md":
            candidates.append(repo / "docs" / "releases" / f"{release}.md")
    for candidate in candidates:
        if candidate.is_file():
            return candidate, candidate.read_text(encoding="utf-8")
    return candidates[-1], None


def _section(text: str, heading: str) -> str:
    pattern = re.compile(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)")
    match = pattern.search(text)
    return match.group(1) if match else ""


def _words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) >= 4}


def _release_signal(
    row: dict[str, str], release_text: str | None
) -> tuple[str | None, str | None]:
    if not release_text:
        return None, None
    item_words = _words(f"{row['spec']} {row['slice']}")
    no_go_words = _words(_section(release_text, "No-Gos"))
    risk_words = _words(_section(release_text, "Risks / Rabbit Holes"))
    if item_words & no_go_words:
        return "defer", "Matches release no-gos."
    if item_words & risk_words:
        return "risk-first", "Matches release risks/rabbit holes."
    return None, None


def _extract_link_target(markdown: str) -> str:
    match = re.search(r"\[[^\]]+\]\(([^)]+)\)", markdown)
    return match.group(1) if match else ""


def _classify(row: dict[str, str], release_text: str | None) -> str:
    release_category, _reason = _release_signal(row, release_text)
    if release_category:
        return release_category
    status = row["status"].replace("*", "").strip().upper()
    label = row["slice"].lower()
    if " and " in label or "/" in label:
        return "split"
    if status.startswith(("DONE", "REVIEWED", "RECONCILED")):
        return "include"
    if status.startswith(("IN_PROGRESS", "READY_FOR_IMPLEMENTATION", "READY_FOR_REVIEW")):
        return "risk-first"
    return "defer"


def _read_linked_specs(repo: Path, rows: list[dict[str, str]]) -> list[str]:
    read = []
    board_dir = (repo / "docs" / "specs").resolve()
    for row in rows:
        target = row.get("spec_path")
        if not target:
            continue
        raw_path = Path(target)
        if raw_path.is_absolute():
            continue
        path = (board_dir / raw_path).resolve()
        try:
            path.relative_to(board_dir)
        except ValueError:
            continue
        if path.is_file():
            path.read_text(encoding="utf-8")
            read.append(path.relative_to(repo.resolve()).as_posix())
    return read


def _recommendations(
    rows: list[dict[str, str]], release_text: str | None
) -> dict[str, list[dict[str, str]]]:
    grouped = {category: [] for category in CATEGORIES}
    for row in rows:
        grouped[_classify(row, release_text)].append(row)
    return grouped


def _render_group(
    category: str, rows: list[dict[str, str]], release_text: str | None
) -> str:
    title = "Risk-First" if category == "risk-first" else category.title()
    lines = [f"## {title}", ""]
    if not rows:
        lines.append("_No items detected._")
        return "\n".join(lines)
    lines.extend(
        [
            "| Item | Evidence read | Recommendation | Rationale | Non-mutating JIG handoff |",
            "|---|---|---|---|---|",
        ]
    )
    for row in rows:
        item = row["slice"]
        evidence = "release plan + " if release_text else ""
        evidence += f"{row['spec']} status board row ({row['status']})"
        _release_category, release_reason = _release_signal(row, release_text)
        if release_reason:
            rationale = release_reason
        elif category == "include":
            rationale = "Already complete or reviewed enough to support this release boundary."
        elif category == "risk-first":
            rationale = "Close to the release path but not done; retire remaining risk before commitment."
        elif category == "split":
            rationale = "The label suggests mixed scope; shape a smaller release-facing slice."
        else:
            rationale = "Useful work, but outside the current proven release cutline."
        handoff = "Draft instructions or run JIG workflow separately; do not change status here."
        lines.append(
            f"| {item} | {evidence} | {category} | {rationale} | {handoff} |"
        )
    return "\n".join(lines)


def _render(repo: Path, release: str | None) -> str:
    release_path, release_text = _resolve_release(repo, release)
    if release and release_text is None:
        return "\n".join(
            [
                "# Cutline",
                "",
                f"Release plan missing: {release_path}",
                "JIG files left untouched.",
                "",
            ]
        )

    board = repo / "docs" / "specs" / "README.md"
    spec_dir = repo / "docs" / "specs"
    if not board.is_file() and not spec_dir.is_dir():
        return "\n".join(
            [
                "# Cutline",
                "",
                "No JIG specs/status board were found.",
                "Use the release plan appetite, no-gos, and risks for release-plan-only guidance.",
                "JIG files left untouched.",
                "",
            ]
        )

    if not board.is_file():
        return "\n".join(
            [
                "# Cutline",
                "",
                "No JIG status board was found at docs/specs/README.md.",
                "JIG files left untouched.",
                "",
            ]
        )

    rows = _parse_board(board)
    read_specs = _read_linked_specs(repo, rows)
    grouped = _recommendations(rows, release_text)
    if release_path and release_text:
        release_line = f"Release plan inspected: {release_path.relative_to(repo).as_posix()}"
    else:
        release_line = "Release plan inspected: none supplied"
    parts = [
        "# Cutline",
        "",
        release_line,
        f"JIG files read: docs/specs/README.md"
        + (", " + ", ".join(read_specs) if read_specs else ""),
        "",
    ]
    for category in CATEGORIES:
        parts.append(_render_group(category, grouped[category], release_text))
        parts.append("")
    parts.append("JIG files left untouched.")
    parts.append("")
    return "\n".join(parts)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="render a non-mutating cutline")
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--release", help="release slug or docs/releases path")
    return parser


def main(argv: list[str]) -> int:
    ns = _parser().parse_args(argv[1:])
    repo = Path(ns.repo)
    output = _render(repo, ns.release)
    sys.stdout.write(output)
    return 1 if "Release plan missing:" in output else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
