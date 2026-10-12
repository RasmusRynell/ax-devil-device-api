"""Spec patches: RFC 6902-style operations with an ``expect`` guard (design section 8)."""

from __future__ import annotations

import copy
from typing import Any


class PatchError(ValueError):
    pass


def _tokens(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise PatchError(f"invalid JSON pointer {pointer!r}")
    return [t.replace("~1", "/").replace("~0", "~") for t in pointer[1:].split("/")]


def _child(container: Any, token: str, pointer: str) -> Any:
    try:
        if isinstance(container, list):
            return container[int(token)]
        return container[token]
    except (KeyError, IndexError, ValueError, TypeError):
        raise PatchError(f"patch path {pointer!r} does not exist (failed at {token!r})") from None


def get_pointer(doc: Any, pointer: str) -> Any:
    node = doc
    for token in _tokens(pointer):
        node = _child(node, token, pointer)
    return node


def apply_patch(spec: dict[str, Any], ops: list[dict[str, Any]], *, source: str = "patch") -> dict[str, Any]:
    """Return a patched deep copy of ``spec``. Any mismatch raises ``PatchError``."""
    doc = copy.deepcopy(spec)
    for index, op in enumerate(ops):
        where = f"{source} #{index + 1} ({op.get('op')} {op.get('path')})"
        kind = op.get("op")
        if kind not in ("add", "replace", "remove"):
            raise PatchError(f"{where}: unknown op {kind!r}")
        if "path" not in op:
            raise PatchError(f"{where}: missing path")
        tokens = _tokens(op["path"])
        if not tokens:
            raise PatchError(f"{where}: cannot patch the document root")
        parent = get_pointer(doc, "/" + "/".join(t.replace("~", "~0").replace("/", "~1") for t in tokens[:-1])) if len(tokens) > 1 else doc
        last = tokens[-1]
        try:
            if "expect" in op:
                current = _child(parent, last, op["path"]) if not (isinstance(parent, list) and last == "-") else None
                if current != op["expect"]:
                    raise PatchError(f"{where}: expected {op['expect']!r} but found {current!r}; the base spec changed")
            if kind != "remove" and "value" not in op:
                raise PatchError(f"{where}: missing value")
            if isinstance(parent, list):
                if kind == "add":
                    parent.insert(len(parent) if last == "-" else int(last), copy.deepcopy(op["value"]))
                elif kind == "replace":
                    parent[int(last)] = copy.deepcopy(op["value"])
                else:
                    del parent[int(last)]
            elif isinstance(parent, dict):
                if kind in ("replace", "remove") and last not in parent:
                    raise PatchError(f"{where}: path does not exist")
                if kind == "remove":
                    del parent[last]
                else:
                    parent[last] = copy.deepcopy(op["value"])
            else:
                raise PatchError(f"{where}: parent is not a container")
        except (IndexError, ValueError) as error:
            if isinstance(error, PatchError):
                raise
            raise PatchError(f"{where}: {error}") from None
    return doc
