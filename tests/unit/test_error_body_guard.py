"""Response body text enters an exception only through ``body_excerpt(op, ...)`` (or the generic ``redact_text``).

A scan of the runtime source: any exception/error construction whose arguments read ``.text``, ``.content``,
``.safe_text`` or call ``.excerpt()`` outside those helpers fails. Adding a new bypass fails CI; a justified exception
goes in ALLOWED below with a reason.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[2] / "src" / "ax_devil_device_api"
SCANNED = ("_protocols", "_runtime", "_http")
BODY_ATTRIBUTES = {"text", "content", "safe_text", "excerpt"}
SANCTIONED = {"body_excerpt", "redact_text"}
ERROR_CALL = re.compile(r"(Error|Denied|Unavailable|NotSupported|SessionClosed)$|^(api_error|http_error)$")

# (file relative to the package, enclosing function): why raw body text may appear in that error.
ALLOWED: dict[tuple[str, str], str] = {
    # ``api_error(..., details=response.safe_text)``: the raw text goes to ``details`` only, and api_error itself puts
    # it through ``_safe_details`` (omitted for an operation that returns secret fields, otherwise redacted and bounded).
    ("_protocols/base.py", "http_error"): "details= is sanitized inside api_error (_safe_details)",
    ("_protocols/rest.py", "_decode"): "details= is sanitized inside api_error (_safe_details)",
}


def _callee(node: ast.Call) -> str:
    func = node.func
    return func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""


def _reads_body(node: ast.AST) -> bool:
    """Whether the subtree reads body text, not counting what sits inside a sanctioned helper call."""
    if isinstance(node, ast.Call) and _callee(node) in SANCTIONED:
        return False
    if isinstance(node, ast.Attribute) and node.attr in BODY_ATTRIBUTES:
        return True
    return any(_reads_body(child) for child in ast.iter_child_nodes(node))


def _violations() -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for folder in SCANNED:
        for path in sorted((PACKAGE / folder).rglob("*.py")):
            tree = ast.parse(path.read_text())
            relative = path.relative_to(PACKAGE).as_posix()

            def visit(node: ast.AST, function: str) -> None:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function = node.name
                if isinstance(node, ast.Call) and ERROR_CALL.search(_callee(node)):
                    args = [*node.args, *(keyword.value for keyword in node.keywords)]
                    if any(_reads_body(arg) for arg in args):
                        found.add((relative, function))
                for child in ast.iter_child_nodes(node):
                    visit(child, function)

            visit(tree, "<module>")
    return found


def test_response_body_text_only_enters_errors_through_body_excerpt() -> None:
    unexpected = sorted(_violations() - set(ALLOWED))
    assert not unexpected, (
        "raw response body text is put into an exception here; route it through body_excerpt(op, ...) "
        f"(or redact_text where there is no operation): {unexpected}"
    )


def test_every_allow_list_entry_is_still_needed() -> None:
    stale = sorted(set(ALLOWED) - _violations())
    assert not stale, f"remove these from ALLOWED, they no longer read body text: {stale}"
