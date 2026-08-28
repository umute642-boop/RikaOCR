# SPDX-License-Identifier: Apache-2.0
"""Tests for the document entity model and its validation."""

import pytest
from rikaocr.common.exceptions import ValidationError
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Baseline, Point, Polygon
from rikaocr.core.document.models import (
    SCHEMA_VERSION,
    Document,
    Line,
    Page,
    Region,
    Token,
    Word,
)


def _build_valid_document() -> Document:
    polygon = Polygon((Point(0, 0), Point(50, 0), Point(50, 12), Point(0, 12)))
    line = Line(
        text="بسم",
        baseline=Baseline((Point(0, 10), Point(50, 10))),
        polygon=polygon,
        words=[Word(text="بسم", tokens=[Token(text="ب", index=0)])],
        confidence=0.9,
    )
    region = Region(region_type=RegionType.PARAGRAPH, polygon=polygon, lines=[line])
    page = Page(page_id="p1", width=100, height=200, regions=[region])
    return Document(doc_id="doc-1", pages=[page])


def test_valid_document_passes_validation() -> None:
    _build_valid_document().validate()


def test_document_default_schema_version() -> None:
    assert Document(doc_id="doc-1").schema_version == SCHEMA_VERSION


def test_empty_doc_id_raises() -> None:
    with pytest.raises(ValidationError):
        Document(doc_id="").validate()


def test_empty_page_id_raises() -> None:
    with pytest.raises(ValidationError):
        Page(page_id="").validate()


def test_negative_reading_index_raises() -> None:
    with pytest.raises(ValidationError):
        Region(region_type=RegionType.PARAGRAPH, reading_index=-1).validate()


def test_confidence_out_of_range_raises() -> None:
    with pytest.raises(ValidationError):
        Line(text="x", confidence=1.5).validate()


def test_empty_token_text_raises() -> None:
    with pytest.raises(ValidationError):
        Token(text="", index=0).validate()


def test_nested_invalid_token_propagates() -> None:
    document = Document(
        doc_id="doc-1",
        pages=[
            Page(
                page_id="p1",
                regions=[
                    Region(
                        region_type=RegionType.PARAGRAPH,
                        lines=[Line(text="x", words=[Word(text="x", tokens=[Token("", 0)])])],
                    )
                ],
            )
        ],
    )
    with pytest.raises(ValidationError):
        document.validate()


def test_region_iter_in_reading_order() -> None:
    region = Region(
        region_type=RegionType.PARAGRAPH,
        lines=[Line(text="b", reading_index=1), Line(text="a", reading_index=0)],
    )
    ordered = [line.text for line in region.iter_in_reading_order()]
    assert ordered == ["a", "b"]


def test_page_iter_in_reading_order() -> None:
    page = Page(
        page_id="p1",
        regions=[
            Region(region_type=RegionType.HEADER, reading_index=2),
            Region(region_type=RegionType.PARAGRAPH, reading_index=0),
        ],
    )
    ordered = [region.reading_index for region in page.iter_in_reading_order()]
    assert ordered == [0, 2]


def test_entities_are_mutable() -> None:
    line = Line(text="")
    line.text = "بسم"
    assert line.text == "بسم"
