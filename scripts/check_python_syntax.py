"""Syntax-check Python files without writing bytecode caches."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def check(paths: list[str]) -> int:
    for raw_path in paths:
        path = Path(raw_path)
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        sys.stderr.write("usage: check_python_syntax.py FILE [FILE ...]\n")
        return 2
    return check(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
