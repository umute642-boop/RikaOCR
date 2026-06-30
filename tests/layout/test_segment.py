# SPDX-License-Identifier: Apache-2.0
"""Tests for segment_document and RTL reading-order assignment."""

from PIL import Image

from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Point, Polygon
from rikaocr.core.document.models import Line, Region
from rikaocr.layout.base import SegmentationResult, segment_document
from rikaocr.layout.dummy import DummySegmenter


def _rect(x0: int, y0: int, x1: int, y1: int) -> Polygon:
    return Polygon((Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1)))


def _image(width: int = 90, height: int = 30) -> Image.Image:
    return Image.new("RGB", (width, height), (255, 255, 255))


def test_builds_single_page_document_with_size() -> None:
    document = segment_document(
        _image(90, 30), DummySegmenter(num_lines=3), doc_id="d", page_id="p"
    )
    assert document.doc_id == "d"
    assert len(document.pages) == 1
    page = document.pages[0]
    assert page.page_id == "p"
    assert (page.width, page.height) == (90, 30)
    assert len(page.regions[0].lines) == 3
    document.validate()  # produced document must satisfy domain invariants


def test_lines_get_top_to_bottom_reading_index() -> None:
    document = segment_document(_image(90, 30), DummySegmenter(num_lines=3), doc_id="d", page_id="p")
    lines = document.pages[0].regions[0].lines
    assert [line.reading_index for line in lines] == [0, 1, 2]


def test_regions_ordered_right_to_left() -> None:
    # Two regions on the same row; the right-hand one must read first (RTL).
    left = Region(region_type=RegionType.PARAGRAPH, polygon=_rect(0, 0, 40, 30))
    right = Region(region_type=RegionType.PARAGRAPH, polygon=_rect(50, 0, 90, 30))

    class _TwoRegionSegmenter:
        def segment(self, image: Image.Image) -> SegmentationResult:
            return SegmentationResult(regions=[left, right])

    document = segment_document(_image(), _TwoRegionSegmenter(), doc_id="d", page_id="p")
    ordered = document.pages[0].regions
    assert ordered[0] is right
    assert ordered[1] is left
    assert [r.reading_index for r in ordered] == [0, 1]
