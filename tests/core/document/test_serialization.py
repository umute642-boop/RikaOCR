# SPDX-License-Identifier: Apache-2.0
"""Tests for lossless (de)serialisation of the document model."""

import pytest

from rikaocr.common.exceptions import SerializationError
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Baseline, BBox, Point, Polygon
from rikaocr.core.document.models import Document, Line, Page, Region, Token, Word
from rikaocr.core.document.serialization import from_dict, from_json, to_dict, to_json


def _coherent_document() -> Document:
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
        reading_index=0,
        baseline=Baseline((Point(0, 15), Point(80, 15))),
        polygon=Polygon((Point(0, 0), Point(80, 0), Point(80, 20), Point(0, 20))),
        words=[word],
        confidence=0.95,
    )
    region = Region(
        region_type=RegionType.PARAGRAPH,
        reading_index=0,
        polygon=Polygon((Point(0, 0), Point(100, 0), Point(100, 50), Point(0, 50))),
        lines=[line],
    )
    page = Page(page_id="p1", image_ref="img/p1.png", width=100, height=50, regions=[region])
    return Document(
        doc_id="doc-1",
        pages=[page],
        metadata={"source": "BOA", "tags": ["rika", "test"], "ok": True, "note": None},
    )


def test_dict_round_trip_is_lossless() -> None:
    document = _coherent_document()
    assert from_dict(to_dict(document)) == document


def test_json_round_trip_is_lossless() -> None:
    document = _coherent_document()
    assert from_json(to_json(document)) == document


def test_empty_document_round_trip() -> None:
    document = Document(doc_id="empty")
    assert from_dict(to_dict(document)) == document


def test_to_json_returns_str_with_unicode() -> None:
    text = to_json(_coherent_document())
    assert isinstance(text, str)
    assert "اب" in text


def test_to_dict_top_level_keys() -> None:
    data = to_dict(_coherent_document())
    assert set(data) == {"schema_version", "doc_id", "metadata", "pages"}


def test_unsupported_schema_version_raises() -> None:
    data = to_dict(_coherent_document())
    data["schema_version"] = "9.9"
    with pytest.raises(SerializationError):
        from_dict(data)


def test_missing_schema_version_raises() -> None:
    data = to_dict(_coherent_document())
    del data["schema_version"]
    with pytest.raises(SerializationError):
        from_dict(data)


def test_malformed_document_raises() -> None:
    data = to_dict(_coherent_document())
    del data["doc_id"]
    with pytest.raises(SerializationError):
        from_dict(data)


def test_invalid_json_raises() -> None:
    with pytest.raises(SerializationError):
        from_json("{not valid json")


def test_non_object_json_raises() -> None:
    with pytest.raises(SerializationError):
        from_json("[1, 2, 3]")
