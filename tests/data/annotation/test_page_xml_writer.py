# SPDX-License-Identifier: Apache-2.0
"""Tests for the PAGE-XML writer and Document <-> PAGE round-trip."""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from rikaocr.common.exceptions import DataError
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Baseline, BBox, Point, Polygon
from rikaocr.core.document.models import Document, Line, Page, Region, Word
from rikaocr.data.annotation.page_xml import PageXmlCodec, from_page_xml, to_page_xml

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "page"


def _read_fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def _canonical_document() -> Document:
    line = Line(
        text="بسم الله",
        reading_index=0,
        baseline=Baseline((Point(10, 70), Point(990, 70))),
        polygon=Polygon((Point(10, 10), Point(990, 10), Point(990, 80), Point(10, 80))),
        words=[
            Word(text="بسم", bbox=BBox(900, 10, 990, 80)),
            Word(text="الله", bbox=BBox(800, 10, 895, 80)),
        ],
        confidence=0.88,
    )
    region = Region(
        region_type=RegionType.PARAGRAPH,
        reading_index=0,
        polygon=Polygon((Point(10, 10), Point(990, 10), Point(990, 300), Point(10, 300))),
        lines=[line],
    )
    page = Page(
        page_id="rika001.png", image_ref="rika001.png", width=1000, height=600, regions=[region]
    )
    return Document(doc_id="rika001", pages=[page])


def test_to_page_xml_is_well_formed() -> None:
    xml = to_page_xml(_canonical_document())
    root = ET.fromstring(xml)
    assert root.tag.endswith("PcGts")
    assert "TextRegion" in xml
    assert "بسم الله" in xml


@pytest.mark.parametrize("fixture", ["sample_min.xml", "sample_rika.xml"])
def test_fixture_round_trip(fixture: str) -> None:
    document = from_page_xml(_read_fixture(fixture))
    assert from_page_xml(to_page_xml(document)) == document


def test_canonical_document_round_trip() -> None:
    document = _canonical_document()
    assert from_page_xml(to_page_xml(document)) == document


def test_confidence_round_trip() -> None:
    document = _canonical_document()
    restored = from_page_xml(to_page_xml(document))
    assert restored.pages[0].regions[0].lines[0].confidence == 0.88


def test_reading_order_round_trip() -> None:
    page = Page(
        page_id="multi.png",
        image_ref="multi.png",
        regions=[
            Region(region_type=RegionType.HEADER, reading_index=0),
            Region(region_type=RegionType.PARAGRAPH, reading_index=1),
        ],
    )
    document = Document(doc_id="multi", pages=[page])
    restored = from_page_xml(to_page_xml(document))
    types = [region.region_type for region in restored.pages[0].regions]
    assert types == [RegionType.HEADER, RegionType.PARAGRAPH]
    assert [r.reading_index for r in restored.pages[0].regions] == [0, 1]


def test_doc_id_round_trip_via_pcgtsid() -> None:
    page = Page(page_id="page-1", regions=[])
    document = Document(doc_id="custom-doc-id", pages=[page])
    restored = from_page_xml(to_page_xml(document))
    assert restored.doc_id == "custom-doc-id"


def test_to_page_xml_requires_single_page() -> None:
    with pytest.raises(DataError):
        to_page_xml(Document(doc_id="empty"))


def test_codec_save_and_load_round_trip(tmp_path: Path) -> None:
    document = from_page_xml(_read_fixture("sample_min.xml"))
    target = tmp_path / "out.xml"
    codec = PageXmlCodec()
    codec.save(document, target)
    assert codec.load(target) == document


def test_tokens_are_not_persisted_yet() -> None:
    page = Page(
        page_id="t.png",
        image_ref="t.png",
        regions=[
            Region(
                region_type=RegionType.PARAGRAPH,
                lines=[Line(text="x", words=[Word(text="x")])],
            )
        ],
    )
    document = Document(doc_id="t", pages=[page])
    restored = from_page_xml(to_page_xml(document))
    assert restored.pages[0].regions[0].lines[0].words[0].tokens == []
