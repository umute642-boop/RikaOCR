# SPDX-License-Identifier: Apache-2.0
"""Tests for the DummySegmenter."""

from PIL import Image

from rikaocr.core.document.enums import RegionType
from rikaocr.layout.base import Segmenter
from rikaocr.layout.dummy import DummySegmenter


def _image(width: int = 90, height: int = 30) -> Image.Image:
    return Image.new("RGB", (width, height), (255, 255, 255))


def test_produces_one_paragraph_region_with_n_lines() -> None:
    result = DummySegmenter(num_lines=3).segment(_image())
    assert len(result.regions) == 1
    region = result.regions[0]
    assert region.region_type is RegionType.PARAGRAPH
    assert len(region.lines) == 3


def test_lines_are_full_width_disjoint_bands() -> None:
    result = DummySegmenter(num_lines=3).segment(_image(90, 30))
    boxes = [line.polygon.bounding_box() for line in result.regions[0].lines]
    # Full width and stacked vertically without gaps: 0-10, 10-20, 20-30.
    assert [b.y_min for b in boxes] == [0, 10, 20]
    assert [b.y_max for b in boxes] == [10, 20, 30]
    assert all(b.x_min == 0 and b.x_max == 90 for b in boxes)
    # Segmentation produces geometry only -- no text yet.
    assert all(line.text == "" for line in result.regions[0].lines)


def test_satisfies_segmenter_protocol() -> None:
    assert isinstance(DummySegmenter(), Segmenter)
