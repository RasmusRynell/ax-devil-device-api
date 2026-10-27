"""The docs describe ``use_token`` as the runtime behaves: only ``use_token=True`` uses a wssession token."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FILES = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md")), *sorted((ROOT / ".github").rglob("*.md"))]
# "use_token=False ... wssession" in one sentence/parenthesis, without saying the token belongs to True
FALSE_CLAIM = re.compile(r"use_token=False`?[^.;]{0,40}\((?:authenticate|auth)[^)]*wssession", re.I)


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_doc_says_the_default_authenticates_through_wssession(path: Path) -> None:
    assert not FALSE_CLAIM.search(path.read_text(encoding="utf-8")), f"{path.name}: use_token=False does not use wssession.cgi"


def test_the_skill_reference_states_the_default_and_the_token_case() -> None:
    text = (ROOT / ".github/skills/ax-devil-device-api/references/python-api.md").read_text(encoding="utf-8")
    sentence = text[text.index("`use_token=False`") :][:400]
    assert "configured credentials" in sentence and "`True`" in sentence and "wssession.cgi" in sentence


def test_the_runtime_agrees() -> None:
    source = (ROOT / "src/ax_devil_device_api/_runtime/ws.py").read_text(encoding="utf-8")
    assert '"anonymous" if use_token else "required"' in source and "before_send = fetch if use_token else None" in source
