# SPDX-License-Identifier: Apache-2.0
"""Tests for the engine-agnostic transliteration interface."""

from rikaocr.transliteration.base import TransliterationResult, Transliterator


class DummyTransliterator:
    def transliterate(self, text: str) -> TransliterationResult:
        return TransliterationResult(text=f"latin:{text}")


def test_transliteration_result_holds_text() -> None:
    result = TransliterationResult(text="Abaran")
    assert result.text == "Abaran"


def test_runtime_protocol_accepts_compatible_implementation() -> None:
    transliterator = DummyTransliterator()
    assert isinstance(transliterator, Transliterator)
    assert transliterator.transliterate("آباران").text == "latin:آباران"
