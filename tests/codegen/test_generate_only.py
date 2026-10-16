"""``generate --all --only <id>`` must leave a tree that ``codegen check`` accepts."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pytest

import codegen.cli as cli
import codegen.output as output

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A copy of the generated tree that the generator writes to instead of the repository."""
    apis = tmp_path / "src" / "ax_devil_device_api" / "apis"
    shutil.copytree(REPO / "src" / "ax_devil_device_api" / "apis", apis, ignore=shutil.ignore_patterns("__pycache__"))
    surface = tmp_path / "docs" / "api_surface.txt"
    surface.parent.mkdir(parents=True)
    shutil.copy(REPO / "docs" / "api_surface.txt", surface)
    for module in (cli, output):
        monkeypatch.setattr(module, "APIS_PKG", apis)
        monkeypatch.setattr(module, "SURFACE_PATH", surface)
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    return tmp_path


def test_generate_all_only_a_curated_id_keeps_the_tree_consistent(tree: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.cmd_generate(argparse.Namespace(only=["disk-management"], all=True)) == 0
    namespace = (tree / "src" / "ax_devil_device_api" / "apis" / "__init__.py").read_text()
    # image-stabilization is uncurated: --all builds it, but its module is not written, so it must not be listed
    assert "image_stabilization" not in namespace
    assert "image_stabilization" not in (tree / "docs" / "api_surface.txt").read_text()
    assert cli.cmd_check(argparse.Namespace(all=False)) == 0, capsys.readouterr().err


def test_modules_that_exist_stay_in_the_aggregates(tree: Path) -> None:
    assert cli.cmd_generate(argparse.Namespace(only=["disk-management"], all=False)) == 0
    namespace = (tree / "src" / "ax_devil_device_api" / "apis" / "__init__.py").read_text()
    assert "disk_management" in namespace and "mqtt_client" in namespace


def _snapshot(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): p.read_text() for p in sorted(root.rglob("*")) if p.is_file()}


def test_a_selector_that_matches_nothing_fails_and_writes_nothing(tree: Path, capsys: pytest.CaptureFixture[str]) -> None:
    before = _snapshot(tree)
    assert cli.cmd_generate(argparse.Namespace(only=["disk-managment"], all=False)) == 1  # typo
    err = capsys.readouterr().err
    assert "disk-managment" in err and "no spec has this id" in err and "nothing was written" in err
    assert _snapshot(tree) == before


def test_every_unmatched_selector_is_listed_even_next_to_a_good_one(tree: Path, capsys: pytest.CaptureFixture[str]) -> None:
    before = _snapshot(tree)
    assert cli.cmd_generate(argparse.Namespace(only=["disk-management", "typo-one", "typo-two"], all=False)) == 1
    err = capsys.readouterr().err
    assert "typo-one" in err and "typo-two" in err and "disk-management:" not in err
    assert _snapshot(tree) == before


def test_an_uncurated_selector_without_all_is_reported_with_a_hint(tree: Path, capsys: pytest.CaptureFixture[str]) -> None:
    before = _snapshot(tree)
    assert cli.cmd_generate(argparse.Namespace(only=["image-stabilization"], all=False)) == 1
    assert "use --all" in capsys.readouterr().err
    assert _snapshot(tree) == before


def test_a_matching_selector_still_generates(tree: Path) -> None:
    assert cli.cmd_generate(argparse.Namespace(only=["disk-management"], all=False)) == 0
