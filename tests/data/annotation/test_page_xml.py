# SPDX-License-Identifier: Apache-2.0
"""Tests for the PAGE-XML reader (from_page_xml)."""

from pathlib import Path

import pytest
from rikaocr.common.exceptions import DataError
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import BBox
from rikaocr.data.annotation.page_xml import from_page_xml

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "page"
_PAGE_NS = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"


def _read_fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def test_read_min_fixture() -> None:
    document = from_page_xml(_read_fixture("sample_min.xml"))
    assert document.doc_id == "min"
    assert len(document.pages) == 1
    page = document.pages[0]
    assert page.image_ref == "min.png"
    assert page.width == 200
    assert page.height == 100

    region = page.regions[0]
    assert region.region_type == RegionType.PARAGRAPH
    assert region.polygon is not None

    line = region.lines[0]
    assert line.text == "hello"
    assert line.confidence == 0.9
    assert line.baseline is not None

    word = line.words[0]
    assert word.text == "hello"
    assert word.bbox == BBox(0, 0, 80, 50)


def test_read_rika_fixture_preserves_unicode() -> None:
    document = from_page_xml(_read_fixture("sample_rika.xml"))
    page = document.pages[0]
    assert page.image_ref == "rika001.png"
    assert len(page.regions) == 2

    first_line = page.regions[0].lines[0]
    assert first_line.text == "بسم الله"
    assert [word.text for word in first_line.words] == ["بسم", "الله"]
    assert first_line.confidence == 0.88


def test_read_rika_fixture_marginalia_without_geometry() -> None:
    document = from_page_xml(_read_fixture("sample_rika.xml"))
    marginalia = document.pages[0].regions[1]
    assert marginalia.region_type == RegionType.MARGINALIA
    line = marginalia.lines[0]
    assert line.text == "لاچين"
    assert line.baseline is None
    assert line.words == []


def test_reading_index_assigned_in_document_order() -> None:
    document = from_page_xml(_read_fixture("sample_rika.xml"))
    assert [region.reading_index for region in document.pages[0].regions] == [0, 1]


def test_word_polygon_simplified_to_bbox() -> None:
    document = from_page_xml(_read_fixture("sample_rika.xml"))
    word = document.pages[0].regions[0].lines[0].words[0]
    assert word.bbox == BBox(900, 10, 990, 80)


def test_parsed_document_is_valid() -> None:
    from_page_xml(_read_fixture("sample_rika.xml")).validate()


def test_malformed_xml_raises() -> None:
    with pytest.raises(DataError):
        from_page_xml("<PcGts><Page>")


def test_doctype_is_rejected() -> None:
    payload = '<?xml version="1.0"?><!DOCTYPE pcgts><PcGts></PcGts>'
    with pytest.raises(DataError):
        from_page_xml(payload)


def test_missing_page_element_raises() -> None:
    payload = f'<?xml version="1.0"?><PcGts xmlns="{_PAGE_NS}"></PcGts>'
    with pytest.raises(DataError):
        from_page_xml(payload)
