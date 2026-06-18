"""Validate shaper plugin manifests and committed host-package manifests."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class ManifestSpec:
    path: str
    required_fields: tuple[str, ...]


MANIFESTS = (
    ManifestSpec(
        ".claude-plugin/plugin.json",
        ("name", "version", "description", "author.name"),
    ),
    ManifestSpec(
        ".claude-plugin/marketplace.json",
        ("name", "owner.name", "plugins"),
    ),
    ManifestSpec(
        ".codex-plugin/plugin.json",
        ("name", "version", "description", "interface.displayName", "interface.category"),
    ),
    ManifestSpec(
        "hosts/claude/.claude-plugin/plugin.json",
        ("name", "version", "description", "author.name"),
    ),
    ManifestSpec(
        "hosts/codex/.agents/plugins/marketplace.json",
        ("name", "plugins"),
    ),
    ManifestSpec(
        "hosts/codex/plugins/shaper/.codex-plugin/plugin.json",
        ("name", "version", "description", "interface.displayName", "interface.category"),
    ),
)


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing file"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc.msg}"
    if not isinstance(data, dict):
        return None, "manifest root must be a JSON object"
    return data, None


def _get_field(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _check_required(data: dict[str, Any], spec: ManifestSpec) -> list[str]:
    errors: list[str] = []
    for field in spec.required_fields:
        value = _get_field(data, field)
        if value is None or value == "":
            errors.append(f"missing required field '{field}'")
    return errors


def _versions_match(manifests: dict[str, dict[str, Any]]) -> list[str]:
    version_paths = (
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        "hosts/claude/.claude-plugin/plugin.json",
        "hosts/codex/plugins/shaper/.codex-plugin/plugin.json",
    )
    versions = {
        path: manifests[path]["version"]
        for path in version_paths
        if path in manifests and "version" in manifests[path]
    }
    if len(set(versions.values())) <= 1:
        return []
    details = ", ".join(f"{path}={version}" for path, version in versions.items())
    return [f"version mismatch across plugin manifests: {details}"]


def _check_marketplaces(manifests: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    claude = manifests.get(".claude-plugin/marketplace.json")
    codex = manifests.get("hosts/codex/.agents/plugins/marketplace.json")

    if claude:
        plugins = claude.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            errors.append(".claude-plugin/marketplace.json: plugins must be a non-empty list")
        else:
            source = plugins[0].get("source") if isinstance(plugins[0], dict) else None
            if not isinstance(source, dict) or source.get("path") != "hosts/claude":
                errors.append(
                    ".claude-plugin/marketplace.json: first plugin source.path must be hosts/claude"
                )

    if codex:
        plugins = codex.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            errors.append("hosts/codex/.agents/plugins/marketplace.json: plugins must be a non-empty list")
        else:
            plugin = plugins[0]
            if not isinstance(plugin, dict):
                errors.append("hosts/codex/.agents/plugins/marketplace.json: first plugin must be an object")
            else:
                source = plugin.get("source")
                if not isinstance(source, dict) or source.get("path") != "./plugins/shaper":
                    errors.append(
                        "hosts/codex/.agents/plugins/marketplace.json: first plugin source.path must be ./plugins/shaper"
                    )
    return errors


def validate(root: Path = ROOT, out=None) -> int:
    if out is None:
        out = sys.stdout
    root = root.resolve()
    errors: list[str] = []
    manifests: dict[str, dict[str, Any]] = {}
    valid_manifest_paths: set[str] = set()

    for spec in MANIFESTS:
        data, error = _load_json(root / spec.path)
        if error:
            errors.append(f"{spec.path}: {error}")
            continue
        assert data is not None
        manifests[spec.path] = data
        field_errors = _check_required(data, spec)
        for field_error in field_errors:
            errors.append(f"{spec.path}: {field_error}")
        if not field_errors:
            valid_manifest_paths.add(spec.path)

    errors.extend(_versions_match(manifests))
    errors.extend(_check_marketplaces(manifests))

    if errors:
        for error in errors:
            out.write(f"ERROR: {error}\n")
        out.write(f"{len(valid_manifest_paths)}/{len(MANIFESTS)} manifest(s) valid\n")
        return 1

    out.write(f"OK: {len(MANIFESTS)}/{len(MANIFESTS)} manifest(s) valid\n")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="validate shaper plugin manifests")
    parser.add_argument("--root", default=str(ROOT), help="repository root to validate")
    return parser


def main(argv: list[str]) -> int:
    ns = _build_parser().parse_args(argv[1:])
    return validate(root=Path(ns.root))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
