# SPDX-License-Identifier: Apache-2.0
"""Document-level transliteration without mutating OCR output."""

from __future__ import annotations

from dataclasses import dataclass

from rikaocr.core.document.models import Document
from rikaocr.transliteration.base import Transliterator


@dataclass(frozen=True, slots=True)
class LineTransliteration:
    """Transliteration associated with one OCR line."""

    page_id: str
    region_reading_index: int
    line_reading_index: int
    source_text: str
    transliteration: str


@dataclass(frozen=True, slots=True)
class DocumentTransliteration:
    """Separate transliteration view of a recognised document."""

    doc_id: str
    lines: tuple[LineTransliteration, ...]


def transliterate_document(
    document: Document,
    transliterator: Transliterator,
) -> DocumentTransliteration:
    """Transliterate OCR lines while leaving ``document`` unchanged."""
    results: list[LineTransliteration] = []

    for page in document.pages:
        for region in page.iter_in_reading_order():
            for line in region.iter_in_reading_order():
                latin = (
                    transliterator.transliterate(line.text).text
                    if line.text
                    else ""
                )
                results.append(
                    LineTransliteration(
                        page_id=page.page_id,
                        region_reading_index=region.reading_index,
                        line_reading_index=line.reading_index,
                        source_text=line.text,
                        transliteration=latin,
                    )
                )

    return DocumentTransliteration(
        doc_id=document.doc_id,
        lines=tuple(results),
    )


__all__ = [
    "LineTransliteration",
    "DocumentTransliteration",
    "transliterate_document",
]
