"""Discovery of the generated API modules (``apis/*.py``) through their public metadata.

Every generated module exposes ``INFO`` (``ApiInfo``), ``OPS`` (a class whose
attributes are ``Operation`` descriptors) and a sync and an async API class.
Modules are imported only when asked for.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from functools import cache
from types import ModuleType

from .. import apis
from .._protocols.base import ApiInfo, Operation
from ..apis._base import AsyncApi, SyncApi


@dataclass(frozen=True)
class ApiEntry:
    """One generated API: its module name (``dev.apis.<name>``), metadata, operations and classes."""

    name: str
    info: ApiInfo
    operations: dict[str, Operation]
    sync_class: type[SyncApi]
    async_class: type[AsyncApi]


def api_names() -> list[str]:
    """Names of all generated API modules, sorted; usable as ``dev.apis.<name>``."""
    return sorted(m.name for m in pkgutil.iter_modules(apis.__path__) if not m.name.startswith("_"))


def _entry(name: str, module: ModuleType) -> ApiEntry:
    info = module.INFO
    ops = {k: v for k, v in vars(module.OPS).items() if isinstance(v, Operation)}
    classes = [c for _, c in inspect.getmembers(module, inspect.isclass) if c.__module__ == module.__name__]
    sync = next(c for c in classes if issubclass(c, SyncApi))
    asyn = next(c for c in classes if issubclass(c, AsyncApi))
    return ApiEntry(name, info, ops, sync, asyn)


@cache
def load_api(name: str) -> ApiEntry:
    """Import and describe one generated API. ``KeyError`` for an unknown name."""
    if name not in api_names():
        raise KeyError(name)
    return _entry(name, importlib.import_module(f"{apis.__name__}.{name}"))


def load_all() -> list[ApiEntry]:
    """Every generated API that can be described (imports all modules)."""
    entries: list[ApiEntry] = []
    for name in api_names():
        try:
            entries.append(load_api(name))
        except (StopIteration, AttributeError):  # module without the standard shape
            continue
    return entries
