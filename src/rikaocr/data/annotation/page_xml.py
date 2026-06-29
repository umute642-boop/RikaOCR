# SPDX-License-Identifier: Apache-2.0
"""PAGE-XML reader: parse eScriptorium/Kraken PAGE files into the document model.

Only the reader (``from_page_xml``) is implemented here; the writer is added in a
later step. Parsing uses the standard-library ``xml.etree.ElementTree`` (no third
party dependency). Word/glyph coordinates are read as bounding boxes, matching
the document model (see ADR-009 and the M2 plan); the full PAGE polygon detail
below line level is intentionally simplified.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from rikaocr.common.exceptions import DataError
from rikaocr.core.document.geometry import Baseline, BBox, Point, Polygon
from rikaocr.core.document.models import Document, Line, Page, Region, Word
from rikaocr.data.annotation.region_mapping import region_type_from_page


def from_page_xml(text: str) -> Document:
    """Parse a PAGE-XML string into a :class:`Document`.

    Raises:
        DataError: if the input is not well-formed PAGE-XML, declares a DOCTYPE,
            or has no ``<Page>`` element.
    """
    if "<!DOCTYPE" in text:
        raise DataError("DOCTYPE declarations are not allowed in PAGE-XML input.")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise DataError(f"Malformed PAGE-XML: {exc}") from exc

    ns = _namespace(root)
    page_el = root.find(f"{ns}Page")
    if page_el is None:
        raise DataError("PAGE-XML has no <Page> element.")

    image_ref = page_el.get("imageFilename")
    page = Page(
        page_id=image_ref or "page-1",
        image_ref=image_ref,
        width=_int_or_none(page_el.get("imageWidth")),
        height=_int_or_none(page_el.get("imageHeight")),
        regions=[
            _read_region(region_el, ns, index)
            for index, region_el in enumerate(page_el.findall(f"{ns}TextRegion"))
        ],
    )
    doc_id = image_ref.rsplit(".", 1)[0] if image_ref else "document"
    return Document(doc_id=doc_id, pages=[page])


def _read_region(elem: ET.Element, ns: str, index: int) -> Region:
    return Region(
        region_type=region_type_from_page(elem.get("type")),
        reading_index=index,
        polygon=_coords_polygon(elem, ns),
        lines=[
            _read_line(line_el, ns, line_index)
            for line_index, line_el in enumerate(elem.findall(f"{ns}TextLine"))
        ],
    )


def _read_line(elem: ET.Element, ns: str, index: int) -> Line:
    text, confidence = _text_equiv(elem, ns)
    return Line(
        text=text,
        reading_index=index,
        baseline=_baseline(elem, ns),
        polygon=_coords_polygon(elem, ns),
        words=[_read_word(word_el, ns) for word_el in elem.findall(f"{ns}Word")],
        confidence=confidence,
    )


def _read_word(elem: ET.Element, ns: str) -> Word:
    text, _ = _text_equiv(elem, ns)
    return Word(text=text, bbox=_coords_bbox(elem, ns))


def _namespace(elem: ET.Element) -> str:
    tag = elem.tag
    if tag.startswith("{"):
        return tag[: tag.index("}") + 1]
    return ""


def _int_or_none(value: str | None) -> int | None:
    return int(value) if value is not None and value != "" else None


def _text_equiv(elem: ET.Element, ns: str) -> tuple[str, float | None]:
    text_equiv = elem.find(f"{ns}TextEquiv")
    if text_equiv is None:
        return "", None
    unicode_el = text_equiv.find(f"{ns}Unicode")
    text = unicode_el.text if unicode_el is not None and unicode_el.text is not None else ""
    conf = text_equiv.get("conf")
    return text, float(conf) if conf is not None else None


def _coords_polygon(elem: ET.Element, ns: str) -> Polygon | None:
    points = _coords_points(elem, ns)
    return Polygon(points) if points is not None and len(points) >= 3 else None


def _coords_bbox(elem: ET.Element, ns: str) -> BBox | None:
    points = _coords_points(elem, ns)
    return BBox.from_points(points) if points else None


def _coords_points(elem: ET.Element, ns: str) -> tuple[Point, ...] | None:
    coords = elem.find(f"{ns}Coords")
    if coords is None:
        return None
    raw = coords.get("points")
    return _parse_points(raw) if raw else None


def _baseline(elem: ET.Element, ns: str) -> Baseline | None:
    baseline_el = elem.find(f"{ns}Baseline")
    if baseline_el is None:
        return None
    raw = baseline_el.get("points")
    if not raw:
        return None
    points = _parse_points(raw)
    return Baseline(points) if len(points) >= 2 else None


def _parse_points(raw: str) -> tuple[Point, ...]:
    try:
        return tuple(_parse_point(pair) for pair in raw.split())
    except ValueError as exc:
        raise DataError(f"Invalid points string: {raw!r} ({exc})") from exc


def _parse_point(pair: str) -> Point:
    x_str, y_str = pair.split(",")
    return Point(int(float(x_str)), int(float(y_str)))


__all__ = ["from_page_xml"]
