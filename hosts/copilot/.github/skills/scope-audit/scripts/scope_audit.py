"""Audit release-plan scope against JIG work without mutating JIG files."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ACTIVE_STATUSES = (
    "IN_PROGRESS",
    "READY_FOR_IMPLEMENTATION",
    "READY_FOR_REVIEW",
    "REVIEWED",
    "RECONCILED",
    "DONE",
)
SCOPE_EXPANSION_WORDS = {
    "api",
    "automation",
    "dashboard",
    "editing",
    "mobile",
    "notifications",
    "service",
    "ui",
    "web",
    "workflow",
}
RELEVANCE_STOPWORDS = {
    "add",
    "and",
    "before",
    "can",
    "current",
    "from",
    "jig",
    "only",
    "plan",
    "release",
    "report",
    "scope",
    "spec",
    "specs",
    "the",
    "this",
    "with",
}
NICE_TO_HAVE_PATTERNS = (
    "nice-to-have",
    "nice to have",
    "optional",
    "polish",
    "post-release",
    "stretch",
    "follow-up",
)
UNRESOLVED_RISK_PATTERNS = (
    "tbd",
    "unknown",
    "unresolved",
    "no retirement",
    "needs decision",
    "needs research",
)


@dataclass(frozen=True)
class BoardRow:
    spec: str
    slice_label: str
    status: str
    notes: str
    spec_path: str
    text: str = ""


@dataclass(frozen=True)
class Finding:
    item: str
    evidence: str
    recommendation: str
    rationale: str


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


def _content_words(text: str) -> set[str]:
    return _words(text) - RELEVANCE_STOPWORDS


def _proposed_work_text(row: BoardRow) -> str:
    acceptance = _section(row.text, "Acceptance Criteria")
    scoped_text = acceptance if acceptance else row.text
    return f"{row.spec} {row.slice_label} {row.notes} {scoped_text}"


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
                notes=_strip_markdown(cells[3]),
                spec_path=_extract_link_target(cells[0]),
            )
        )
    return rows


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


def _referenced_spec_keys(release_text: str, slate_text: str) -> set[str]:
    return {
        key
        for key in (
            _spec_reference_key(target)
            for target in [*_link_targets(release_text), *_link_targets(slate_text)]
        )
        if key.endswith("/spec.md")
    }


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
        target = row.spec_path
        if target:
            raw_path = Path(target)
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
                notes=row.notes,
                spec_path=row.spec_path,
                text=text,
            )
        )
    return hydrated, read


def _title(text: str, fallback: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    return _strip_markdown(match.group(1)) if match else fallback


def _discover_unlisted_specs(
    repo: Path, rows: list[BoardRow]
) -> tuple[list[BoardRow], list[str]]:
    specs_dir = repo / "docs" / "specs"
    if not specs_dir.is_dir():
        return [], []
    listed = {
        _spec_reference_key(row.spec_path or f"{row.spec}/spec.md")
        for row in rows
    }
    discovered: list[BoardRow] = []
    read: list[str] = []
    for path in sorted(specs_dir.glob("*/spec.md")):
        rel = path.relative_to(specs_dir).as_posix()
        if _spec_reference_key(rel) in listed:
            continue
        text = path.read_text(encoding="utf-8")
        for slice_path in sorted(path.parent.glob("slice-*.md")):
            text += "\n" + slice_path.read_text(encoding="utf-8")
        slug = path.parent.name
        discovered.append(
            BoardRow(
                spec=slug,
                slice_label=f"{slug} - {_title(text, slug)}",
                status="UNLISTED",
                notes="",
                spec_path=rel,
                text=text,
            )
        )
        read.append(path.resolve().relative_to(repo.resolve()).as_posix())
        for slice_path in sorted(path.parent.glob("slice-*.md")):
            read.append(slice_path.resolve().relative_to(repo.resolve()).as_posix())
    return discovered, read


def _is_active(status: str) -> bool:
    normalized = status.replace("*", "").strip().upper()
    return normalized.startswith(ACTIVE_STATUSES)


def _cutline_words(release_text: str, heading: str) -> set[str]:
    cutline = _section(release_text, "Cutline")
    pattern = re.compile(rf"(?ms)^### {re.escape(heading)}\n(.*?)(?=^### |\Z)")
    match = pattern.search(cutline)
    return _words(match.group(1) if match else "")


def _cutline_entries(release_text: str, heading: str) -> list[str]:
    cutline = _section(release_text, "Cutline")
    pattern = re.compile(rf"(?ms)^### {re.escape(heading)}\n(.*?)(?=^### |\Z)")
    match = pattern.search(cutline)
    if not match:
        return []
    entries = []
    for raw in match.group(1).splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("|---"):
            continue
        if stripped.startswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if cells and cells[0].lower() != "item":
                stripped = cells[0]
        else:
            stripped = stripped.lstrip("-*").strip()
        lowered = stripped.lower()
        if lowered in {"_none_", "_-_", "_tbd_", "tbd", "none"}:
            continue
        entries.append(stripped)
    return entries


def _section_entries(text: str, heading: str) -> list[str]:
    entries = []
    for raw in _section(text, heading).splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("|") or stripped.startswith("#"):
            continue
        stripped = stripped.lstrip("-*").strip()
        if not stripped or stripped.lower() in {"_none_", "_-_", "tbd"}:
            continue
        entries.append(stripped)
    return entries


def _appetite_leakage(rows: list[BoardRow], release_text: str) -> list[Finding]:
    appetite_words = _words(_section(release_text, "Appetite"))
    include_words = _cutline_words(release_text, "Include")
    allowed = appetite_words | include_words
    findings = []
    for row in rows:
        if not _is_active(row.status):
            continue
        item_text = _proposed_work_text(row)
        expansion = sorted((_words(item_text) & SCOPE_EXPANSION_WORDS) - allowed)
        if not expansion:
            continue
        findings.append(
            Finding(
                item=row.slice_label,
                evidence=f"{row.spec} status board row ({row.status})",
                recommendation="tighten, defer, or split",
                rationale=(
                    "Mentions "
                    + ", ".join(expansion)
                    + " outside the release appetite or include cutline."
                ),
            )
        )
    return findings


def _phrase_matches(entry: str, text: str) -> bool:
    entry_words = _words(entry)
    if entry_words and entry_words <= _words(text):
        return True
    normalized_entry = " ".join(entry.lower().replace("-", " ").split())
    normalized_text = " ".join(text.lower().replace("-", " ").split())
    return normalized_entry in normalized_text


def _rabbit_holes_and_no_gos(rows: list[BoardRow], release_text: str) -> list[Finding]:
    findings = []
    for risk in _section_entries(release_text, "Risks / Rabbit Holes"):
        risk_lower = risk.lower()
        if any(pattern in risk_lower for pattern in UNRESOLVED_RISK_PATTERNS):
            findings.append(
                Finding(
                    item="Release plan rabbit hole",
                    evidence=risk,
                    recommendation="retire the rabbit hole before implementation",
                    rationale="Risk or retirement path is still unresolved.",
                )
            )
    no_gos = _section_entries(release_text, "No-Gos")
    for row in rows:
        if not _is_active(row.status):
            continue
        item_text = _proposed_work_text(row)
        for no_go in no_gos:
            if _phrase_matches(no_go, item_text):
                findings.append(
                    Finding(
                        item=row.slice_label,
                        evidence=f"release no-go: {no_go}",
                        recommendation="split out or defer conflicting work",
                        rationale="Active JIG work conflicts with release no-go.",
                    )
                )
                break
    return findings


def _jig_overreach(rows: list[BoardRow], release_text: str) -> list[Finding]:
    findings = []
    scoped_out = []
    for heading in ("Defer", "Split", "Risk-First"):
        scoped_out.extend((heading, entry) for entry in _cutline_entries(release_text, heading))
    for row in rows:
        if not _is_active(row.status):
            continue
        item_text = _proposed_work_text(row)
        for heading, entry in scoped_out:
            if _phrase_matches(entry, item_text):
                findings.append(
                    Finding(
                        item=row.slice_label,
                        evidence=f"release plan cutline says {heading}: {entry}",
                        recommendation="move after the cutline or split to a later release",
                        rationale="Active JIG work exceeds the current release cutline.",
                    )
                )
                break
    return findings


def _orphan_specs(
    rows: list[BoardRow], release_text: str, slate_text: str
) -> list[Finding]:
    referenced = _referenced_spec_keys(release_text, slate_text)
    release_context = "\n".join(
        _section(release_text, heading)
        for heading in (
            "Problem / Baseline",
            "Appetite",
            "Solution Outline",
            "Cutline",
            "JIG Handoff",
        )
    )
    context_words = _content_words(release_context)
    findings = []
    for row in rows:
        key = _spec_reference_key(row.spec_path or f"{row.spec}/spec.md")
        if key in referenced:
            continue
        item_text = f"{row.spec} {row.slice_label} {row.notes} {row.text}"
        overlap = sorted(_content_words(item_text) & context_words)
        if len(overlap) < 2:
            continue
        findings.append(
            Finding(
                item=row.slice_label,
                evidence=f"{row.spec} is not referenced by release plan or release slate",
                recommendation="decide include, defer, split, or drop",
                rationale="Relevant term overlap: " + ", ".join(overlap[:5]) + ".",
            )
        )
    return findings


def _nice_to_have_creep(rows: list[BoardRow]) -> list[Finding]:
    findings = []
    for row in rows:
        if not _is_active(row.status):
            continue
        text = _proposed_work_text(row).lower()
        matches = sorted(pattern for pattern in NICE_TO_HAVE_PATTERNS if pattern in text)
        if not matches:
            continue
        findings.append(
            Finding(
                item=row.slice_label,
                evidence=f"{row.spec} linked JIG text",
                recommendation="defer optional polish or stretch scope",
                rationale="Uses creep signal(s): " + ", ".join(matches) + ".",
            )
        )
    return findings


def _render_findings(title: str, findings: list[Finding]) -> str:
    lines = [f"## {title}", ""]
    if not findings:
        lines.append("_No findings detected._")
        return "\n".join(lines)
    lines.extend(
        [
            "| Item | Evidence read | Recommendation | Rationale |",
            "|---|---|---|---|",
        ]
    )
    for finding in findings:
        lines.append(
            "| "
            + " | ".join(
                (
                    finding.item.replace("|", "\\|"),
                    finding.evidence.replace("|", "\\|"),
                    finding.recommendation.replace("|", "\\|"),
                    finding.rationale.replace("|", "\\|"),
                )
            )
            + " |"
        )
    return "\n".join(lines)


def _render(repo: Path, release: str | None) -> str:
    release_path, release_text = _resolve_release(repo, release)
    if release and release_text is None:
        return "\n".join(
            [
                "# Scope Audit",
                "",
                f"Release plan missing: {release_path}",
                "JIG files left untouched.",
                "",
            ]
        )
    release_text = release_text or ""
    slate = repo / "docs" / "releases" / "README.md"
    slate_text = slate.read_text(encoding="utf-8") if slate.is_file() else ""

    board = repo / "docs" / "specs" / "README.md"
    no_jig_message = ""
    jig_files_read: list[str] = []
    if board.is_file():
        rows, read_specs = _read_row_specs(repo, _parse_board(board))
        unlisted, unlisted_reads = _discover_unlisted_specs(repo, rows)
        rows.extend(unlisted)
        read_specs.extend(unlisted_reads)
        jig_files_read = ["docs/specs/README.md", *read_specs]
    else:
        rows, read_specs = _discover_unlisted_specs(repo, [])
        if not rows:
            no_jig_message = "No JIG specs/status board were found."
        else:
            jig_files_read = read_specs
    if release_path and release_text:
        release_line = (
            "Release plan inspected: "
            f"{release_path.resolve().relative_to(repo.resolve()).as_posix()}"
        )
    else:
        release_line = "Release plan inspected: none supplied"
    finding_groups = [
        ("Appetite Leakage", _appetite_leakage(rows, release_text)),
        ("Nice-To-Have Creep", _nice_to_have_creep(rows)),
        (
            "Rabbit Holes And No-Gos",
            _rabbit_holes_and_no_gos(rows, release_text),
        ),
        ("JIG Overreach", _jig_overreach(rows, release_text)),
        ("Orphan Specs", _orphan_specs(rows, release_text, slate_text)),
    ]
    if any(findings for _title, findings in finding_groups):
        summary = "Scope tightening findings detected."
    else:
        summary = "No scope tightening findings detected."
    parts = [
        "# Scope Audit",
        "",
        release_line,
        no_jig_message
        or "JIG files read: " + ", ".join(jig_files_read),
        "",
        summary,
        "",
    ]
    for title, findings in finding_groups:
        parts.append(_render_findings(title, findings))
        parts.append("")
    parts.extend(
        [
            "## Advisory Only",
            "",
            "Patch-ready instructions only: use JIG workflow separately for any lifecycle changes.",
            "JIG files left untouched.",
            "",
        ]
    )
    return "\n".join(parts)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="render a non-mutating scope audit")
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
