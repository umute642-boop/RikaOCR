# SPDX-License-Identifier: Apache-2.0
"""Crop line images from a page image using the document's geometry.

For each line that has a polygon, its bounding box is cropped from the page. If
``mask_polygon`` is set, pixels outside the polygon are painted white. Lines
without croppable geometry, and boxes that clamp to zero area, are skipped (with
a warning). Dewarping is intentionally out of scope (see the M4 plan). Requires
the optional ``[data]`` extra.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from rikaocr.common.logging import get_logger
from rikaocr.core.document.geometry import Polygon
from rikaocr.core.document.models import Document, Line

_logger = get_logger(__name__)
_WHITE_RGB = (255, 255, 255)


def crop_lines(
    document: Document, page_image: Image.Image, *, mask_polygon: bool = False
) -> list[tuple[Line, Image.Image]]:
    """Crop every croppable line of ``document`` from ``page_image`` (reading order)."""
    crops: list[tuple[Line, Image.Image]] = []
    for page in document.pages:
        for region in page.iter_in_reading_order():
            for line in region.iter_in_reading_order():
                cropped = crop_line(page_image, line, mask_polygon=mask_polygon)
                if cropped is not None:
                    crops.append((line, cropped))
    return crops


def crop_line(
    page_image: Image.Image, line: Line, *, mask_polygon: bool = False
) -> Image.Image | None:
    """Crop a single line's image, or return ``None`` if it cannot be cropped."""
    if line.polygon is None:
        _logger.warning("Skipping line without polygon geometry: %r", line.text)
        return None

    width, height = page_image.size
    box = line.polygon.bounding_box()
    left = _clamp(box.x_min, 0, width)
    upper = _clamp(box.y_min, 0, height)
    right = _clamp(box.x_max, 0, width)
    lower = _clamp(box.y_max, 0, height)
    if right <= left or lower <= upper:
        _logger.warning("Skipping line with empty cropped area: %r", line.text)
        return None

    cropped = page_image.crop((left, upper, right, lower)).convert("RGB")
    if not mask_polygon:
        return cropped
    return _apply_polygon_mask(cropped, line.polygon, origin=(left, upper))


def _apply_polygon_mask(
    cropped: Image.Image, polygon: Polygon, *, origin: tuple[int, int]
) -> Image.Image:
    offset_x, offset_y = origin
    points = [(point.x - offset_x, point.y - offset_y) for point in polygon.points]
    mask = Image.new("L", cropped.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    background = Image.new("RGB", cropped.size, _WHITE_RGB)
    background.paste(cropped, (0, 0), mask)
    return background


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


__all__ = ["crop_lines", "crop_line"]
