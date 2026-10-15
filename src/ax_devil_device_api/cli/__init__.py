"""Command line: ``ax-devil [connection options] <command>``.

``call <api> <op> [key=value ...]`` runs any operation of any generated API;
``apis`` and ``ops`` list what exists (read from the generated modules);
``summary``, ``supported`` and ``snapshot`` (JPEG to a file or stdout) are hand-written commands from ``features``.
Output is JSON on stdout; errors are JSON on stderr with a non-zero exit code. ``supported`` and ``apis --supported`` list probe failures
(``errors`` key / ``warning`` lines on stderr); when discovery cannot run at all (device unreachable, credentials rejected) they exit 1
with the error instead of reporting every API as unknown.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import typing
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any, NoReturn, TextIO

from pydantic import BaseModel, ValidationError

from .. import Device
from .._http.upload import is_upload_field
from .._protocols.base import Operation
from .._protocols.xmlmap import element_text
from .._runtime.capabilities import SupportResult
from .._runtime.driver import StreamResult
from .._streams import Part
from .._validate import bounded_int, non_negative_int, positive_finite
from ..errors import ApiError, ConfigurationError, DeviceError, HttpError, display_text
from ..features import api_support, device_summary, load_all, load_api, snapshot
from ..features.registry import ApiEntry
from ..rtsp import RtspBinding

ENV_HOST = "AX_DEVIL_HOST"
ENV_USER = ("AX_DEVIL_USER", "CAM_USER")
ENV_PASSWORD = ("AX_DEVIL_PASSWORD", "CAM_PASS")


class CliError(Exception):
    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


class _Parser(argparse.ArgumentParser):
    """Reports bad arguments as ``CliError`` so ``main`` can answer in JSON instead of argparse's usage text."""

    def error(self, message: str) -> NoReturn:
        raise CliError(f"{message} (see `{self.prog} --help`)")


def _env(names: Sequence[str], *, keep_empty: bool = False) -> str | None:
    """The first set environment variable; an empty value counts only with ``keep_empty`` (a password may be empty)."""
    for name in names:
        value = os.environ.get(name)
        if value is not None and (value or keep_empty):
            return value
    return None


def _nonempty(option: str) -> Callable[[str], str]:
    """An argparse ``type=`` for a value that has no meaning when empty (an unset shell variable, say): a usage error."""

    def convert(text: str) -> str:
        if not text:
            raise argparse.ArgumentTypeError(f"{option} must not be empty")
        return text

    return convert


def _arg(check: Callable[[Any], Any], kind: type) -> Callable[[str], Any]:
    """An argparse ``type=``: parse as ``kind``, then validate (errors become a usage message)."""

    def convert(text: str) -> Any:
        try:
            return check(kind(text))
        except ConfigurationError as error:
            raise argparse.ArgumentTypeError(str(error)) from None
        except ValueError:
            raise argparse.ArgumentTypeError(f"invalid {kind.__name__} value: {text!r}") from None

    return convert


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="ax-devil", description="Call VAPIX APIs of an Axis device. Output is JSON.")
    conn = parser.add_argument_group(
        "connection", f"host, user and password default to ${ENV_HOST}, ${ENV_USER[0]} (or $CAM_USER) and ${ENV_PASSWORD[0]} (or $CAM_PASS)"
    )
    conn.add_argument("--host", "-H", type=_nonempty("--host"), help="device address (host or IP)")
    conn.add_argument("--user", "-u", type=_nonempty("--user"), help="user name")
    conn.add_argument("--password", "-p", help="password (prefer the environment: arguments show up in process lists)")
    conn.add_argument("--port", type=_arg(lambda v: bounded_int("--port", v, 1, 65535), int))
    conn.add_argument("--http", action="store_true", help="use plain HTTP (default is HTTPS)")
    conn.add_argument("--insecure", "-k", action="store_true", help="do not verify the TLS certificate")
    conn.add_argument("--ca-bundle", metavar="PATH", type=_nonempty("--ca-bundle"), help="CA bundle used to verify the TLS certificate")
    conn.add_argument("--base-path", default="", help="path prefix of a reverse proxy or VMS")
    conn.add_argument("--timeout", type=_arg(lambda v: positive_finite("--timeout", v), float), default=10.0, help="seconds (default 10)")

    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    apis = sub.add_parser("apis", help="list generated APIs (no device needed)")
    apis.add_argument("--supported", action="store_true", help="only APIs the device offers (needs a device)")
    apis.set_defaults(run=_cmd_apis)

    ops = sub.add_parser("ops", help="list the operations of an API and their parameters (no device needed)")
    ops.add_argument("api")
    ops.set_defaults(run=_cmd_ops)

    call = sub.add_parser("call", help="call an operation: call <api> <op> [key=value ...]")
    call.add_argument("api")
    call.add_argument("op")
    call.add_argument("args", nargs="*", metavar="key=value", help="parameters; values are parsed as JSON, else taken as strings. For an upload parameter (see `ops`), key=@PATH sends that file")
    call.add_argument("--json", dest="json_args", metavar="JSON|@FILE", help="parameters as a JSON object, or @file")
    call.add_argument("--output", "-o", metavar="FILE", type=_nonempty("--output"), help="write the result here instead of stdout: binary results and stream bodies, and also JSON results, line streams and RTSP URLs; '-' means stdout")
    call.add_argument("--limit", type=_arg(lambda v: non_negative_int("--limit", v), int), help="stop a stream after this many items")
    call.set_defaults(run=_cmd_call)

    snap = sub.add_parser("snapshot", help="fetch a JPEG image; writes to --output FILE, or raw to stdout")
    snap.add_argument("--output", "-o", metavar="FILE", type=_nonempty("--output"), help="file to write (default: stdout, '-' also means stdout)")
    snap.add_argument("--resolution", type=_nonempty("--resolution"), help="for example 640x480")
    snap.add_argument("--camera", type=_nonempty("--camera"), help="camera number or 'quad'")
    snap.add_argument("--compression", type=int, help="0-100, higher is smaller")
    snap.add_argument("--color", type=int, choices=(0, 1))
    snap.add_argument("--rotation", type=int, choices=(0, 90, 180, 270))
    snap.add_argument("--mirror", type=int, choices=(0, 1))
    snap.set_defaults(run=_cmd_snapshot)

    sub.add_parser("summary", help="identity and discovery summary of the device").set_defaults(run=_cmd_summary)
    sub.add_parser("supported", help="support status of every generated API").set_defaults(run=_cmd_support)
    return parser


# -- helpers ----------------------------------------------------------------


def make_device(args: argparse.Namespace) -> Device:
    host = args.host if args.host is not None else os.environ.get(ENV_HOST)
    if not host:
        raise CliError(f"no device: pass --host or set ${ENV_HOST}")
    # ``is None`` checks: an explicit empty value (an empty password) must not fall back to the environment.
    user = args.user if args.user is not None else _env(ENV_USER)
    password = args.password if args.password is not None else _env(ENV_PASSWORD, keep_empty=True)
    if (user is None) != (password is None):
        raise CliError("give both user and password, or neither")
    verify: bool | str = args.ca_bundle if args.ca_bundle is not None else (not args.insecure)
    return Device(
        host,
        credentials=(user, password) if user is not None and password is not None else None,
        scheme="http" if args.http else "https",
        allow_http=args.http,
        port=args.port,
        base_path=args.base_path,
        verify=verify,
        timeout=args.timeout,
    )


def _entry(name: str) -> ApiEntry:
    try:
        return load_api(name)
    except KeyError:
        raise CliError(f"unknown API {name!r}; see `ax-devil apis`") from None


def parse_value(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return text


def _accepts_text(annotation: Any) -> bool:
    """Whether a parameter's type takes a string (so a leading ``@`` in its value is just text)."""
    if annotation is str or annotation is Any:
        return True
    return any(_accepts_text(arg) for arg in typing.get_args(annotation))


def _field_of(op: Operation | None, key: str) -> Any:
    if op is None or op.params is None:
        return None
    for name, field in op.params.model_fields.items():
        if key in (name, field.alias, field.validation_alias):
            return field
    return None


def _cli_value(op: Operation | None, key: str, text: str) -> Any:
    """The value of ``key=text``. ``key=@path`` names a file for a parameter typed as an upload source; other
    parameters never interpret a leading ``@`` (string values keep it as text; for any other type it is an error)."""
    field = _field_of(op, key)
    if text.startswith("@") and field is not None:
        if is_upload_field(field):
            if len(text) == 1:
                raise CliError(f"{key}=@FILE needs a file name")
            path = Path(text[1:]).expanduser()
            if not path.is_file():
                raise CliError(f"{key}: no such file: {path}")
            return path
        if not _accepts_text(field.annotation):
            raise CliError(f"{key}: '@' is only for file uploads; this parameter takes {field.annotation}")
    return parse_value(text)


def parse_params(args: list[str], json_arg: str | None, op: Operation | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if json_arg is not None:  # an empty --json (an unset shell variable) is invalid JSON, not "absent"
        if json_arg == "@":
            raise CliError("--json @FILE needs a file name")
        raw = Path(json_arg[1:]).read_text() if json_arg.startswith("@") else json_arg
        try:
            loaded = json.loads(raw)
        except ValueError as error:
            raise CliError(f"--json is not valid JSON: {error}") from None
        if not isinstance(loaded, dict):
            raise CliError("--json must be a JSON object")
        params.update(loaded)
    for item in args:
        key, sep, value = item.partition("=")
        if not sep or not key:
            raise CliError(f"expected key=value, got {item!r}")
        params[key] = _cli_value(op, key, value)
    return params


def to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", by_alias=False)
    if isinstance(value, ET.Element):
        return element_text(value)
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [to_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "value"):  # enums
        return to_jsonable(value.value)
    return str(value)


def emit(value: Any, out: TextIO) -> None:
    out.write(json.dumps(to_jsonable(value), indent=2, ensure_ascii=False) + "\n")


def _field_info(op: Operation) -> list[dict[str, Any]]:
    if op.params is None:
        return []
    return [
        {"name": n, "type": str(f.annotation), "required": f.is_required(), "description": f.description, "upload": is_upload_field(f)}
        for n, f in op.params.model_fields.items()
    ]


# -- commands -----------------------------------------------------------------


_UNREACHABLE_ERROR = re.compile(r"\b(ConnectionFailed|ConnectTimeout|TlsError|AuthError): (.*)", re.S)


class DiscoveryFailed(Exception):
    """Discovery could not run at all (device unreachable, credentials rejected): reported like any library error."""

    def __init__(self, error: dict[str, Any]) -> None:
        super().__init__(error["message"])
        self.error = error


def _probe_errors(results: Mapping[str, SupportResult]) -> list[str]:
    """Every distinct probe failure behind the answers, in first-seen order."""
    return list(dict.fromkeys(display_text(e) for r in results.values() for e in r.errors))


def _check_discovery(results: Mapping[str, SupportResult]) -> list[str]:
    """The probe errors; raises ``DiscoveryFailed`` when no API got an answer (nothing could be discovered)."""
    from .. import Support

    errors = _probe_errors(results)
    if errors and results and all(r.status is Support.UNKNOWN for r in results.values()):
        for text in errors:
            found = _UNREACHABLE_ERROR.search(text)
            if found and not text.startswith("not run"):
                kind, message = found.group(1), found.group(2)
                break
        else:
            kind, message = "DiscoveryError", errors[0]
        raise DiscoveryFailed({"type": kind, "message": f"API discovery could not run: {message}", "probes": errors})
    return errors


def _warn(errors: list[str], err: TextIO) -> None:
    for text in errors:
        err.write(json.dumps({"warning": {"type": "ProbeFailed", "message": text}}) + "\n")


def _cmd_apis(args: argparse.Namespace, out: TextIO, err: TextIO) -> None:
    entries = load_all()
    support = None
    if args.supported:
        from .. import Support

        with make_device(args) as dev:  # closed like every other device command: repeated in-process main() must not leak pools
            results = api_support(dev, entries)
        _warn(_check_discovery(results), err)
        support = {n: r for n, r in results.items() if r.status is Support.YES}
    emit(
        [
            {"name": e.name, "id": e.info.id, "title": e.info.name, "family": e.info.family.value, "operations": len(e.operations)}
            for e in entries
            if support is None or e.name in support
        ],
        out,
    )


def _cmd_ops(args: argparse.Namespace, out: TextIO) -> None:
    entry = _entry(args.api)
    emit(
        [
            {"name": n, "access": op.access, "effect": op.effect, "parameters": _field_info(op), "takes_request": op.params is not None}
            for n, op in entry.operations.items()
        ],
        out,
    )


def _stream_is_binary(op: Any) -> bool | None:
    """Whether a stream operation yields bytes (``bytes``/``mjpeg`` decoder), ``False`` for ``lines``, ``None`` if unknown."""
    decoder = getattr(getattr(op.binding, "reply", None), "decoder", None)
    if decoder in ("bytes", "mjpeg"):
        return True
    return False if decoder == "lines" else None


def _stdout_buffer(out: TextIO) -> Any:
    """Binary buffer behind ``out``, refusing a terminal before anything is written.

    Only the process's real stdout may fall back to ``sys.stdout.buffer``. A stream handed in by the caller that has no
    ``buffer`` cannot take bytes: writing to the process-wide stdout instead would put them somewhere unexpected.
    """
    buffer = getattr(out, "buffer", None)
    if buffer is None and out is not sys.stdout:
        raise CliError("binary output requires a binary stream; use --output FILE", code=1)
    # Judge the stream the bytes would reach before writing anything to it.
    target = out if buffer is not None else sys.stdout
    if target.isatty():
        raise CliError("refusing to write binary to a terminal: pass --output FILE")
    return buffer if buffer is not None else sys.stdout.buffer


@contextmanager
def _text_sink(path: str | None, out: TextIO) -> Iterator[TextIO]:
    """Where JSON text goes: ``out`` without ``--output`` or with ``-``, else the file (created or truncated, UTF-8)."""
    if path is None or path == "-":
        yield out
        return
    with open(path, "w", encoding="utf-8") as handle:
        yield handle


def _write_line(sink: TextIO, text: str) -> None:
    sink.write(text + "\n")
    sink.flush()  # a long-running monitor can be followed with tail -f


def _write_binary(chunks: Any, path: str | None, out: TextIO) -> None:
    if path is None:
        raise CliError("binary result: pass --output FILE")
    if path == "-":
        buffer = _stdout_buffer(out)
        for chunk in chunks:
            buffer.write(chunk)
        buffer.flush()
        return
    with open(path, "wb") as handle:
        for chunk in chunks:
            handle.write(chunk)


def _cmd_call(args: argparse.Namespace, out: TextIO) -> None:
    entry = _entry(args.api)
    op = entry.operations.get(args.op)
    if op is None:
        raise CliError(f"unknown operation {args.op!r} of {args.api}; see `ax-devil ops {args.api}`")
    params = parse_params(args.args, args.json_args, op)
    with make_device(args) as dev:
        if isinstance(op.binding, RtspBinding):
            # RTSP operations build a URL (no request); credentials are never put into it.
            with _text_sink(args.output, out) as sink:
                emit({"url": dev.rtsp_url_for(op, params).safe}, sink)
            return
        result = dev.invoke(op, **params)
        if isinstance(result, StreamResult):
            with result:
                items = iter(result)
                if args.limit is not None:
                    items = (item for _, item in zip(range(args.limit), items))
                binary = _stream_is_binary(op)
                first = None
                if binary is None:  # decoder unknown: the first item tells
                    first = next(items, None)
                    binary = isinstance(first, (bytes, Part))
                if binary:
                    # Known from the decoder, so an empty stream still creates or truncates the file.
                    rest = items if first is None else _chain(first, items)
                    chunks = (i.body if isinstance(i, Part) else i for i in rest)
                    _write_binary(chunks, args.output, out)
                else:
                    # The sink is opened before the first item arrives: an empty stream still creates or truncates the file.
                    with _text_sink(args.output, out) as sink:
                        for item in _chain(first, items) if first is not None else items:
                            _write_line(sink, json.dumps(to_jsonable(item), ensure_ascii=False))
            return
    if isinstance(result, (bytes, bytearray)):
        _write_binary([bytes(result)], args.output, out)
        return
    with _text_sink(args.output, out) as sink:
        emit(result, sink)


def _chain(first: Any, rest: Any) -> Any:
    yield first
    yield from rest


def _cmd_snapshot(args: argparse.Namespace, out: TextIO) -> None:
    options = {k: getattr(args, k) for k in ("resolution", "camera", "compression", "color", "rotation", "mirror")}
    with make_device(args) as dev:
        data = snapshot(dev, **options)
    if args.output is not None and args.output != "-":
        Path(args.output).write_bytes(data)
        return
    buffer = _stdout_buffer(out)
    buffer.write(data)
    buffer.flush()


def _cmd_summary(args: argparse.Namespace, out: TextIO) -> None:
    with make_device(args) as dev:
        data = device_summary(dev).to_dict()
        data["probe_errors"] = {key: display_text(text) for key, text in data["probe_errors"].items()}
        emit(data, out)


def _cmd_support(args: argparse.Namespace, out: TextIO, err: TextIO) -> None:
    with make_device(args) as dev:
        results = api_support(dev)
    errors = _check_discovery(results)
    emit({"apis": {n: {"status": r.status.value, "reason": display_text(r.reason)} for n, r in results.items()}, "errors": errors}, out)
    _warn(errors, err)


# -- entry point ----------------------------------------------------------------


def _error_json(error: BaseException) -> dict[str, Any]:
    # Only display forms leave the process: the raw code, api and operation are device or spec text.
    data: dict[str, Any] = {"type": type(error).__name__, "message": display_text(str(error))}
    if isinstance(error, ApiError):
        code = error.code if isinstance(error.code, int) else (None if error.code is None else display_text(error.code, 100))
        data.update(code=code, kind=display_text(error.kind, 100), api=display_text(error.api, 100), operation=display_text(error.operation, 100))
    elif isinstance(error, HttpError):
        data["status"] = getattr(error, "status", None)
    return data


_NEEDS_ERR = (_cmd_apis, _cmd_support)


def main(argv: Sequence[str] | None = None, *, out: TextIO | None = None, err: TextIO | None = None) -> int:
    stdout: TextIO = out or sys.stdout
    stderr: TextIO = err or sys.stderr
    try:
        args = build_parser().parse_args(argv)
        run: Callable[..., None] = args.run
        run(args, stdout, stderr) if args.run in _NEEDS_ERR else run(args, stdout)
    except DiscoveryFailed as error:
        stderr.write(json.dumps({"error": error.error}) + "\n")
        return 1
    except CliError as error:
        stderr.write(json.dumps({"error": {"type": "UsageError", "message": display_text(str(error))}}) + "\n")
        return error.code
    except ValidationError as error:
        stderr.write(json.dumps({"error": {"type": "InvalidParameters", "message": display_text(str(error))}}) + "\n")
        return 2
    except DeviceError as error:
        # Before ValueError: ConfigurationError is both, and is reported with the library's own error shape.
        stderr.write(json.dumps({"error": _error_json(error)}) + "\n")
        return 1
    except (TypeError, ValueError) as error:
        # A value that passed validation but failed a local check (a path parameter of ".", say).
        stderr.write(json.dumps({"error": {"type": "InvalidParameters", "message": display_text(str(error))}}) + "\n")
        return 2
    except OSError as error:
        stderr.write(json.dumps({"error": {"type": type(error).__name__, "message": display_text(str(error))}}) + "\n")
        return 1
    return 0


__all__ = ["build_parser", "main"]
