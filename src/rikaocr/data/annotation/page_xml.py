# SPDX-License-Identifier: Apache-2.0
"""PAGE-XML codec: convert eScriptorium/Kraken PAGE files to/from the document model.

Both the reader (``from_page_xml``) and writer (``to_page_xml``), plus a
file-based :class:`PageXmlCodec`, use the standard-library
``xml.etree.ElementTree`` (no third-party dependency).

Round-trip guarantee (see the M2 plan and ADR-017): ``Document -> PAGE ->
Document`` is lossless for documents in the canonical form produced by the
reader and by layout, namely: exactly one page; ``page_id`` equal to
``image_ref``; contiguous ``reading_index`` values in reading order; empty
``metadata``; and words without sub-token (glyph) decomposition. The reverse
direction (``PAGE -> Document -> PAGE``) simplifies word/glyph polygons to
bounding boxes, matching the document model (ADR-009).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Sequence
from pathlib import Path

from rikaocr.common.exceptions import DataError
from rikaocr.common.types import PathLike
from rikaocr.core.document.geometry import Baseline, BBox, Point, Polygon
from rikaocr.core.document.models import Document, Line, Page, Region, Word
from rikaocr.data.annotation.region_mapping import region_type_from_page, region_type_to_page

PAGE_NAMESPACE = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"
_PLACEHOLDER_TIMESTAMP = "1970-01-01T00:00:00"


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
    doc_id = root.get("pcGtsId") or (image_ref.rsplit(".", 1)[0] if image_ref else "document")
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


def to_page_xml(document: Document, *, indent: bool = True) -> str:
    """Serialise a single-page :class:`Document` to a PAGE-XML string.

    Raises:
        DataError: if the document does not contain exactly one page (a PAGE-XML
            file represents exactly one page).
    """
    if len(document.pages) != 1:
        raise DataError("PAGE-XML represents exactly one page; document must have one page.")

    ET.register_namespace("", PAGE_NAMESPACE)
    ns = f"{{{PAGE_NAMESPACE}}}"
    root = ET.Element(f"{ns}PcGts")
    if document.doc_id:
        root.set("pcGtsId", document.doc_id)
    _write_metadata(root, ns)
    _write_page(root, document.pages[0], ns)

    if indent:
        ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{body}\n'


def _write_metadata(root: ET.Element, ns: str) -> None:
    metadata = ET.SubElement(root, f"{ns}Metadata")
    ET.SubElement(metadata, f"{ns}Creator").text = "RikaOCR"
    ET.SubElement(metadata, f"{ns}Created").text = _PLACEHOLDER_TIMESTAMP
    ET.SubElement(metadata, f"{ns}LastChange").text = _PLACEHOLDER_TIMESTAMP


def _write_page(root: ET.Element, page: Page, ns: str) -> None:
    page_el = ET.SubElement(root, f"{ns}Page")
    if page.image_ref is not None:
        page_el.set("imageFilename", page.image_ref)
    if page.width is not None:
        page_el.set("imageWidth", str(page.width))
    if page.height is not None:
        page_el.set("imageHeight", str(page.height))
    for index, region in enumerate(page.iter_in_reading_order()):
        _write_region(page_el, region, ns, index)


def _write_region(parent: ET.Element, region: Region, ns: str, index: int) -> None:
    region_el = ET.SubElement(parent, f"{ns}TextRegion")
    region_el.set("id", f"r{index}")
    region_el.set("type", region_type_to_page(region.region_type))
    if region.polygon is not None:
        _write_coords(region_el, region.polygon.points, ns)
    for line_index, line in enumerate(region.iter_in_reading_order()):
        _write_line(region_el, line, ns, line_index)


def _write_line(parent: ET.Element, line: Line, ns: str, index: int) -> None:
    line_el = ET.SubElement(parent, f"{ns}TextLine")
    line_el.set("id", f"l{index}")
    if line.polygon is not None:
        _write_coords(line_el, line.polygon.points, ns)
    if line.baseline is not None:
        ET.SubElement(line_el, f"{ns}Baseline").set("points", _format_points(line.baseline.points))
    for word_index, word in enumerate(line.words):
        _write_word(line_el, word, ns, word_index)
    _write_text_equiv(line_el, line.text, ns, confidence=line.confidence)


def _write_word(parent: ET.Element, word: Word, ns: str, index: int) -> None:
    word_el = ET.SubElement(parent, f"{ns}Word")
    word_el.set("id", f"w{index}")
    if word.bbox is not None:
        _write_coords(word_el, _bbox_to_points(word.bbox), ns)
    _write_text_equiv(word_el, word.text, ns)


def _write_coords(parent: ET.Element, points: Sequence[Point], ns: str) -> None:
    ET.SubElement(parent, f"{ns}Coords").set("points", _format_points(points))


def _write_text_equiv(
    parent: ET.Element, text: str, ns: str, *, confidence: float | None = None
) -> None:
    text_equiv = ET.SubElement(parent, f"{ns}TextEquiv")
    if confidence is not None:
        text_equiv.set("conf", f"{confidence}")
    ET.SubElement(text_equiv, f"{ns}Unicode").text = text


def _format_points(points: Sequence[Point]) -> str:
    return " ".join(f"{point.x},{point.y}" for point in points)


def _bbox_to_points(bbox: BBox) -> tuple[Point, ...]:
    return (
        Point(bbox.x_min, bbox.y_min),
        Point(bbox.x_max, bbox.y_min),
        Point(bbox.x_max, bbox.y_max),
        Point(bbox.x_min, bbox.y_max),
    )


class PageXmlCodec:
    """File-based PAGE-XML codec wrapping :func:`from_page_xml` / :func:`to_page_xml`."""

    def load(self, path: PathLike) -> Document:
        """Read a PAGE-XML file and return a :class:`Document`."""
        return from_page_xml(Path(path).read_text(encoding="utf-8"))

    def save(self, document: Document, path: PathLike, *, indent: bool = True) -> None:
        """Write a :class:`Document` to ``path`` as PAGE-XML."""
        Path(path).write_text(to_page_xml(document, indent=indent), encoding="utf-8")


__all__ = ["from_page_xml", "to_page_xml", "PageXmlCodec", "PAGE_NAMESPACE"]
