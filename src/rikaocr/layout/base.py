# SPDX-License-Identifier: Apache-2.0
"""Layout segmentation port and the page-level helper (ADR-011, ADR-020).

``Segmenter`` is the engine-agnostic contract; an engine's output is returned as
a thin, motor-neutral :class:`SegmentationResult` (regions with line geometry,
no text). :func:`segment_document` assembles a :class:`Document`, assigning a
deterministic right-to-left reading order. Requires the optional ``[data]``
extra (Pillow) for the image type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from PIL import Image

from rikaocr.core.document.geometry import BBox
from rikaocr.core.document.models import Document, Line, Page, Region

# Sort key for items whose bounding box could not be determined: pushed last
# while preserving their original relative order (Python's sort is stable).
_NO_BBOX_KEY = (1, 0, 0)


@dataclass(frozen=True, slots=True)
class SegmentationResult:
    """Engine output: the regions (with line geometry) found on one page.

    This is intentionally thin -- it carries only the produced geometry, leaving
    page bookkeeping (size, reading order) to :func:`segment_document`.
    """

    regions: list[Region] = field(default_factory=list)


@runtime_checkable
class Segmenter(Protocol):
    """Detects the region/line geometry of a single page image."""

    def segment(self, image: Image.Image) -> SegmentationResult:
        """Return the regions and lines detected in ``image`` (no text)."""
        ...


def _line_bbox(line: Line) -> BBox | None:
    """Best-effort bounding box for a line (polygon, else baseline)."""
    if line.polygon is not None:
        return line.polygon.bounding_box()
    if line.baseline is not None:
        return BBox.from_points(line.baseline.points)
    return None


def _region_bbox(region: Region) -> BBox | None:
    """Best-effort bounding box for a region (polygon, else its lines)."""
    if region.polygon is not None:
        return region.polygon.bounding_box()
    boxes = [box for line in region.lines if (box := _line_bbox(line)) is not None]
    if not boxes:
        return None
    return BBox(
        min(b.x_min for b in boxes),
        min(b.y_min for b in boxes),
        max(b.x_max for b in boxes),
        max(b.y_max for b in boxes),
    )


def _rtl_key(bbox: BBox | None) -> tuple[int, int, int]:
    """Reading-order key: top-to-bottom, then right-to-left (RTL)."""
    if bbox is None:
        return _NO_BBOX_KEY
    return (0, bbox.y_min, -bbox.x_min)


def order_reading(regions: list[Region]) -> list[Region]:
    """Sort ``regions`` and their lines into RTL reading order, in place.

    Regions and the lines within each region are ordered top-to-bottom then
    right-to-left, and their ``reading_index`` fields are reassigned to match.
    Items without resolvable geometry keep their original relative order and are
    placed last. Returns the same list (now reordered) for convenience.
    """
    regions.sort(key=lambda region: _rtl_key(_region_bbox(region)))
    for region_index, region in enumerate(regions):
        region.reading_index = region_index
        region.lines.sort(key=lambda line: _rtl_key(_line_bbox(line)))
        for line_index, line in enumerate(region.lines):
            line.reading_index = line_index
    return regions


def segment_document(
    image: Image.Image,
    segmenter: Segmenter,
    *,
    doc_id: str,
    page_id: str,
    image_ref: str | None = None,
) -> Document:
    """Segment ``image`` into a single-page :class:`Document` with reading order.

    The page's ``width``/``height`` are taken from the image; the detected
    regions are ordered via :func:`order_reading`. No text is filled in -- pass
    the result to :func:`rikaocr.recognition.base.recognize_document` for that.
    """
    result = segmenter.segment(image)
    regions = order_reading(list(result.regions))
    width, height = image.size
    page = Page(
        page_id=page_id,
        image_ref=image_ref,
        width=width,
        height=height,
        regions=regions,
    )
    return Document(doc_id=doc_id, pages=[page])


__all__ = ["SegmentationResult", "Segmenter", "order_reading", "segment_document"]
