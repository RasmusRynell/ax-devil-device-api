"""Async examples in the docs must compile and use the AsyncDevice API correctly.

On ``AsyncDevice`` a streaming operation is a coroutine returning the stream, so it is entered as
``async with await adev.apis.<api>.<op>(...)``. A session's ``connect(...)`` is not a coroutine: ``async with ...connect(...)``.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "README.md",
    ROOT / "docs" / "design.md",
    ROOT / "docs" / "spec-format.md",
    *sorted((ROOT / ".github" / "skills").rglob("*.md")),
]
FENCE = re.compile(r"```python\n(.*?)```", re.S)


def async_blocks() -> list[tuple[str, str]]:
    blocks = []
    for path in FILES:
        for index, match in enumerate(FENCE.finditer(path.read_text(encoding="utf-8"))):
            code = match.group(1)
            if "async " in code or "await " in code:
                blocks.append((f"{path.relative_to(ROOT).as_posix()}#{index}", code))
    return blocks


def _is_api_call(node: ast.expr) -> bool:
    """A call like ``adev.apis.media_stream.get_media_stream(...)`` that is not awaited."""
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return False
    names = []
    current: ast.expr = node.func
    while isinstance(current, ast.Attribute):
        names.append(current.attr)
        current = current.value
    return "apis" in names and node.func.attr != "connect"


@pytest.mark.parametrize(("where", "code"), async_blocks(), ids=lambda v: v if isinstance(v, str) and "#" in v else "")
def test_async_blocks_compile_and_await_stream_operations(where: str, code: str) -> None:
    tree = compile(code, where, "exec", flags=ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    compile(code, where, "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncWith):
            for item in node.items:
                assert not _is_api_call(item.context_expr), f"{where}: `async with` needs `await` before the API call (line {node.lineno})"
        if isinstance(node, ast.AsyncFor):
            assert not _is_api_call(node.iter), f"{where}: `async for` needs `await` before the API call (line {node.lineno})"


def test_there_are_async_examples_to_check() -> None:
    assert len(async_blocks()) >= 3


def test_the_checker_catches_the_original_mistake() -> None:
    bad = 'async with adev.apis.media_stream.get_media_stream(container="mp4") as stream:\n    pass\n'
    tree = ast.parse(bad)
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncWith))
    assert _is_api_call(node.items[0].context_expr)
    good = ast.parse('async with await adev.apis.media_stream.get_media_stream() as s:\n    pass\n')
    node = next(n for n in ast.walk(good) if isinstance(n, ast.AsyncWith))
    assert not _is_api_call(node.items[0].context_expr)
