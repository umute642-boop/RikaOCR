# SPDX-License-Identifier: Apache-2.0
"""Tests for line cropping (synthetic pages built at runtime with Pillow)."""

from PIL import Image, ImageDraw

from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Point, Polygon
from rikaocr.core.document.models import Document, Line, Page, Region
from rikaocr.data.dataset.cropping import crop_line, crop_lines


def _rect_polygon(x0: int, y0: int, x1: int, y1: int) -> Polygon:
    return Polygon((Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1)))


def _document_with_lines(lines: list[Line]) -> Document:
    region = Region(region_type=RegionType.PARAGRAPH, lines=lines)
    return Document(doc_id="d", pages=[Page(page_id="p", regions=[region])])


def test_crop_line_size_and_content() -> None:
    page = Image.new("RGB", (100, 60), (255, 255, 255))
    ImageDraw.Draw(page).rectangle((10, 10, 49, 29), fill=(0, 0, 0))
    line = Line(text="x", polygon=_rect_polygon(10, 10, 50, 30))

    cropped = crop_line(page, line)

    assert cropped is not None
    assert cropped.size == (40, 20)
    assert cropped.getpixel((0, 0)) == (0, 0, 0)


def test_crop_line_polygon_mask_whitens_outside() -> None:
    page = Image.new("RGB", (40, 20), (0, 0, 0))
    triangle = Polygon((Point(0, 0), Point(40, 0), Point(0, 20)))
    line = Line(text="x", polygon=triangle)

    masked = crop_line(page, line, mask_polygon=True)

    assert masked is not None
    assert masked.size == (40, 20)
    assert masked.getpixel((1, 1)) == (0, 0, 0)  # inside triangle -> original
    assert masked.getpixel((39, 19)) == (255, 255, 255)  # outside -> white


def test_crop_line_clamps_to_page_bounds() -> None:
    page = Image.new("RGB", (60, 60), (255, 255, 255))
    line = Line(text="x", polygon=_rect_polygon(40, 40, 80, 80))

    cropped = crop_line(page, line)

    assert cropped is not None
    assert cropped.size == (20, 20)


def test_crop_line_out_of_bounds_returns_none() -> None:
    page = Image.new("RGB", (50, 50), (255, 255, 255))
    line = Line(text="x", polygon=_rect_polygon(60, 60, 80, 80))
    assert crop_line(page, line) is None


def test_crop_line_without_polygon_returns_none() -> None:
    page = Image.new("RGB", (20, 20), (255, 255, 255))
    assert crop_line(page, Line(text="x")) is None


def test_crop_line_zero_area_returns_none() -> None:
    page = Image.new("RGB", (20, 20), (255, 255, 255))
    line = Line(text="x", polygon=Polygon((Point(5, 5), Point(5, 5), Point(5, 5))))
    assert crop_line(page, line) is None


def test_crop_lines_skips_uncroppable_and_preserves_text() -> None:
    page = Image.new("RGB", (100, 60), (255, 255, 255))
    croppable = Line(text="ok", reading_index=0, polygon=_rect_polygon(0, 0, 30, 20))
    no_geometry = Line(text="skip", reading_index=1)

    results = crop_lines(_document_with_lines([croppable, no_geometry]), page)

    assert [line.text for line, _ in results] == ["ok"]
    assert results[0][1].size == (30, 20)
