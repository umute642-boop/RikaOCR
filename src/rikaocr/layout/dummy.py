# SPDX-License-Identifier: Apache-2.0
"""A trivial segmenter that splits a page into evenly spaced horizontal lines.

It performs no analysis: it returns one paragraph region spanning the page with
``num_lines`` full-width horizontal bands. Used to exercise the layout and
recognition pipeline without any model or heavy dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Point, Polygon
from rikaocr.core.document.models import Line, Region
from rikaocr.layout.base import SegmentationResult


def _rectangle(x0: int, y0: int, x1: int, y1: int) -> Polygon:
    return Polygon((Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1)))


@dataclass(frozen=True, slots=True)
class DummySegmenter:
    """Splits the page into ``num_lines`` full-width horizontal line bands."""

    num_lines: int = 3

    def segment(self, image: Image.Image) -> SegmentationResult:
        """Return one paragraph region with evenly spaced horizontal lines."""
        width, height = image.size
        lines: list[Line] = []
        for index in range(self.num_lines):
            y0 = index * height // self.num_lines
            y1 = (index + 1) * height // self.num_lines
            lines.append(Line(text="", polygon=_rectangle(0, y0, width, y1)))
        region = Region(
            region_type=RegionType.PARAGRAPH,
            polygon=_rectangle(0, 0, width, height),
            lines=lines,
        )
        return SegmentationResult(regions=[region])


__all__ = ["DummySegmenter"]
