# SPDX-License-Identifier: Apache-2.0
"""Tests for recognize_document (cropping + recognition into Line.text)."""

from PIL import Image
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Point, Polygon
from rikaocr.core.document.models import Document, Line, Page, Region
from rikaocr.recognition.base import recognize_document
from rikaocr.recognition.dummy import DummyRecognizer


def _rect(x0: int, y0: int, x1: int, y1: int) -> Polygon:
    return Polygon((Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1)))


def test_fills_text_for_croppable_lines_only() -> None:
    page = Image.new("RGB", (100, 40), (255, 255, 255))
    croppable = Line(text="orig", reading_index=0, polygon=_rect(0, 0, 50, 20))
    no_geometry = Line(text="keep", reading_index=1)
    document = Document(
        doc_id="d",
        pages=[
            Page(
                page_id="p", regions=[Region(RegionType.PARAGRAPH, lines=[croppable, no_geometry])]
            )
        ],
    )

    result = recognize_document(document, page, DummyRecognizer(text="X", confidence=0.9))

    assert result is document  # mutated in place and returned
    assert croppable.text == "X"
    assert croppable.confidence == 0.9
    assert no_geometry.text == "keep"  # left untouched (not croppable)
    assert no_geometry.confidence is None
