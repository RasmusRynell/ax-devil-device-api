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


# -- device error TEXT (an envelope message, an ``Error:`` line) ------------------------------------------------------

API_ERRORS = {"ApiError", "ApiAccessDenied", "ApiUnavailable"}
# The only places allowed to construct an API error from device text; both put it through a redactor first.
API_ERROR_BUILDERS = {("_protocols/base.py", "api_error"), ("_runtime/ws_codecs.py", "api_error")}


def test_api_errors_are_only_built_in_the_two_funnels() -> None:
    built: set[tuple[str, str]] = set()
    for folder in SCANNED:
        for path in sorted((PACKAGE / folder).rglob("*.py")):
            relative = path.relative_to(PACKAGE).as_posix()

            def visit(node: ast.AST, function: str, relative: str = relative) -> None:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function = node.name
                if isinstance(node, ast.Call) and (_callee(node) in API_ERRORS or (_callee(node) == "cls" and function == "api_error")):
                    built.add((relative, function))
                for child in ast.iter_child_nodes(node):
                    visit(child, function)

            visit(ast.parse(path.read_text()), "<module>")
    assert built <= API_ERROR_BUILDERS, f"build API errors only through api_error (error_text): {sorted(built - API_ERROR_BUILDERS)}"


def test_the_device_message_in_api_error_only_feeds_lookups_and_error_text() -> None:
    """In ``api_error`` the raw ``message`` may be used for the code lookup and inside ``error_text(...)`` only."""
    tree = ast.parse((PACKAGE / "_protocols" / "base.py").read_text())
    function = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "api_error")
    allowed_callees = {"error_text", "error_code", "isinstance"}
    offenders: list[int] = []

    def walk(node: ast.AST, inside: bool) -> None:
        if isinstance(node, ast.Call) and _callee(node) in allowed_callees:
            inside = True
        if isinstance(node, ast.IfExp):  # ``... if message else ...`` only tests presence; it does not put the text anywhere
            walk(node.body, inside)
            walk(node.orelse, inside)
            return
        if isinstance(node, ast.Name) and node.id == "message" and isinstance(node.ctx, ast.Load) and not inside:
            offenders.append(node.lineno)
        for child in ast.iter_child_nodes(node):
            walk(child, inside)

    for statement in function.body:
        walk(statement, False)
    assert not offenders, f"device message used outside error_text/lookup in api_error at lines {offenders}"


# -- device-derived values interpolated into a format error ---------------------------------------------------------------

FORMAT_ERROR = "ResponseFormatError"
SAFE_FORMATTERS = {"error_text", "body_excerpt", "redact_text", "display_text", "_kind"}
# (file, unparsed expression) -> why the value cannot carry device text. Any other value in a ResponseFormatError message
# (a method name, version, key, id, header value, ...) must go through one of SAFE_FORMATTERS.
EXEMPT_VALUES: dict[tuple[str, str], str] = {
    ("_protocols/jsonrpc.py", "negotiation.key"): "the key the SPEC names (apiVersions), not a device value",
    ("_protocols/jsonrpc.py", "binding.method!r"): "the method WE asked for (from the spec)",
    ("_protocols/base.py", "message"): "_shape_message(): field names and error types only, omitted for secret operations",
    ("_protocols/cgi.py", "error"): "an expat ParseError: fixed vocabulary plus a position; XmlDeclarationError has a fixed text",
    ("_runtime/ws_codecs.py", "where"): "a fixed label chosen by the codec",
    ("_runtime/ws_codecs.py", "fields"): "only declared TopicSampleParams field names (anything else is 'an unexpected field')",
    ("_runtime/ws.py", "reason"): "the JSON decoder's position-only message (non-finite constants are fixed names)",
    ("_runtime/ws.py", "MAX_WS_MESSAGE_BYTES"): "a constant",
    ("_streams.py", "self._length"): "an integer (a parsed Content-Length), never text",
    ("_streams.py", "self._max"): "our configured limit, an integer",
}


def _format_error_values() -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    # the whole package: a format error built anywhere (the streams, the device facade) is held to the same rule
    for path in sorted(PACKAGE.rglob("*.py")):
        relative = path.relative_to(PACKAGE).as_posix()
        for node in ast.walk(ast.parse(path.read_text())):
            if not (isinstance(node, ast.Call) and _callee(node) == FORMAT_ERROR):
                continue
            message = next((kw.value for kw in node.keywords if kw.arg == "message"), node.args[2] if len(node.args) > 2 else None)
            if message is None or (isinstance(message, ast.Constant) and isinstance(message.value, str)):
                continue
            if isinstance(message, ast.JoinedStr):
                parts = [(part.value, part.conversion == ord("r")) for part in message.values if isinstance(part, ast.FormattedValue)]
            else:
                parts = [(message, False)]
            for value, as_repr in parts:
                if isinstance(value, ast.Call) and _callee(value) in SAFE_FORMATTERS:
                    continue
                found.add((relative, ast.unparse(value) + ("!r" if as_repr else "")))
    return found


def test_format_errors_only_interpolate_device_values_through_the_helpers() -> None:
    unexpected = sorted(_format_error_values() - set(EXEMPT_VALUES))
    assert not unexpected, (
        "a device-derived value is interpolated into a ResponseFormatError; pass it through error_text(op, repr(value)) "
        f"(or _kind(value) in a WebSocket codec), or list it in EXEMPT_VALUES with the reason it cannot carry text: {unexpected}"
    )


def test_every_exempt_format_value_is_still_used() -> None:
    stale = sorted(set(EXEMPT_VALUES) - _format_error_values())
    assert not stale, f"remove these from EXEMPT_VALUES: {stale}"
