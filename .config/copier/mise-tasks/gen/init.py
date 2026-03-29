#!/usr/bin/env python
import argparse
import ast
import os
import subprocess
from pathlib import Path

TEMPLATE: str = """\
from liblaf.lazy_loader import attach_stub

__getattr__, __dir__, __all__ = attach_stub(__name__, __package__, __file__)

del attach_stub
"""


class Args(argparse.Namespace):
    path: Path


def parse_args() -> Args:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path)
    args: argparse.Namespace = parser.parse_args(namespace=Args())
    if args.path is None:
        if (path := os.getenv("MISE_PROJECT_ROOT")) is not None:
            args.path = Path(path)
        else:
            args.path = Path.cwd()
    return args


def git_ls_files(path: Path) -> list[Path]:
    result: subprocess.CompletedProcess[str] = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            f"{path}/**/__init__.pyi",
        ],
        stdout=subprocess.PIPE,
        check=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line]


def get_docstring(file: Path) -> str | None:
    if not file.exists():
        return None
    source: str = file.read_text()
    module: ast.Module = ast.parse(source)
    if not (module.body and isinstance(module.body[0], ast.Expr)):
        return None
    node: ast.expr = module.body[0].value
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return ast.get_source_segment(source, node)
    return None


def render_init(file: Path) -> str:
    docstring: str | None = get_docstring(file)
    if docstring is None:
        return TEMPLATE
    return f"{docstring}\n\n{TEMPLATE}"


def main() -> None:
    args: Args = parse_args()
    for pyi in git_ls_files(args.path):
        py: Path = pyi.with_suffix(".py")
        content: str = render_init(py)
        if py.exists():
            if py.read_text() == content:
                print("skipped:", py)
            else:
                print("updated:", py)
                py.write_text(content)
        else:
            print("created:", py)
            py.write_text(content)


if __name__ == "__main__":
    main()
