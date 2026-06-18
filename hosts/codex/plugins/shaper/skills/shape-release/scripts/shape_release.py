"""Create or refine shaper release-plan Markdown files."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


STATUSES = ("candidate", "committed", "shipping", "shipped", "dropped")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _source_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _template_text() -> str:
    return (_source_root() / "templates" / "release-plan.md").read_text(
        encoding="utf-8"
    )


def _title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def _replace_h1(text: str, title: str) -> str:
    line = f"# Release Plan: {title}"
    if text.startswith("# Release Plan:"):
        return re.sub(r"(?m)^# Release Plan: .*$", line, text, count=1)
    return f"{line}\n\n{text.lstrip()}"


def _section_pattern(heading: str) -> re.Pattern[str]:
    escaped = re.escape(heading)
    return re.compile(rf"(?ms)^## {escaped}\n.*?(?=^## |\Z)")


def _replace_section(text: str, heading: str, body: str) -> str:
    replacement = f"## {heading}\n\n{body.rstrip()}\n"
    pattern = _section_pattern(heading)
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return text.rstrip() + f"\n\n{replacement}"


def _append_section_bullets(text: str, heading: str, values: list[str]) -> str:
    if not values:
        return text
    pattern = _section_pattern(heading)
    match = pattern.search(text)
    if not match:
        return _replace_section(text, heading, _bullet_lines(values, ""))
    section = match.group(0).rstrip()
    additions = []
    for value in values:
        bullet = f"- {value}"
        if value not in section and bullet not in section:
            additions.append(bullet)
    if not additions:
        return text
    replacement = f"{section}\n" + "\n".join(additions) + "\n"
    return text[: match.start()] + replacement + text[match.end() :]


def _fill_cutline_tbd(text: str, value: str) -> str:
    replacement = f"| {value} | User supplied release-shaping note | To classify with `cutline` |"
    return text.replace("| _TBD_ | _TBD_ | _TBD_ |", replacement, 1)


def _fill_cutline_values(text: str, values: list[str]) -> str:
    for value in values:
        if "| _TBD_ | _TBD_ | _TBD_ |" in text:
            text = _fill_cutline_tbd(text, value)
        else:
            text = _append_section_bullets(text, "Cutline", [value])
    return text


def _bullet_lines(values: list[str], missing: str) -> str:
    if not values:
        return f"- TBD - {missing}"
    return "\n".join(f"- {value}" for value in values)


def _status_body(status: str) -> str:
    return (
        f"`{status}`\n\n"
        "Allowed statuses: `candidate`, `committed`, `shipping`, `shipped`, "
        "`dropped`.\n"
        "Do not move a plan from `candidate` to `committed` without an "
        "explicit user decision."
    )


def _upsert(path: Path, ns: argparse.Namespace) -> str:
    existing = path.exists()
    if existing:
        text = path.read_text(encoding="utf-8")
    else:
        text = _template_text()
    text = re.sub(r"(?m)\n*_Last shaped: \d{4}-\d{2}-\d{2}_\n*$", "", text)

    title = ns.title or _title_from_slug(ns.slug)
    text = _replace_h1(text, title)
    if ns.status or not existing:
        text = _replace_section(text, "Status", _status_body(ns.status or "candidate"))

    if existing and ns.problem:
        text = _append_section_bullets(text, "Problem / Baseline", [ns.problem])
    elif ns.problem or not existing:
        text = _replace_section(
            text,
            "Problem / Baseline",
            _bullet_lines(
                [ns.problem] if ns.problem else [],
                "ask the maintainer for the problem and baseline",
            ),
        )
    if existing and ns.appetite:
        text = _append_section_bullets(text, "Appetite", [ns.appetite])
    elif ns.appetite or not existing:
        text = _replace_section(
            text,
            "Appetite",
            _bullet_lines(
                [ns.appetite] if ns.appetite else [],
                "ask for the fixed time or attention budget",
            ),
        )
    if existing and ns.solution:
        text = _append_section_bullets(text, "Solution Outline", [ns.solution])
    elif ns.solution or not existing:
        text = _replace_section(
            text,
            "Solution Outline",
            _bullet_lines(
                [ns.solution] if ns.solution else [],
                "ask for the smallest useful release shape",
            ),
        )
    if existing and ns.risk:
        text = _append_section_bullets(text, "Risks / Rabbit Holes", ns.risk)
    elif ns.risk or not existing:
        text = _replace_section(
            text,
            "Risks / Rabbit Holes",
            _bullet_lines(ns.risk, "ask for risks and retirement paths"),
        )
    if existing and ns.no_go:
        text = _append_section_bullets(text, "No-Gos", ns.no_go)
    elif ns.no_go or not existing:
        text = _replace_section(
            text,
            "No-Gos",
            _bullet_lines(ns.no_go, "ask what this release will not do"),
        )
    if existing and ns.cutline:
        text = _append_section_bullets(text, "Cutline", ns.cutline)
    elif ns.cutline or not existing:
        if ns.cutline:
            text = _fill_cutline_values(text, ns.cutline)
    if existing and ns.jig_handoff:
        text = _append_section_bullets(text, "JIG Handoff", ns.jig_handoff)
    elif ns.jig_handoff or not existing:
        text = _replace_section(
            text,
            "JIG Handoff",
            _bullet_lines(
                ns.jig_handoff,
                "ask which JIG specs or slices should receive handoff notes",
            ),
        )
    if existing and ns.criterion:
        text = _append_section_bullets(text, "Release-Check Criteria", ns.criterion)
    elif ns.criterion or not existing:
        text = _replace_section(
            text,
            "Release-Check Criteria",
            _bullet_lines(
                ns.criterion,
                "ask what evidence should be true before shipping",
            ),
        )

    text = text.rstrip() + f"\n\n_Last shaped: {date.today().isoformat()}_\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="create or refine docs/releases/<slug>.md"
    )
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--slug", required=True, help="kebab-case release slug")
    parser.add_argument("--title", help="release-plan title")
    parser.add_argument("--status", choices=STATUSES)
    parser.add_argument("--problem")
    parser.add_argument("--appetite")
    parser.add_argument("--solution")
    parser.add_argument("--risk", action="append", default=[])
    parser.add_argument("--no-go", action="append", default=[])
    parser.add_argument("--cutline", action="append", default=[])
    parser.add_argument("--jig-handoff", action="append", default=[])
    parser.add_argument("--criterion", action="append", default=[])
    return parser


def main(argv: list[str]) -> int:
    ns = _parser().parse_args(argv[1:])
    if not SLUG_RE.fullmatch(ns.slug):
        sys.stderr.write("slug must be kebab-case lowercase letters/digits\n")
        return 2

    repo = Path(ns.repo)
    path = repo / "docs" / "releases" / f"{ns.slug}.md"
    _upsert(path, ns)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
