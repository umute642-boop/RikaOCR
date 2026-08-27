# SPDX-License-Identifier: Apache-2.0
"""Engine-agnostic transliteration interface.

The transliteration layer consumes recognised Ottoman Arabic-script text and
produces a separate Latin-script representation. It does not modify the OCR
Document or overwrite ``Line.text``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class TransliterationResult:
    """Latin-script transliteration produced for one source text."""

    text: str


@runtime_checkable
class Transliterator(Protocol):
    """Transliterate Ottoman Arabic-script text into Latin script."""

    def transliterate(self, text: str) -> TransliterationResult:
        """Return the transliteration of ``text``."""
        ...


__all__ = ["TransliterationResult", "Transliterator"]
