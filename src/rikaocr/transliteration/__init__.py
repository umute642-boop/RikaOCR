# SPDX-License-Identifier: Apache-2.0
"""Transliteration interfaces, adapters, and document helpers."""

from rikaocr.transliteration.base import TransliterationResult, Transliterator
from rikaocr.transliteration.document import (
    DocumentTransliteration,
    LineTransliteration,
    transliterate_document,
)

__all__ = [
    "TransliterationResult",
    "Transliterator",
    "LineTransliteration",
    "DocumentTransliteration",
    "transliterate_document",
]
