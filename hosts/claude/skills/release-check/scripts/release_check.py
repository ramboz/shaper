"""Advisory release-check from release-plan criteria and JIG status.

Reads a release plan and JIG status board/specs (when present) and recommends
one of ship / cut scope / stop and re-shape / extend only with explicit
rationale. This is the JIG-only slice: servo signals are reported as not
evaluated, never as a failure. The helper never mutates JIG lifecycle state.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


DONE_STATUS = "DONE"
UNRESOLVED_RISK_PATTERNS = (
    "tbd",
    "unknown",
    "unresolved",
    "no retirement",
    "needs decision",
    "needs research",
)
EMPTY_MARKERS = {"_none_", "_-_", "_tbd_", "tbd", "none", "-"}


@dataclass(frozen=True)
class BoardRow:
    spec: str
    slice_label: str
    status: str
    spec_path: str
    text: str = ""


def _strip_markdown(value: str) -> str:
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", value)
    return " ".join(value.strip().split())


def _extract_link_target(markdown: str) -> str:
    match = re.search(r"\[[^\]]+\]\(([^)]+)\)", markdown)
    return match.group(1) if match else ""


def _link_targets(markdown: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", markdown)


def _section(text: str, heading: str) -> str:
    pattern = re.compile(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)")
    match = pattern.search(text)
    return match.group(1) if match else ""


def _words(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) >= 3 or word in {"ui"}
    }


def _section_entries(text: str, heading: str) -> list[str]:
    entries = []
    for raw in _section(text, heading).splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("|") or stripped.startswith("#"):
            continue
        stripped = stripped.lstrip("-*").strip()
        if not stripped or stripped.lower() in EMPTY_MARKERS:
            continue
        entries.append(stripped)
    return entries


def _resolve_release(repo: Path, release: str | None) -> tuple[Path | None, str | None]:
    if not release:
        return None, None
    repo_root = repo.resolve()
    raw = Path(release)
    candidates = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.append(repo / raw)
        if raw.suffix != ".md":
            candidates.append(repo / "docs" / "releases" / f"{release}.md")
    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(repo_root)
        except ValueError:
            continue
        if resolved.is_file():
            return resolved, resolved.read_text(encoding="utf-8")
    return candidates[-1], None


def _spec_reference_key(target: str) -> str:
    normalized = target.split("#", 1)[0].replace("\\", "/").strip()
    for marker in ("docs/specs/", "../specs/", "specs/"):
        if marker in normalized:
            normalized = normalized.split(marker, 1)[1]
            break
    parts = [part for part in normalized.split("/") if part and part != "."]
    if len(parts) >= 2 and parts[-1] == "spec.md":
        return "/".join(parts[-2:])
    if len(parts) >= 2 and parts[1] == "spec.md":
        return "/".join(parts[:2])
    return normalized


def _referenced_spec_keys(release_text: str) -> set[str]:
    return {
        key
        for key in (_spec_reference_key(target) for target in _link_targets(release_text))
        if key.endswith("/spec.md")
    }


def _parse_board(board: Path) -> list[BoardRow]:
    rows: list[BoardRow] = []
    for line in board.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 4 or cells[0].lower() == "spec":
            continue
        rows.append(
            BoardRow(
                spec=_strip_markdown(cells[0]),
                slice_label=_strip_markdown(cells[1]),
                status=_strip_markdown(cells[2]),
                spec_path=_extract_link_target(cells[0]),
            )
        )
    return rows


def _slice_fragment(label: str) -> str:
    match = re.search(r"\b\d{3}-\d{2}\b", label)
    return match.group(0) if match else ""


def _linked_slice_paths(spec_path: Path, spec_text: str, row: BoardRow) -> list[Path]:
    fragment = _slice_fragment(row.slice_label)
    if not fragment:
        return []
    candidates: list[Path] = []
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", spec_text):
        label, target = match.groups()
        if fragment not in label and fragment not in target:
            continue
        path = (spec_path.parent / target.split("#", 1)[0]).resolve()
        try:
            path.relative_to(spec_path.parent.resolve())
        except ValueError:
            continue
        if path.is_file() and path.suffix == ".md":
            candidates.append(path)
    if candidates:
        return sorted(set(candidates))
    return [
        path
        for path in sorted(spec_path.parent.glob("slice-*.md"))
        if fragment in path.read_text(encoding="utf-8")
    ]


def _read_row_specs(repo: Path, rows: list[BoardRow]) -> tuple[list[BoardRow], list[str]]:
    read: list[str] = []
    hydrated: list[BoardRow] = []
    board_dir = (repo / "docs" / "specs").resolve()
    for row in rows:
        text = ""
        if row.spec_path:
            raw_path = Path(row.spec_path)
            if not raw_path.is_absolute():
                path = (board_dir / raw_path).resolve()
                try:
                    path.relative_to(board_dir)
                except ValueError:
                    path = None
                if path and path.is_file():
                    text = path.read_text(encoding="utf-8")
                    read.append(path.relative_to(repo.resolve()).as_posix())
                    for slice_path in _linked_slice_paths(path, text, row):
                        text += "\n" + slice_path.read_text(encoding="utf-8")
                        read.append(slice_path.relative_to(repo.resolve()).as_posix())
        hydrated.append(
            BoardRow(
                spec=row.spec,
                slice_label=row.slice_label,
                status=row.status,
                spec_path=row.spec_path,
                text=text,
            )
        )
    return hydrated, read


def _is_done(status: str) -> bool:
    return status.replace("*", "").strip().upper().startswith(DONE_STATUS)


def _proposed_work_text(row: BoardRow) -> str:
    acceptance = _section(row.text, "Acceptance Criteria")
    scoped_text = acceptance if acceptance else row.text
    return f"{row.spec} {row.slice_label} {scoped_text}"


def _phrase_matches(entry: str, text: str) -> bool:
    entry_words = _words(entry)
    if entry_words and entry_words <= _words(text):
        return True
    normalized_entry = " ".join(entry.lower().replace("-", " ").split())
    normalized_text = " ".join(text.lower().replace("-", " ").split())
    return normalized_entry in normalized_text


def _in_scope(rows: list[BoardRow], release_text: str) -> list[BoardRow]:
    referenced = _referenced_spec_keys(release_text)
    if not referenced:
        return list(rows)
    scoped = [
        row
        for row in rows
        if _spec_reference_key(row.spec_path or f"{row.spec}/spec.md") in referenced
    ]
    return scoped or list(rows)


def _unresolved_risks(release_text: str) -> list[str]:
    findings = []
    for risk in _section_entries(release_text, "Risks / Rabbit Holes"):
        if any(pattern in risk.lower() for pattern in UNRESOLVED_RISK_PATTERNS):
            findings.append(risk)
    return findings


def _no_go_conflicts(rows: list[BoardRow], release_text: str) -> list[tuple[str, str]]:
    conflicts = []
    no_gos = _section_entries(release_text, "No-Gos")
    for row in rows:
        item_text = _proposed_work_text(row)
        for no_go in no_gos:
            if _phrase_matches(no_go, item_text):
                conflicts.append((row.slice_label, no_go))
                break
    return conflicts


def _extension_rationale(release_text: str) -> str:
    entries = _section_entries(release_text, "Extension")
    return " ".join(entries).strip()


def _recommend(
    scoped: list[BoardRow],
    conflicts: list[tuple[str, str]],
    risks: list[str],
    extension: str,
) -> tuple[str, str]:
    incomplete = [row for row in scoped if not _is_done(row.status)]
    done = [row for row in scoped if _is_done(row.status)]

    if conflicts:
        detail = "; ".join(f"{label} vs no-go '{no_go}'" for label, no_go in conflicts)
        return (
            "stop and re-shape",
            "In-scope JIG work conflicts with a release no-go: "
            f"{detail}. Re-shape the release so it no longer crosses the no-go.",
        )
    if scoped and not done:
        return (
            "stop and re-shape",
            "No in-scope JIG work is DONE, so there is no shippable subset. "
            "Re-shape the release around what can actually be built.",
        )
    if incomplete:
        labels = ", ".join(row.slice_label for row in incomplete)
        if extension:
            return (
                "extend only with explicit rationale",
                "In-scope work is incomplete ("
                f"{labels}). The release plan records an explicit extension "
                f"rationale: {extension}",
            )
        risk_note = (
            f" Unresolved rabbit holes also remain ({'; '.join(risks)}) and must "
            "be retired before the cut subset ships."
            if risks
            else ""
        )
        return (
            "cut scope",
            "A DONE subset is shippable while in-scope work remains incomplete "
            f"({labels}). Cut or defer the incomplete work to ship within "
            f"appetite.{risk_note}",
        )
    if risks:
        joined = "; ".join(risks)
        if extension:
            return (
                "extend only with explicit rationale",
                "In-scope work is DONE but unresolved rabbit holes remain "
                f"({joined}). The release plan records an explicit extension "
                f"rationale: {extension}",
            )
        return (
            "stop and re-shape",
            "In-scope work is DONE but unresolved rabbit holes remain "
            f"({joined}) and there is no scope left to cut. Retire the risk "
            "or re-shape before shipping.",
        )
    if not scoped:
        return (
            "stop and re-shape",
            "No in-scope JIG evidence was found, so ship cannot be confirmed. "
            "Re-shape the release around tracked work.",
        )
    return (
        "ship",
        "All in-scope JIG work is DONE, no unresolved rabbit holes remain, and "
        "no active work conflicts with a release no-go.",
    )


def _criterion_line(label: str, value: str) -> str:
    return f"- {label}: {value if value else 'missing'}"


def _render_criteria(release_text: str) -> list[str]:
    appetite = " ".join(_section_entries(release_text, "Appetite"))
    cutline = "present" if _section(release_text, "Cutline").strip() else "missing"
    handoff = "; ".join(_section_entries(release_text, "JIG Handoff")) or ""
    criteria = "; ".join(_section_entries(release_text, "Release-Check Criteria")) or ""
    rabbit_holes = _section_entries(release_text, "Risks / Rabbit Holes")
    no_gos = _section_entries(release_text, "No-Gos")
    return [
        "## Release Criteria Read",
        "",
        _criterion_line("Appetite", appetite),
        _criterion_line("Cutline", cutline),
        _criterion_line("JIG handoff", handoff),
        _criterion_line("Release-check criteria", criteria),
        _criterion_line("Rabbit holes", "; ".join(rabbit_holes) or "none listed"),
        _criterion_line("No-gos", "; ".join(no_gos) or "none listed"),
    ]


def _render_jig_status(scoped: list[BoardRow]) -> list[str]:
    lines = ["## JIG Status", ""]
    if not scoped:
        lines.append("_No in-scope JIG work found._")
        return lines
    lines.extend(["| Spec | Slice | Status |", "|---|---|---|"])
    for row in scoped:
        slice_label = row.slice_label.replace("|", "\\|")
        lines.append(f"| {row.spec} | {slice_label} | {row.status} |")
    done = sum(1 for row in scoped if _is_done(row.status))
    lines.extend(["", f"In-scope slices: {len(scoped)}; DONE: {done}."])
    return lines


def _render_open_risks(
    conflicts: list[tuple[str, str]], risks: list[str]
) -> list[str]:
    lines = ["## Open Risks", ""]
    if not conflicts and not risks:
        lines.append("_No open risks detected._")
        return lines
    for risk in risks:
        lines.append(f"- Unresolved rabbit hole: {risk}")
    for label, no_go in conflicts:
        lines.append(f"- No-go conflict: {label} crosses no-go '{no_go}'.")
    return lines


def _render(repo: Path, release: str | None) -> str:
    release_path, release_text = _resolve_release(repo, release)
    if release and release_text is None:
        return "\n".join(
            [
                "# Release Check",
                "",
                f"Release plan missing: {release_path}",
                "JIG files left untouched.",
                "",
            ]
        )
    release_text = release_text or ""

    board = repo / "docs" / "specs" / "README.md"
    no_jig_message = ""
    jig_files_read: list[str] = []
    rows: list[BoardRow] = []
    if board.is_file():
        rows, read_specs = _read_row_specs(repo, _parse_board(board))
        jig_files_read = list(dict.fromkeys(["docs/specs/README.md", *read_specs]))
    else:
        no_jig_message = "No JIG specs/status board were found."

    scoped = _in_scope(rows, release_text)
    conflicts = _no_go_conflicts(scoped, release_text)
    risks = _unresolved_risks(release_text)
    extension = _extension_rationale(release_text)
    recommendation, rationale = _recommend(scoped, conflicts, risks, extension)

    if release_path and release_text:
        release_line = (
            "Release plan inspected: "
            f"{release_path.resolve().relative_to(repo.resolve()).as_posix()}"
        )
    else:
        release_line = "Release plan inspected: none supplied"

    parts = [
        "# Release Check",
        "",
        release_line,
        no_jig_message or "JIG files read: " + ", ".join(jig_files_read),
        "Servo signals: not evaluated (JIG-only slice).",
        "",
    ]
    parts.extend(_render_criteria(release_text))
    parts.append("")
    parts.extend(_render_jig_status(scoped))
    parts.append("")
    parts.extend(_render_open_risks(conflicts, risks))
    parts.append("")
    parts.extend(
        [
            f"## Recommendation: {recommendation}",
            "",
            rationale,
            "",
            "## Advisory Only",
            "",
            "Advisory only: use JIG workflow separately for any lifecycle changes.",
            "JIG files left untouched.",
            "",
        ]
    )
    return "\n".join(parts)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="render an advisory release check")
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
