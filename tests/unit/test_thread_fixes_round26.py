"""Count-like stream limits must be real positive integers."""

from __future__ import annotations

from typing import Any

import pytest

from ax_devil_device_api._streams import LinesDecoder, MixedReplaceDecoder, MultipartLinesDecoder, decoder_for
from ax_devil_device_api.errors import ConfigurationError

BAD = [1.5, True, 0, -1, "2", None]


@pytest.mark.parametrize("bad", BAD)
def test_mixed_replace_decoder_rejects_bad_max_part_bytes(bad: Any) -> None:
    with pytest.raises(ConfigurationError, match="max_part_bytes"):
        MixedReplaceDecoder("b", max_part_bytes=bad)


@pytest.mark.parametrize("bad", BAD)
def test_lines_decoders_reject_bad_max_line_bytes(bad: Any) -> None:
    with pytest.raises(ConfigurationError, match="max_line_bytes"):
        LinesDecoder(max_line_bytes=bad)
    with pytest.raises(ConfigurationError, match="max_line_bytes"):
        MultipartLinesDecoder(MixedReplaceDecoder("b"), max_line_bytes=bad)


def test_good_limits_still_work() -> None:
    assert LinesDecoder(max_line_bytes=1).feed(b"a\nb\n") == ["a", "b"]
    assert MixedReplaceDecoder("b", max_part_bytes=1)
    assert decoder_for is not None
