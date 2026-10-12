"""Command line: ``ax-devil [connection options] <command>``.

``call <api> <op> [key=value ...]`` runs any operation of any generated API;
``apis`` and ``ops`` list what exists (read from the generated modules);
``summary``, ``supported`` and ``snapshot`` (JPEG to a file or stdout) are hand-written commands from ``features``.
Output is JSON on stdout; errors are JSON on stderr with a non-zero exit code.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, TextIO

from pydantic import BaseModel, ValidationError

from .. import Device
from .._protocols.base import Operation
from .._runtime.driver import StreamResult
from .._streams import Part
from ..errors import ApiError, DeviceError, HttpError
from ..features import api_support, device_summary, load_all, load_api, snapshot
from ..features.registry import ApiEntry

ENV_HOST = "AX_DEVIL_HOST"
ENV_USER = ("AX_DEVIL_USER", "CAM_USER")
ENV_PASSWORD = ("AX_DEVIL_PASSWORD", "CAM_PASS")


class CliError(Exception):
    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


def _env(names: Sequence[str]) -> str | None:
    for name in names:
        if os.environ.get(name):
            return os.environ[name]
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ax-devil", description="Call VAPIX APIs of an Axis device. Output is JSON.")
    conn = parser.add_argument_group(
        "connection", f"host, user and password default to ${ENV_HOST}, ${ENV_USER[0]} (or $CAM_USER) and ${ENV_PASSWORD[0]} (or $CAM_PASS)"
    )
    conn.add_argument("--host", "-H", help="device address (host or IP)")
    conn.add_argument("--user", "-u", help="user name")
    conn.add_argument("--password", "-p", help="password (prefer the environment: arguments show up in process lists)")
    conn.add_argument("--port", type=int)
    conn.add_argument("--http", action="store_true", help="use plain HTTP (default is HTTPS)")
    conn.add_argument("--insecure", "-k", action="store_true", help="do not verify the TLS certificate")
    conn.add_argument("--ca-bundle", metavar="PATH", help="CA bundle used to verify the TLS certificate")
    conn.add_argument("--base-path", default="", help="path prefix of a reverse proxy or VMS")
    conn.add_argument("--timeout", type=float, default=10.0, help="seconds (default 10)")

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
    call.add_argument("args", nargs="*", metavar="key=value", help="parameters; values are parsed as JSON, else taken as strings")
    call.add_argument("--json", dest="json_args", metavar="JSON|@FILE", help="parameters as a JSON object, or @file")
    call.add_argument("--output", "-o", metavar="FILE", help="write binary results (or stream bodies) here")
    call.add_argument("--limit", type=int, help="stop a stream after this many items")
    call.set_defaults(run=_cmd_call)

    snap = sub.add_parser("snapshot", help="fetch a JPEG image; writes to --output FILE, or raw to stdout")
    snap.add_argument("--output", "-o", metavar="FILE", help="file to write (default: stdout, '-' also means stdout)")
    snap.add_argument("--resolution", help="for example 640x480")
    snap.add_argument("--camera", help="camera number or 'quad'")
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
    host = args.host or os.environ.get(ENV_HOST)
    if not host:
        raise CliError(f"no device: pass --host or set ${ENV_HOST}")
    user, password = args.user or _env(ENV_USER), args.password or _env(ENV_PASSWORD)
    if bool(user) != bool(password):
        raise CliError("give both user and password, or neither")
    verify: bool | str = args.ca_bundle or (not args.insecure)
    return Device(
        host,
        credentials=(user, password) if user and password else None,
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


def parse_params(args: list[str], json_arg: str | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if json_arg:
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
        params[key] = parse_value(value)
    return params


def to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", by_alias=False)
    if isinstance(value, ET.Element):
        return ET.tostring(value, encoding="unicode")
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
        {"name": n, "type": str(f.annotation), "required": f.is_required(), "description": f.description}
        for n, f in op.params.model_fields.items()
    ]


# -- commands -----------------------------------------------------------------


def _cmd_apis(args: argparse.Namespace, out: TextIO) -> None:
    entries = load_all()
    support = None
    if args.supported:
        from .. import Support

        support = {n: r for n, r in api_support(make_device(args), entries).items() if r.status is Support.YES}
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


def _write_binary(chunks: Any, path: str | None) -> None:
    if not path:
        raise CliError("binary result: pass --output FILE")
    with open(path, "wb") as handle:
        for chunk in chunks:
            handle.write(chunk)


def _cmd_call(args: argparse.Namespace, out: TextIO) -> None:
    entry = _entry(args.api)
    op = entry.operations.get(args.op)
    if op is None:
        raise CliError(f"unknown operation {args.op!r} of {args.api}; see `ax-devil ops {args.api}`")
    params = parse_params(args.args, args.json_args)
    with make_device(args) as dev:
        result = dev.invoke(op, **params)
        if isinstance(result, StreamResult):
            with result:
                items = iter(result)
                if args.limit is not None:
                    items = (item for _, item in zip(range(args.limit), items))
                first = next(items, None)
                if isinstance(first, (bytes, Part)):
                    chunks = (i.body if isinstance(i, Part) else i for i in _chain(first, items))
                    _write_binary(chunks, args.output)
                else:
                    for item in _chain(first, items) if first is not None else ():
                        out.write(json.dumps(to_jsonable(item), ensure_ascii=False) + "\n")
            return
    if isinstance(result, (bytes, bytearray)):
        _write_binary([bytes(result)], args.output)
        return
    emit(result, out)


def _chain(first: Any, rest: Any) -> Any:
    yield first
    yield from rest


def _cmd_snapshot(args: argparse.Namespace, out: TextIO) -> None:
    options = {k: getattr(args, k) for k in ("resolution", "camera", "compression", "color", "rotation", "mirror")}
    with make_device(args) as dev:
        data = snapshot(dev, **options)
    if args.output and args.output != "-":
        Path(args.output).write_bytes(data)
        return
    buffer = getattr(out, "buffer", None)
    if buffer is not None:
        buffer.write(data)
        buffer.flush()
    elif sys.stdout.isatty():
        raise CliError("refusing to write binary to a terminal: pass --output FILE")
    else:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()


def _cmd_summary(args: argparse.Namespace, out: TextIO) -> None:
    with make_device(args) as dev:
        emit(device_summary(dev).to_dict(), out)


def _cmd_support(args: argparse.Namespace, out: TextIO) -> None:
    with make_device(args) as dev:
        emit({n: {"status": r.status.value, "reason": r.reason} for n, r in api_support(dev).items()}, out)


# -- entry point ----------------------------------------------------------------


def _error_json(error: BaseException) -> dict[str, Any]:
    data: dict[str, Any] = {"type": type(error).__name__, "message": str(error)}
    if isinstance(error, ApiError):
        data.update(code=error.code, kind=error.kind, api=error.api, operation=error.operation)
    elif isinstance(error, HttpError):
        data["status"] = getattr(error, "status", None)
    return data


def main(argv: Sequence[str] | None = None, *, out: TextIO | None = None, err: TextIO | None = None) -> int:
    stdout: TextIO = out or sys.stdout
    stderr: TextIO = err or sys.stderr
    args = build_parser().parse_args(argv)
    run: Callable[[argparse.Namespace, TextIO], None] = args.run
    try:
        run(args, stdout)
    except CliError as error:
        stderr.write(json.dumps({"error": {"type": "UsageError", "message": str(error)}}) + "\n")
        return error.code
    except ValidationError as error:
        stderr.write(json.dumps({"error": {"type": "InvalidParameters", "message": str(error)}}) + "\n")
        return 2
    except TypeError as error:
        stderr.write(json.dumps({"error": {"type": "InvalidParameters", "message": str(error)}}) + "\n")
        return 2
    except DeviceError as error:
        stderr.write(json.dumps({"error": _error_json(error)}) + "\n")
        return 1
    except OSError as error:
        stderr.write(json.dumps({"error": {"type": type(error).__name__, "message": str(error)}}) + "\n")
        return 1
    return 0


__all__ = ["build_parser", "main"]
