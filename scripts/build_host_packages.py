"""Build shaper's committed Claude and Codex host packages.

The repository root is canonical source. `hosts/claude` and `hosts/codex` are
source-derived install payloads committed for remote host installation. Use
`--check` as the drift guard: it rebuilds into a scratch directory and compares
the result to the committed `hosts/` tree without mutating it.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "shaper"
REGEN_COMMAND = "python3 scripts/build_host_packages.py"
OPTIONAL_ROOT_FILES = ("README.md", "LICENSE", "shaper.jpg")
OPTIONAL_RUNTIME_DIRS = ("skills", "templates", "agents", "hooks")
EXCLUDED_DIR_NAMES = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache"})
EXCLUDED_FILE_SUFFIXES = (".pyc",)
SOURCE_OWNED_DIRS = (
    ".claude-plugin",
    ".codex-plugin",
    ".codex",
    ".jig",
    "docs",
    "scripts",
    "tests",
    "hosts",
)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _is_excluded(path: Path) -> bool:
    if any(part in EXCLUDED_DIR_NAMES for part in path.parts[:-1]):
        return True
    return any(path.name.endswith(suffix) for suffix in EXCLUDED_FILE_SUFFIXES)


def _validate_hosts_root(source_root: Path, hosts_root: Path) -> tuple[bool, str]:
    source_root = source_root.resolve()
    hosts_root = hosts_root.resolve()
    if hosts_root == source_root:
        return False, "hosts root must not be the source root"
    if hosts_root in source_root.parents:
        return False, "hosts root must not be an ancestor of the source root"
    if source_root in hosts_root.parents:
        if not (
            _is_relative_to(hosts_root, source_root / "hosts")
            or _is_relative_to(hosts_root, source_root / "dist")
        ):
            return False, "in-tree hosts root must be under hosts/ or dist/"
        source_owned = {source_root / name for name in SOURCE_OWNED_DIRS}
        if hosts_root in source_owned or any(root in hosts_root.parents for root in source_owned):
            if not _is_relative_to(hosts_root, source_root / "hosts"):
                return False, "hosts root must not be a source-owned path"
    return True, ""


def _copy_optional_file(source_root: Path, output_dir: Path, name: str) -> None:
    src = source_root / name
    if src.is_file():
        (output_dir / name).write_bytes(src.read_bytes())


def _copy_runtime_dir(source_root: Path, output_dir: Path, name: str) -> None:
    src_dir = source_root / name
    if not src_dir.is_dir():
        return
    for src in sorted(src_dir.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(src_dir)
        if _is_excluded(rel):
            continue
        dst = output_dir / name / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())


def _load_codex_manifest(source_root: Path) -> dict:
    return json.loads((source_root / ".codex-plugin" / "plugin.json").read_text())


def _write_codex_marketplace(host_root: Path, source_root: Path) -> None:
    manifest = _load_codex_manifest(source_root)
    payload = {
        "name": PLUGIN_NAME,
        "interface": {"displayName": manifest["interface"]["displayName"]},
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": {
                    "source": "local",
                    "path": f"./plugins/{PLUGIN_NAME}",
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": manifest["interface"]["category"],
            }
        ],
    }
    path = host_root / ".agents" / "plugins" / "marketplace.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_claude_package(source_root: Path, hosts_root: Path) -> int:
    source_root = source_root.resolve()
    output_dir = hosts_root.resolve() / "claude"
    manifest = source_root / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        sys.stderr.write(f"ERROR: missing {manifest}\n")
        return 1

    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir / ".claude-plugin").mkdir(parents=True)
    (output_dir / ".claude-plugin" / "plugin.json").write_bytes(manifest.read_bytes())
    for name in OPTIONAL_ROOT_FILES:
        _copy_optional_file(source_root, output_dir, name)
    for name in OPTIONAL_RUNTIME_DIRS:
        _copy_runtime_dir(source_root, output_dir, name)
    return 0


def build_codex_package(source_root: Path, hosts_root: Path) -> int:
    source_root = source_root.resolve()
    host_root = hosts_root.resolve() / "codex"
    plugin_root = host_root / "plugins" / PLUGIN_NAME
    manifest = source_root / ".codex-plugin" / "plugin.json"
    if not manifest.is_file():
        sys.stderr.write(f"ERROR: missing {manifest}\n")
        return 1

    if host_root.exists():
        shutil.rmtree(host_root)
    (plugin_root / ".codex-plugin").mkdir(parents=True)
    (plugin_root / ".codex-plugin" / "plugin.json").write_bytes(manifest.read_bytes())
    for name in OPTIONAL_ROOT_FILES:
        _copy_optional_file(source_root, plugin_root, name)
    for name in OPTIONAL_RUNTIME_DIRS:
        _copy_runtime_dir(source_root, plugin_root, name)
    _write_codex_marketplace(host_root, source_root)
    return 0


def build_all(source_root: Path, hosts_root: Path, out=None) -> int:
    if out is None:
        out = sys.stdout
    source_root = source_root.resolve()
    hosts_root = hosts_root.resolve()
    ok, reason = _validate_hosts_root(source_root, hosts_root)
    if not ok:
        out.write(f"ERROR: unsafe hosts root: {reason}: {hosts_root}\n")
        return 1

    claude_code = build_claude_package(source_root, hosts_root)
    codex_code = build_codex_package(source_root, hosts_root)
    if claude_code == 0:
        out.write(f"OK: built Claude package at {hosts_root / 'claude'}\n")
    if codex_code == 0:
        out.write(f"OK: built Codex package at {hosts_root / 'codex'}\n")
    return claude_code or codex_code


def _is_ephemeral(rel: Path) -> bool:
    return "__pycache__" in rel.parts or rel.suffix == ".pyc"


def _file_map(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    if not root.is_dir():
        return result
    for path in sorted(root.rglob("*")):
        if path.is_file() and not _is_ephemeral(path.relative_to(root)):
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def _diff_packages(expected_root: Path, committed_root: Path) -> list[str]:
    expected = _file_map(expected_root)
    committed = _file_map(committed_root)
    drifted = set()
    for rel, data in expected.items():
        if committed.get(rel) != data:
            drifted.add(rel)
    for rel in committed:
        if rel not in expected:
            drifted.add(rel)
    return sorted(drifted)


def check_drift(source_root: Path, hosts_root: Path, out=None) -> int:
    if out is None:
        out = sys.stdout
    source_root = source_root.resolve()
    hosts_root = hosts_root.resolve()
    scratch = Path(tempfile.mkdtemp(prefix="shaper-host-drift-"))
    try:
        sink = type("_Sink", (), {"write": staticmethod(lambda *_args, **_kwargs: None)})()
        code = build_all(source_root=source_root, hosts_root=scratch, out=sink)
        if code != 0:
            out.write(f"ERROR: could not regenerate host packages (exit {code}).\n")
            return 1

        drifted = _diff_packages(scratch, hosts_root)
        if not drifted:
            out.write("OK: committed host packages are in sync with source.\n")
            return 0

        out.write("ERROR: committed host packages are stale relative to source.\n")
        for rel in drifted:
            out.write(f"  - hosts/{rel}\n")
        out.write(
            "Regenerate and commit the host packages:\n"
            f"    {REGEN_COMMAND}\n"
        )
        return 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="build or check shaper's committed host packages"
    )
    parser.add_argument("--source-root", default=str(ROOT))
    parser.add_argument("--hosts-root", default=None)
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate in a scratch dir and diff against committed hosts/",
    )
    return parser


def main(argv: list[str]) -> int:
    ns = _build_parser().parse_args(argv[1:])
    source_root = Path(ns.source_root)
    hosts_root = Path(ns.hosts_root) if ns.hosts_root else source_root / "hosts"
    if ns.check:
        return check_drift(source_root=source_root, hosts_root=hosts_root)
    return build_all(source_root=source_root, hosts_root=hosts_root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
