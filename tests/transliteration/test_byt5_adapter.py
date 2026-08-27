# SPDX-License-Identifier: Apache-2.0
"""Tests for ByT5 inference modes without loading ML dependencies."""

from rikaocr.transliteration.byt5_adapter import ByT5Transliterator


def test_word_mode_transliterates_units_separately_and_preserves_whitespace() -> None:
    transliterator = object.__new__(ByT5Transliterator)
    transliterator._mode = "word"
    transliterator._transliterate_sequence = lambda text: f"[{text}]"

    result = transliterator.transliterate("حضور  حضرت")

    assert result.text == "[حضور]  [حضرت]"
