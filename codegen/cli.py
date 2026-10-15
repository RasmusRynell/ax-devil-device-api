"""``python -m codegen generate | check | validate``."""

from __future__ import annotations

import argparse
import difflib
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .build import SUPPORTED_FAMILIES, build_api
from .loader import ROOT, LoadedSpec, SpecError, load_spec, spec_paths
from .model import ApiDef
from .output import APIS_PKG, SURFACE_PATH, format_python, module_path, render_namespace, render_surface
from .render import render_module

GENERATED_MARK = "# GENERATED"


@dataclass
class Result:
    files: dict[Path, str] = field(default_factory=dict)
    apis: list[ApiDef] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)
    skipped: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    all_ids: set[str] = field(default_factory=set)
    uncurated: list[str] = field(default_factory=list)
    unmatched: dict[str, str] = field(default_factory=dict)
    """``--only`` selectors that produced no module, with the reason."""


def build_all(paths: list[Path], only: list[str] | None = None, include_uncurated: bool = False) -> Result:
    """Load, build and render every spec. One bad spec never stops the others.

    Specs whose ``provenance.curated`` is not true (migrated, not yet reviewed) are only
    generated with ``include_uncurated``; they are still loaded and validated.
    """
    res = Result()
    loaded: list[LoadedSpec] = []
    for path in paths:
        label = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        try:
            spec = load_spec(path)
        except SpecError as error:
            res.errors[label] = str(error)
            continue
        except Exception as error:  # noqa: BLE001 - report, continue
            res.errors[label] = f"{type(error).__name__}: {error}"
            continue
        res.all_ids.add(spec.id)
        loaded.append(spec)

    seen_modules: dict[str, str] = {}
    matched: set[str] = set()
    for spec in loaded:
        family = spec.data["family"]
        if not include_uncurated and not (spec.data.get("provenance") or {}).get("curated"):
            res.uncurated.append(spec.id)
            continue
        if family not in SUPPORTED_FAMILIES:
            res.skipped.setdefault(family, []).append(spec.id)
            continue
        try:
            api = build_api(spec)
            if api.module in seen_modules:
                raise SpecError(f"python.module {api.module!r} is already used by {seen_modules[api.module]}")
            source = render_module(api)
            text = format_python(source, f"src/ax_devil_device_api/apis/{api.module}.py")
        except SpecError as error:
            res.errors[spec.rel] = str(error)
            continue
        except Exception as error:  # noqa: BLE001
            res.errors[spec.rel] = f"{type(error).__name__}: {error}"
            continue
        seen_modules[api.module] = spec.rel
        res.warnings += [f"{spec.rel}: {w}" for w in spec.warnings]
        res.apis.append(api)
        if only is None or api.id in only or spec.path.stem in only:
            res.files[module_path(api)] = text
            matched.update({api.id, spec.path.stem})
    res.apis.sort(key=lambda a: a.module)
    known = res.all_ids | {spec.path.stem for spec in loaded}
    for selector in only or ():
        if selector not in matched:
            res.unmatched[selector] = (
                "this spec is not generated (uncurated or an unsupported family; use --all for uncurated specs)"
                if selector in known
                else "no spec has this id or file name"
            )
    # The shared outputs list only modules that exist after this run: written now, or generated earlier and still on
    # disk. With --only, an API whose module is not written (an uncurated one included by --all, say) must not appear
    # in the namespace, or importing it would fail.
    present = [a for a in res.apis if module_path(a) in res.files or _generated_on_disk(module_path(a))]
    res.files[APIS_PKG / "__init__.py"] = render_namespace(present)
    res.files[SURFACE_PATH] = render_surface(present)
    return res


def _generated_on_disk(path: Path) -> bool:
    return path.is_file() and path.read_text().startswith(GENERATED_MARK)


def report(res: Result) -> None:
    if res.uncurated:
        print(f"note: {len(res.uncurated)} uncurated spec(s) not generated (use --all to include them): {', '.join(sorted(res.uncurated))}", file=sys.stderr)
    for fam, ids in sorted(res.skipped.items()):
        print(f"warning: family {fam!r} is not implemented yet; skipped {len(ids)} spec(s): {', '.join(sorted(ids))}", file=sys.stderr)
    for w in dict.fromkeys(res.warnings):
        print(f"warning: {w}", file=sys.stderr)
    for where, message in sorted(res.errors.items()):
        print(f"error: {where}: {message}", file=sys.stderr)


def _select(args: argparse.Namespace) -> list[Path]:
    return spec_paths()


def stale_files(res: Result) -> list[Path]:
    """Generated modules on disk that no spec produces any more."""
    wanted = set(res.files)
    out = []
    for path in sorted(APIS_PKG.glob("*.py")):
        if path in wanted or path.name.startswith("_"):
            continue
        if path.read_text().startswith(GENERATED_MARK):
            out.append(path)
    return out


def cmd_generate(args: argparse.Namespace) -> int:
    res = build_all(_select(args), args.only or None, args.all)
    report(res)
    if res.errors:
        # The shared files (apis/__init__.py, docs/api_surface.txt) would list only the specs that built, and a
        # partial rewrite would leave the tree inconsistent: write nothing and fail.
        print("error: some specs failed to load or build; nothing was written", file=sys.stderr)
        return 1
    if res.unmatched:
        for selector, reason in sorted(res.unmatched.items()):
            print(f"error: --only {selector}: {reason}", file=sys.stderr)
        print("error: nothing was written", file=sys.stderr)
        return 1
    for path, text in sorted(res.files.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text() != text:
            path.write_text(text)
            print(f"wrote {path.relative_to(ROOT)}")
    if not args.only:
        for path in stale_files(res):
            path.unlink()
            print(f"removed {path.relative_to(ROOT)} (no spec produces it)")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    res = build_all(spec_paths(), include_uncurated=args.all)
    report(res)
    if res.errors:
        # The generated set is incomplete, so comparing it with the tree would only add misleading diffs.
        return 1
    bad = False
    for path, text in sorted(res.files.items()):
        current = path.read_text() if path.exists() else ""
        if current != text:
            bad = True
            rel = path.relative_to(ROOT).as_posix()
            diff = difflib.unified_diff(current.splitlines(), text.splitlines(), f"a/{rel}", f"b/{rel}", lineterm="", n=2)
            print("\n".join(list(diff)[:60]), file=sys.stderr)
            print(f"error: {rel} is out of date; run `uv run python -m codegen generate`", file=sys.stderr)
    for path in stale_files(res):
        bad = True
        print(f"error: {path.relative_to(ROOT)} is generated but no spec produces it", file=sys.stderr)
    if not bad:
        print(f"ok: {len(res.apis)} API module(s) up to date")
    return 1 if bad else 0


def cmd_validate(args: argparse.Namespace) -> int:
    failed = 0
    paths = spec_paths()
    for path in paths:
        try:
            load_spec(path)
        except Exception as error:  # noqa: BLE001 - one broken file must not stop the others
            failed += 1
            message = str(error) if isinstance(error, SpecError) else f"{type(error).__name__}: {error}"
            label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
            print(f"error: {label}: {message}", file=sys.stderr)
    print(f"{len(paths) - failed}/{len(paths)} spec(s) valid")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codegen", description="Generate API modules from specs/apis/**.yaml")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="write generated modules, apis/__init__.py and docs/api_surface.txt")
    gen.add_argument("--only", nargs="+", metavar="ID", help="only write modules for these spec ids")
    gen.add_argument("--all", action="store_true", help="include specs that are not curated yet")
    gen.set_defaults(func=cmd_generate)
    chk = sub.add_parser("check", help="fail if committed generated files differ from a fresh generation")
    chk.add_argument("--all", action="store_true", help="include specs that are not curated yet")
    chk.set_defaults(func=cmd_check)
    val = sub.add_parser("validate", help="validate specs against specs/schema.json (after patches)")
    val.set_defaults(func=cmd_validate)
    args = parser.parse_args(argv)
    return args.func(args)
