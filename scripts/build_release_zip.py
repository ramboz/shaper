"""Build and smoke-test shaper's host-explicit release archives."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "shaper"
HOSTS = ("claude", "codex")
HOST_MANIFESTS = {
    "claude": ".claude-plugin/plugin.json",
    "codex": f"plugins/{PLUGIN_NAME}/.codex-plugin/plugin.json",
}
REQUIRED_FILES = {
    "claude": (
        ".claude-plugin/plugin.json",
        "README.md",
        "skills/shape-release/SKILL.md",
        "skills/shape-release/scripts/shape_release.py",
        "skills/cutline/SKILL.md",
        "skills/cutline/scripts/cutline.py",
        "skills/release-slate/SKILL.md",
        "skills/release-slate/scripts/release_slate.py",
        "templates/release-plan.md",
    ),
    "codex": (
        ".agents/plugins/marketplace.json",
        f"plugins/{PLUGIN_NAME}/.codex-plugin/plugin.json",
        f"plugins/{PLUGIN_NAME}/README.md",
        f"plugins/{PLUGIN_NAME}/skills/shape-release/SKILL.md",
        f"plugins/{PLUGIN_NAME}/skills/shape-release/scripts/shape_release.py",
        f"plugins/{PLUGIN_NAME}/skills/cutline/SKILL.md",
        f"plugins/{PLUGIN_NAME}/skills/cutline/scripts/cutline.py",
        f"plugins/{PLUGIN_NAME}/skills/release-slate/SKILL.md",
        f"plugins/{PLUGIN_NAME}/skills/release-slate/scripts/release_slate.py",
        f"plugins/{PLUGIN_NAME}/templates/release-plan.md",
    ),
}
FORBIDDEN_PREFIXES = {
    "claude": (
        ".codex-plugin/",
        ".github/",
        ".jig/",
        "docs/",
        "hosts/",
        "scripts/",
        "tests/",
    ),
    "codex": (
        ".claude-plugin/",
        ".codex-plugin/",
        ".github/",
        ".jig/",
        "docs/",
        "hosts/",
        "scripts/",
        "tests/",
    ),
}
EXCLUDED_DIR_NAMES = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache"})
EXCLUDED_FILE_NAMES = frozenset({".DS_Store"})
EXCLUDED_FILE_SUFFIXES = (".pyc",)
DETERMINISTIC_MTIME = (2026, 1, 1, 0, 0, 0)


def default_output_path(source_root: Path, host: str, version: str) -> Path:
    return source_root / "dist" / f"shaper-{host}-v{version}.zip"


def expected_output_name(host: str, version: str) -> str:
    return f"shaper-{host}-v{version}.zip"


def host_package_root(hosts_root: Path, host: str) -> Path:
    return hosts_root / host


def _is_excluded(rel: Path) -> bool:
    if any(part in EXCLUDED_DIR_NAMES for part in rel.parts[:-1]):
        return True
    if rel.name in EXCLUDED_FILE_NAMES:
        return True
    return any(rel.name.endswith(suffix) for suffix in EXCLUDED_FILE_SUFFIXES)


def _iter_files(package_root: Path) -> Iterable[Path]:
    for path in package_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(package_root)
        if not _is_excluded(rel):
            yield rel


def _zip_entry(zf: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(filename=arcname, date_time=DETERMINISTIC_MTIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o644 & 0xFFFF) << 16
    info.create_system = 3
    zf.writestr(info, data)


def _manifest_version(package_root: Path, host: str) -> tuple[str | None, str | None]:
    manifest = package_root / HOST_MANIFESTS[host]
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"missing committed {host} package manifest at {manifest}"
    except json.JSONDecodeError as exc:
        return None, f"{manifest}: invalid JSON: {exc.msg}"

    version = data.get("version")
    if not isinstance(version, str) or not version:
        return None, f"{manifest}: missing string version"
    return version, None


def build(
    host: str,
    hosts_root: Path,
    version: str,
    output_path: Path,
    out=None,
) -> int:
    if out is None:
        out = sys.stdout
    if host not in HOSTS:
        out.write(f"FAIL: unknown host {host!r}; expected one of {HOSTS}\n")
        return 1

    package_root = host_package_root(hosts_root, host)
    if not package_root.is_dir():
        out.write(
            f"FAIL: committed {host} package missing at {package_root}; "
            "run python3 scripts/build_host_packages.py\n"
        )
        return 1

    package_version, error = _manifest_version(package_root, host)
    if error:
        out.write(f"FAIL: {error}\n")
        return 1
    if package_version != version:
        out.write(
            f"FAIL: version mismatch: requested {version!r}, but the committed "
            f"{host} package declares {package_version!r}. Refusing to produce "
            "a mislabeled artifact.\n"
        )
        return 2
    expected_name = expected_output_name(host, version)
    if output_path.name != expected_name:
        out.write(
            f"FAIL: output filename must be {expected_name!r} for host {host!r} "
            f"and version {version!r}; got {output_path.name!r}. Refusing to "
            "produce a mislabeled artifact.\n"
        )
        return 2

    entries = sorted(_iter_files(package_root), key=lambda path: path.as_posix())
    if not entries:
        out.write(f"FAIL: committed {host} package at {package_root} is empty\n")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in entries:
            _zip_entry(zf, rel.as_posix(), (package_root / rel).read_bytes())

    if host == "claude":
        out.write(
            f"OK: built {output_path} as a flat Claude Code plugin archive "
            f"with {len(entries)} entries.\n"
        )
    else:
        out.write(
            f"OK: built {output_path} as an extract-then-add Codex marketplace "
            f"bundle with {len(entries)} entries.\n"
        )
    return 0


def _version_from_zip_name(zip_path: Path) -> str | None:
    match = re.search(r"-v(?P<version>\d+\.\d+\.\d+)\.zip$", zip_path.name)
    if not match:
        return None
    return match.group("version")


def _manifest_version_from_zip(
    zf: zipfile.ZipFile, host: str
) -> tuple[str | None, str | None]:
    manifest = HOST_MANIFESTS[host]
    try:
        raw = zf.read(manifest)
    except KeyError:
        return None, f"missing {manifest}"
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"{manifest}: invalid JSON: {exc.msg}"
    version = data.get("version")
    if not isinstance(version, str) or not version:
        return None, f"{manifest}: missing string version"
    return version, None


def smoke_test(host: str, zip_path: Path, expected_version: str | None = None, out=None) -> int:
    if out is None:
        out = sys.stdout
    if host not in HOSTS:
        out.write(f"FAIL smoke[{host}]: unknown host {host!r}; expected one of {HOSTS}\n")
        return 1
    if not zip_path.is_file():
        out.write(f"FAIL smoke[{host}]: zip not found at {zip_path}\n")
        return 1

    if expected_version is None:
        expected_version = _version_from_zip_name(zip_path)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())
            missing = sorted(set(REQUIRED_FILES[host]) - names)
            forbidden = sorted(
                name
                for name in names
                if any(name.startswith(prefix) for prefix in FORBIDDEN_PREFIXES[host])
            )
            junk = sorted(
                name
                for name in names
                if "__pycache__" in Path(name).parts
                or name.endswith(".pyc")
                or Path(name).name == ".DS_Store"
            )
            manifest_version, error = _manifest_version_from_zip(zf, host)
    except zipfile.BadZipFile as exc:
        out.write(f"FAIL smoke[{host}]: invalid zip archive: {exc}\n")
        return 1

    problems: list[str] = []
    if missing:
        problems.append("missing required file(s): " + ", ".join(missing))
    if forbidden:
        problems.append("contains repo-only file(s): " + ", ".join(forbidden))
    if junk:
        problems.append("contains nondistribution file(s): " + ", ".join(junk))
    if error:
        problems.append(error)
    if expected_version and manifest_version and manifest_version != expected_version:
        problems.append(
            f"version mismatch: zip name/version is {expected_version!r}, "
            f"manifest declares {manifest_version!r}"
        )

    if problems:
        out.write(f"FAIL smoke[{host}]: " + "; ".join(problems) + "\n")
        return 1

    if host == "claude":
        out.write(
            "PASS smoke[claude]: flat Claude Code plugin archive validated "
            "with .claude-plugin/plugin.json at the root.\n"
        )
    else:
        out.write(
            "PASS smoke[codex]: extract-then-add Codex marketplace bundle "
            "validated.\n"
        )
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="build or smoke-test host-explicit shaper release archives"
    )
    parser.add_argument("--host", required=True, choices=HOSTS)
    parser.add_argument("--version")
    parser.add_argument("--output")
    parser.add_argument("--source-root", default=str(ROOT))
    parser.add_argument("--hosts-root")
    parser.add_argument("--smoke-test", metavar="ZIP")
    return parser


def main(argv: list[str]) -> int:
    ns = _build_parser().parse_args(argv[1:])
    source_root = Path(ns.source_root)
    hosts_root = Path(ns.hosts_root) if ns.hosts_root else source_root / "hosts"

    if ns.smoke_test:
        return smoke_test(
            host=ns.host,
            zip_path=Path(ns.smoke_test),
            expected_version=ns.version,
        )

    if not ns.version:
        sys.stderr.write("ERROR: --version is required unless --smoke-test is given\n")
        return 2

    output = (
        Path(ns.output)
        if ns.output
        else default_output_path(source_root, ns.host, ns.version)
    )
    return build(
        host=ns.host,
        hosts_root=hosts_root,
        version=ns.version,
        output_path=output,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
