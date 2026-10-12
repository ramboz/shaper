"""Build shaper's committed Claude, Codex, and Copilot host packages.

The repository root is canonical source. `hosts/claude` and `hosts/codex` are
source-derived install payloads committed for remote host installation. Use
`--check` as the drift guard: it rebuilds into a scratch directory and compares
the result to the committed `hosts/` tree without mutating it.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from shaper_root import SKILLS as COPILOT_SKILLS


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

# Each installed skill must work in a fresh shell, with no host root variable
# or project instructions. Bootstrap discovery reads data only: another
# installed plugin's similarly named locator must never be executed.
COPILOT_ROOT_NOTE = '''
## Installed runtime (Copilot CLI)

Run helpers from the consuming repository; `docs/` paths belong to that
repository, not this plugin. Python 3 is required. Do not copy runtime files.
If Copilot discloses this invoked skill's absolute directory, set
`SHAPER_SKILL_DIR` to that directory (the parent of its `SKILL.md`) in the
shell below; prefer it over other installations. Do not guess a project path.
Otherwise leave `SHAPER_SKILL_DIR` unset. This bootstrap honors `COPILOT_HOME`
(default `~/.copilot`), including marketplace and direct installs, and paths
with spaces. Run it in the same shell as each helper, including fresh shells:

```bash
SHAPER_ROOT="$(python3 - <<'PY'
import json
import os
import re
import sys
from pathlib import Path
skills = __COPILOT_SKILLS__
def manifest(root):
    try:
        data = json.loads((root.parent / ".plugin/plugin.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if (not isinstance(data, dict) or data.get("name") != "shaper"
            or data.get("skills") != ".github/skills" or root.name != ".github"
            or not isinstance(data.get("version"), str)
            or not re.fullmatch(r"\\d+\\.\\d+\\.\\d+", data["version"])):
        return None
    required = ["templates/release-plan.md", "scripts/shaper_root.py"]
    for name in skills:
        required.extend((f"skills/{name}/SKILL.md",
                         f"skills/{name}/scripts/{name.replace('-', '_')}.py"))
    return data if all((root / rel).is_file() for rel in required) else None
active = os.environ.get("SHAPER_SKILL_DIR")
roots = []
if active:
    skill = Path(active).resolve()
    if skill.name == "SKILL.md":
        skill = skill.parent
    if skill.name in skills and skill.parent.name == "skills":
        roots.append(skill.parent.parent)
else:
    home = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot")
    roots = (home / "installed-plugins").glob("*/*/.github")
candidates = []
for root in roots:
    data = manifest(root)
    if data:
        candidates.append((tuple(int(part) for part in data["version"].split(".")),
                           str(root.resolve()), root.resolve()))
if not candidates:
    sys.exit("shaper_root: no valid Shaper runtime; install shaper or check COPILOT_HOME / SHAPER_SKILL_DIR")
print(max(candidates)[2])
PY
)" || { echo "Shaper runtime unavailable; stop rather than use consumer-relative helpers." >&2; exit 1; }
export SHAPER_ROOT
```

`SHAPER_ROOT` is the absolute installed `.github` runtime. Keep every helper
and template path quoted. If resolution fails, stop explicitly; do not run
a similarly named file from the consuming repository.
'''


def skill_metadata(text: str) -> tuple[dict[str, str], str]:
    """Read the owned scalar frontmatter subset, rejecting ambiguous metadata."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("skill metadata: missing frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("skill metadata: unterminated frontmatter")
    metadata = {}
    i = 1
    while i < end:
        if not lines[i].strip():
            i += 1
            continue
        match = re.fullmatch(r"([a-z][\w-]*):\s*(.*?)\s*\n?", lines[i])
        if not match or match[1] in metadata:
            raise ValueError("skill metadata: malformed or duplicate field")
        key, value = match.groups()
        if key not in ("name", "description", "user-invocable"):
            raise ValueError(f"skill metadata: unsupported field {key}")
        if key == "user-invocable" and value not in ("true", "false"):
            raise ValueError("skill metadata: user-invocable must be a boolean")
        i += 1
        if value in (">", ">-", ">+", "|", "|-", "|+"):
            parts = []
            while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                parts.append(lines[i].strip())
                i += 1
            value = (" " if value.startswith(">") else "\n").join(parts).strip()
        elif value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError as exc:
                raise ValueError(f"skill metadata: malformed {key}") from exc
        elif value.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", value):
                raise ValueError(f"skill metadata: malformed single-quoted {key}")
            value = value[1:-1].replace("''", "'")
        elif key in ("name", "description") and (
            value.startswith(("[", "{", "'", "#", "*", "&", "!", "@", "`"))
            or ": " in value
            or value.lower() in ("null", "true", "false", "~") or value.isdigit()
        ):
            raise ValueError(f"skill metadata: {key} must be a string")
        metadata[key] = value
    name = metadata.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("skill metadata: missing/invalid colon-free name")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("skill metadata: missing/invalid description")
    return metadata, "".join(lines[end + 1:])


def render_copilot_skill_md(text: str) -> str:
    metadata, body = skill_metadata(text)
    description = metadata["description"]
    metadata["description"] = description[:1021] + "..." if len(description) > 1024 else description
    header = "---\n" + "".join(
        f"{key}: {json.dumps(value, ensure_ascii=False)}\n" if key in ("name", "description")
        else f"{key}: {value}\n" for key, value in metadata.items()
    ) + "---\n"
    if len(description) > 1024:
        body = f"\n> **Full description:** {description}\n" + body
    # Runtime references only; consumer docs/ paths are deliberately untouched.
    body = re.sub(r"skills/[\w-]+/scripts/[\w_]+\.py",
                  lambda match: f'"$SHAPER_ROOT/{match[0]}"', body)
    body = body.replace('`"$SHAPER_ROOT/skills/shape-release/scripts/shape_release.py"',
                        '`python3 "$SHAPER_ROOT/skills/shape-release/scripts/shape_release.py"')
    body = body.replace("templates/release-plan.md", '"$SHAPER_ROOT/templates/release-plan.md"')
    root_note = COPILOT_ROOT_NOTE.replace("__COPILOT_SKILLS__", repr(COPILOT_SKILLS))
    return header + root_note + body


def copilot_package_errors(package: Path) -> list[str]:
    """Check actual native component paths, metadata, and the closed payload."""
    errors = []
    try:
        manifest = json.loads((package / ".plugin/plugin.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["missing/malformed .plugin/plugin.json"]
    if not isinstance(manifest, dict):
        return ["manifest metadata must be an object"]
    for field in ("name", "version", "description"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            errors.append(f"missing/invalid {field} metadata")
    if manifest.get("name") != PLUGIN_NAME:
        errors.append("name must be shaper")
    if not isinstance(manifest.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
        errors.append("invalid version")
    if manifest.get("skills") != ".github/skills" or not (package / ".github/skills").is_dir():
        errors.append("skills component path must exist at .github/skills")
    for field in ("hooks", "agents", "mcpServers", "lspServers"):
        if field in manifest:
            errors.append(f"unsupported component: {field}")
    expected = {".plugin/plugin.json", "README.md", "shaper.jpg",
                ".github/templates/release-plan.md", ".github/scripts/shaper_root.py"}
    if (package / "LICENSE").is_file():
        expected.add("LICENSE")
    for name in COPILOT_SKILLS:
        rel = f".github/skills/{name}/SKILL.md"
        expected.update((rel, f".github/skills/{name}/scripts/{name.replace('-', '_')}.py"))
        path = package / rel
        if path.is_file():
            try:
                metadata, _ = skill_metadata(path.read_text(encoding="utf-8"))
                if metadata["name"] != name or len(metadata["description"]) > 1024:
                    errors.append(f"{rel}: invalid name/description loader metadata")
            except ValueError as exc:
                errors.append(f"{rel}: {exc}")
    actual = set(_file_map(package))
    errors.extend(f"missing required file: {rel}" for rel in sorted(expected - actual))
    errors.extend(f"excluded/unexpected file: {rel}" for rel in sorted(actual - expected))
    return errors


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


def build_copilot_package(source_root: Path, hosts_root: Path) -> int:
    output = hosts_root / "copilot"
    try:
        manifest = json.loads((source_root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("name") != PLUGIN_NAME:
            raise ValueError("invalid canonical Shaper manifest")
        if not isinstance(manifest.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
            raise ValueError("missing/invalid canonical version")
        rendered = {
            name: render_copilot_skill_md((source_root / f"skills/{name}/SKILL.md").read_text(encoding="utf-8"))
            for name in COPILOT_SKILLS
        }
        manifest = {**manifest, "description": "Release shaping before implementation starts for Copilot CLI",
                    "skills": ".github/skills"}
        if output.exists():
            shutil.rmtree(output)
        (output / ".plugin").mkdir(parents=True)
        (output / ".plugin/plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        for name in OPTIONAL_ROOT_FILES:
            _copy_optional_file(source_root, output, name)
        runtime = output / ".github"
        for name, text in rendered.items():
            skill = runtime / "skills" / name
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(text, encoding="utf-8")
            helper = f"{name.replace('-', '_')}.py"
            (skill / "scripts" / helper).write_bytes((source_root / "skills" / name / "scripts" / helper).read_bytes())
        (runtime / "templates").mkdir()
        (runtime / "templates/release-plan.md").write_bytes((source_root / "templates/release-plan.md").read_bytes())
        (runtime / "scripts").mkdir()
        (runtime / "scripts/shaper_root.py").write_bytes((source_root / "scripts/shaper_root.py").read_bytes())
        errors = copilot_package_errors(output)
        if errors:
            raise ValueError("; ".join(errors))
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"ERROR: Copilot package: {exc}\n")
        return 1
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
    copilot_code = build_copilot_package(source_root, hosts_root)
    if claude_code == 0:
        out.write(f"OK: built Claude package at {hosts_root / 'claude'}\n")
    if codex_code == 0:
        out.write(f"OK: built Codex package at {hosts_root / 'codex'}\n")
    if copilot_code == 0:
        out.write(f"OK: built Copilot package at {hosts_root / 'copilot'}\n")
    return claude_code or codex_code or copilot_code


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
