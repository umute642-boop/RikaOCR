# SPDX-License-Identifier: Apache-2.0
"""Tests for document-level transliteration."""

from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.models import Document, Line, Page, Region
from rikaocr.transliteration.base import TransliterationResult
from rikaocr.transliteration.document import transliterate_document


class DummyTransliterator:
    def transliterate(self, text: str) -> TransliterationResult:
        return TransliterationResult(text=f"LATIN:{text}")


def test_transliterate_document_preserves_ocr_text() -> None:
    line = Line(text="آباران", reading_index=0)
    document = Document(
        doc_id="doc-1",
        pages=[
            Page(
                page_id="p1",
                regions=[
                    Region(
                        region_type=RegionType.PARAGRAPH,
                        reading_index=0,
                        lines=[line],
                    )
                ],
            )
        ],
    )

    result = transliterate_document(document, DummyTransliterator())

    assert line.text == "آباران"
    assert result.doc_id == "doc-1"
    assert len(result.lines) == 1
    assert result.lines[0].source_text == "آباران"
    assert result.lines[0].transliteration == "LATIN:آباران"
