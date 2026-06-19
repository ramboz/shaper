"""Maintain shaper's compact docs/releases/README.md slate."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


STATUSES = ("candidate", "committed", "shipping", "shipped", "dropped")
HEADINGS = {
    "candidate": "Candidate",
    "committed": "Committed",
    "shipping": "Shipping",
    "shipped": "Shipped",
    "dropped": "Dropped",
}
LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
STATUS_LINE_RE = re.compile(
    rf"(?im)^\s*(?:[-*]\s*)?`?({'|'.join(STATUSES)})`?\s*$"
)


@dataclass(frozen=True)
class ReleasePlan:
    slug: str
    title: str
    status: str
    why: str
    handoff: str


def _section(text: str, heading: str) -> str:
    pattern = re.compile(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)")
    match = pattern.search(text)
    return match.group(1) if match else ""


def _title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def _title(text: str, slug: str) -> str:
    match = re.search(r"(?m)^#\s+(?:Release Plan:\s*)?(.+?)\s*$", text)
    return match.group(1).strip() if match else _title_from_slug(slug)


def _status(text: str) -> str:
    frontmatter = re.search(r"(?ms)\A---\n(.*?)\n---", text)
    if frontmatter:
        for raw in frontmatter.group(1).splitlines():
            key, sep, value = raw.partition(":")
            if sep and key.strip().lower() == "status":
                status = value.strip().strip("`").lower()
                if status in STATUSES:
                    return status
    match = STATUS_LINE_RE.search(_section(text, "Status"))
    if match:
        return match.group(1).lower()
    return "candidate"


def _clean_cell(value: str) -> str:
    return " ".join(value.replace("|", "\\|").split())


def _meaningful_lines(section: str) -> list[str]:
    lines = []
    for raw in section.splitlines():
        stripped = raw.strip()
        if stripped.startswith("-"):
            stripped = stripped.lstrip("-").strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if "tbd" in lowered or lowered in {"_-_", "-"}:
            continue
        if stripped.endswith(":"):
            continue
        lines.append(stripped)
    return lines


def _why(text: str) -> str:
    for heading in ("Problem / Baseline", "Solution Outline", "Appetite"):
        lines = _meaningful_lines(_section(text, heading))
        if lines:
            return _clean_cell(lines[0])
    return "See release plan."


def _handoff(text: str) -> str:
    links = []
    seen = set()
    for link in LINK_RE.findall(_section(text, "JIG Handoff")):
        if link not in seen:
            links.append(link)
            seen.add(link)
    if not links:
        return "No JIG handoff linked."
    return _clean_cell("JIG handoff: " + ", ".join(links))


def _discover_release_plans(repo: Path) -> list[Path]:
    release_dir = repo / "docs" / "releases"
    if not release_dir.is_dir():
        return []
    return [
        path
        for path in sorted(release_dir.glob("*.md"))
        if path.name.lower() != "readme.md"
    ]


def _read_plan(path: Path) -> ReleasePlan:
    text = path.read_text(encoding="utf-8")
    slug = path.stem
    return ReleasePlan(
        slug=slug,
        title=_title(text, slug),
        status=_status(text),
        why=_why(text),
        handoff=_handoff(text),
    )


def _row(plan: ReleasePlan) -> str:
    return (
        f"| [{_clean_cell(plan.title)}]({plan.slug}.md) | "
        f"{plan.why} | {plan.handoff} |"
    )


def _render_section(status: str, plans: list[ReleasePlan]) -> str:
    heading = HEADINGS[status]
    lines = [f"## {heading}", ""]
    if status == "shipped":
        lines.extend(
            [
                "Recently shipped release plans stay here only while they inform current decisions.",
                "",
            ]
        )
    elif status == "dropped":
        lines.extend(
            [
                "List only currently relevant dropped or no-go release plans. This section is",
                "not an archive of every idea the project declined.",
                "",
            ]
        )
    header = "Why it still matters" if status == "dropped" else "Why it matters now"
    lines.extend(
        [
            f"| Release plan | {header} | Handoff notes |",
            "|---|---|---|",
        ]
    )
    if not plans:
        lines.append("| _None yet_ | _-_ | _-_ |")
    else:
        lines.extend(_row(plan) for plan in plans)
    return "\n".join(lines)


def render_slate(plans: list[ReleasePlan]) -> str:
    grouped = {status: [] for status in STATUSES}
    for plan in plans:
        grouped[plan.status].append(plan)

    lines = [
        "# Release Slate",
        "",
        "This slate is a compact view of release plans that matter right now. It is not",
        "a backlog, not a roadmap, not a sprint plan, and not a second JIG status board.",
        "JIG remains the source of truth for implementation lifecycle state.",
        "",
        "Keep entries short. Link to release plans and, when useful, JIG specs or slices",
        "without copying JIG lifecycle status. Remove dropped or deferred ideas once",
        "they stop informing a current release decision.",
        "",
    ]
    if not plans:
        lines.extend(
            [
                "No release plans were found.",
                "",
            ]
        )
    for status in STATUSES:
        lines.append(_render_section(status, grouped[status]))
        lines.append("")
    return "\n".join(lines)


def update_slate(repo: Path) -> tuple[Path, int, bool]:
    release_dir = repo / "docs" / "releases"
    slate = release_dir / "README.md"
    existing = slate.is_file()
    if existing:
        slate.read_text(encoding="utf-8")
    plan_paths = _discover_release_plans(repo)
    plans = [_read_plan(path) for path in plan_paths]
    release_dir.mkdir(parents=True, exist_ok=True)
    slate.write_text(render_slate(plans), encoding="utf-8")
    return slate, len(plans), existing


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="write or refresh docs/releases/README.md"
    )
    parser.add_argument("--repo", default=".", help="repository root")
    return parser


def main(argv: list[str]) -> int:
    ns = _parser().parse_args(argv[1:])
    repo = Path(ns.repo)
    slate, count, existing = update_slate(repo)
    try:
        slate_display = slate.relative_to(repo)
    except ValueError:
        slate_display = slate
    print(f"Wrote {slate_display.as_posix()}")
    print(f"Release plans discovered: {count}")
    print(f"Existing slate read: {'yes' if existing else 'no'}")
    print("JIG lifecycle state copied: no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
