# SPDX-License-Identifier: Apache-2.0
"""Tests for text-to-geometry alignment invariants."""

import pytest

from rikaocr.common.exceptions import AlignmentError
from rikaocr.core.document.alignment import validate_alignment
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Baseline, BBox, Point, Polygon
from rikaocr.core.document.models import Document, Line, Page, Region, Token, Word


def _wrap(line: Line, *, region_polygon: Polygon | None = None) -> Document:
    region = Region(region_type=RegionType.PARAGRAPH, polygon=region_polygon, lines=[line])
    return Document(doc_id="d", pages=[Page(page_id="p", regions=[region])])


def _aligned_document() -> Document:
    word = Word(
        text="اب",
        bbox=BBox(0, 0, 30, 18),
        tokens=[
            Token(text="ا", index=0, bbox=BBox(0, 0, 10, 18)),
            Token(text="ب", index=1, bbox=BBox(10, 0, 20, 18)),
        ],
    )
    line = Line(
        text="اب",
        baseline=Baseline((Point(0, 15), Point(80, 15))),
        polygon=Polygon((Point(0, 0), Point(80, 0), Point(80, 20), Point(0, 20))),
        words=[word],
    )
    return _wrap(
        line,
        region_polygon=Polygon((Point(0, 0), Point(100, 0), Point(100, 50), Point(0, 50))),
    )


def test_aligned_document_passes() -> None:
    validate_alignment(_aligned_document())


def test_geometry_is_optional() -> None:
    line = Line(
        text="اب",
        words=[Word(text="اب", tokens=[Token("ا", 0), Token("ب", 1)])],
    )
    validate_alignment(_wrap(line))


def test_word_token_text_mismatch_raises() -> None:
    line = Line(text="اب", words=[Word(text="اب", tokens=[Token("ا", 0)])])
    with pytest.raises(AlignmentError):
        validate_alignment(_wrap(line))


def test_line_words_text_mismatch_raises() -> None:
    line = Line(text="WRONG", words=[Word(text="اب", tokens=[Token("ا", 0), Token("ب", 1)])])
    with pytest.raises(AlignmentError):
        validate_alignment(_wrap(line))


def test_token_box_not_contained_raises() -> None:
    word = Word(
        text="اب",
        bbox=BBox(0, 0, 30, 18),
        tokens=[
            Token(text="ا", index=0, bbox=BBox(0, 0, 10, 18)),
            Token(text="ب", index=1, bbox=BBox(40, 0, 60, 18)),
        ],
    )
    with pytest.raises(AlignmentError):
        validate_alignment(_wrap(Line(text="اب", words=[word])))


def test_word_box_not_contained_in_line_raises() -> None:
    line = Line(
        text="اب",
        polygon=Polygon((Point(0, 0), Point(80, 0), Point(80, 20), Point(0, 20))),
        words=[Word(text="اب", bbox=BBox(0, 0, 200, 18))],
    )
    with pytest.raises(AlignmentError):
        validate_alignment(_wrap(line))


def test_line_polygon_not_contained_in_region_raises() -> None:
    line = Line(
        text="اب",
        polygon=Polygon((Point(0, 0), Point(80, 0), Point(80, 20), Point(0, 20))),
        words=[Word(text="اب")],
    )
    region_polygon = Polygon((Point(0, 0), Point(50, 0), Point(50, 50), Point(0, 50)))
    with pytest.raises(AlignmentError):
        validate_alignment(_wrap(line, region_polygon=region_polygon))


def test_custom_word_separator() -> None:
    line = Line(text="ا-ب", words=[Word(text="ا"), Word(text="ب")])
    validate_alignment(_wrap(line), word_separator="-")
    with pytest.raises(AlignmentError):
        validate_alignment(_wrap(line))
