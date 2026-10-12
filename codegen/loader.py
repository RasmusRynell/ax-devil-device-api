"""Find, load, patch and validate spec files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .patches import PatchError, apply_patch

ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = ROOT / "specs"
APIS_DIR = SPECS_DIR / "apis"
PATCHES_DIR = SPECS_DIR / "patches"
SCHEMA_PATH = SPECS_DIR / "schema.json"


class SpecError(Exception):
    """A spec cannot be loaded, validated or generated. Message is user-facing."""


@dataclass
class LoadedSpec:
    path: Path
    data: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return str(self.data.get("id", self.path.stem))

    @property
    def rel(self) -> str:
        try:
            return self.path.relative_to(ROOT).as_posix()
        except ValueError:
            return self.path.as_posix()


def spec_paths(apis_dir: Path = APIS_DIR) -> list[Path]:
    return sorted(apis_dir.rglob("*.yaml"))


_validator: Draft202012Validator | None = None


def validator() -> Draft202012Validator:
    global _validator
    if _validator is None:
        schema = json.loads(SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        _validator = Draft202012Validator(schema)
    return _validator


def validate(data: Any, *, limit: int = 8) -> list[str]:
    errors = sorted(validator().iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])
    out = []
    for error in errors[:limit]:
        path = "/" + "/".join(str(p) for p in error.absolute_path)
        out.append(f"{path}: {error.message[:300]}")
    if len(errors) > limit:
        out.append(f"... and {len(errors) - limit} more")
    return out


def load_patch_ops(spec_id: str, patches_dir: Path = PATCHES_DIR) -> tuple[list[dict[str, Any]], list[str]]:
    path = patches_dir / f"{spec_id}.yaml"
    if not path.exists():
        return [], []
    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as error:
        raise SpecError(f"{path.name}: invalid YAML: {error}") from error
    warnings: list[str] = []
    if raw is None:
        return [], warnings
    if isinstance(raw, dict):
        if raw.get("variants"):
            warnings.append(f"{path.name}: device variants are not generated yet; ignored")
        raw = raw.get("corrections") or []
    if not isinstance(raw, list):
        raise SpecError(f"{path.name}: expected a list of patch operations")
    return raw, warnings


def load_spec(path: Path, *, patches_dir: Path = PATCHES_DIR, do_validate: bool = True) -> LoadedSpec:
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as error:
        raise SpecError(f"invalid YAML: {str(error).splitlines()[0] if str(error) else error}") from error
    if not isinstance(data, dict):
        raise SpecError("the file is not a YAML mapping")
    spec = LoadedSpec(path, data)
    ops, warnings = load_patch_ops(str(data.get("id", path.stem)), patches_dir)
    spec.warnings.extend(warnings)
    if ops:
        try:
            spec.data = apply_patch(data, ops, source=f"patches/{spec.id}.yaml")
        except PatchError as error:
            raise SpecError(f"patch failed: {error}") from error
    if do_validate:
        problems = validate(spec.data)
        if problems:
            raise SpecError("schema validation failed:\n    " + "\n    ".join(problems))
    return spec
