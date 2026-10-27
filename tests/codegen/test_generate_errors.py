"""A spec that fails to load or build must not leave a half-rewritten generated tree."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

import codegen.cli as cli


@pytest.fixture
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    pkg = tmp_path / "apis"
    pkg.mkdir()
    namespace = pkg / "__init__.py"
    namespace.write_text("# sentinel namespace\n")
    surface = tmp_path / "api_surface.txt"
    surface.write_text("sentinel surface\n")
    stale = pkg / "old_module.py"
    stale.write_text(f"{cli.GENERATED_MARK}\nstale = True\n")
    broken = tmp_path / "broken.yaml"
    broken.write_text("id: [this is not: valid\n")
    monkeypatch.setattr(cli, "APIS_PKG", pkg)
    monkeypatch.setattr(cli, "SURFACE_PATH", surface)
    monkeypatch.setattr(cli, "spec_paths", lambda: [broken])
    # With no API built the real renderers have nothing to format; the shared files are still produced from the partial list.
    monkeypatch.setattr(cli, "render_namespace", lambda apis: "# partial namespace\n")
    monkeypatch.setattr(cli, "render_surface", lambda apis: "partial surface\n")
    return {"namespace": namespace, "surface": surface, "stale": stale}


def _args(**kw: object) -> argparse.Namespace:
    return argparse.Namespace(only=None, all=False, **kw)


def test_generate_writes_nothing_and_fails_when_a_spec_is_broken(sandbox: dict[str, Path], capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.cmd_generate(_args()) == 1
    assert sandbox["namespace"].read_text() == "# sentinel namespace\n"
    assert sandbox["surface"].read_text() == "sentinel surface\n"
    assert sandbox["stale"].exists()
    err = capsys.readouterr().err
    assert "broken.yaml" in err and "nothing was written" in err


def test_generate_with_only_is_also_all_or_nothing_on_errors(sandbox: dict[str, Path]) -> None:
    assert cli.cmd_generate(argparse.Namespace(only=["x"], all=False)) == 1
    assert sandbox["namespace"].read_text() == "# sentinel namespace\n"


def test_check_reports_the_build_error_without_misleading_diffs(sandbox: dict[str, Path], capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.cmd_check(_args()) == 1
    err = capsys.readouterr().err
    assert "broken.yaml" in err and "out of date" not in err and "no spec produces" not in err
