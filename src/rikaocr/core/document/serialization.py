# SPDX-License-Identifier: Apache-2.0
"""(De)serialisation of the document model to/from plain dicts and JSON.

The dict form is the canonical interchange shape; JSON is a thin wrapper over
it. Round-trips ``Document -> dict/JSON -> Document`` are lossless. Deserialising
does *not* validate domain invariants (call ``Document.validate()`` separately);
this keeps partially-built documents serialisable.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, cast

from rikaocr.common.exceptions import SerializationError
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Baseline, BBox, Point, Polygon
from rikaocr.core.document.models import (
    SCHEMA_VERSION,
    Document,
    Line,
    Page,
    Region,
    Token,
    Word,
)

# --- geometry ---------------------------------------------------------------


def _point_to_dict(point: Point) -> dict[str, int]:
    return {"x": point.x, "y": point.y}


def _point_from_dict(data: Mapping[str, Any]) -> Point:
    return Point(int(data["x"]), int(data["y"]))


def _bbox_to_dict(bbox: BBox) -> dict[str, int]:
    return {
        "x_min": bbox.x_min,
        "y_min": bbox.y_min,
        "x_max": bbox.x_max,
        "y_max": bbox.y_max,
    }


def _bbox_from_dict(data: Mapping[str, Any]) -> BBox:
    return BBox(int(data["x_min"]), int(data["y_min"]), int(data["x_max"]), int(data["y_max"]))


def _points_to_list(points: Sequence[Point]) -> list[dict[str, int]]:
    return [_point_to_dict(point) for point in points]


def _points_from_list(data: Sequence[Mapping[str, Any]]) -> tuple[Point, ...]:
    return tuple(_point_from_dict(point) for point in data)


def _polygon_to_dict(polygon: Polygon) -> dict[str, Any]:
    return {"points": _points_to_list(polygon.points)}


def _polygon_from_dict(data: Mapping[str, Any]) -> Polygon:
    return Polygon(_points_from_list(data["points"]))


def _baseline_to_dict(baseline: Baseline) -> dict[str, Any]:
    return {"points": _points_to_list(baseline.points)}


def _baseline_from_dict(data: Mapping[str, Any]) -> Baseline:
    return Baseline(_points_from_list(data["points"]))


# --- entities ---------------------------------------------------------------


def _token_to_dict(token: Token) -> dict[str, Any]:
    return {
        "text": token.text,
        "index": token.index,
        "bbox": _bbox_to_dict(token.bbox) if token.bbox is not None else None,
    }


def _token_from_dict(data: Mapping[str, Any]) -> Token:
    bbox = data.get("bbox")
    return Token(
        text=data["text"],
        index=int(data["index"]),
        bbox=_bbox_from_dict(bbox) if bbox is not None else None,
    )


def _word_to_dict(word: Word) -> dict[str, Any]:
    return {
        "text": word.text,
        "bbox": _bbox_to_dict(word.bbox) if word.bbox is not None else None,
        "tokens": [_token_to_dict(token) for token in word.tokens],
    }


def _word_from_dict(data: Mapping[str, Any]) -> Word:
    bbox = data.get("bbox")
    return Word(
        text=data["text"],
        bbox=_bbox_from_dict(bbox) if bbox is not None else None,
        tokens=[_token_from_dict(token) for token in data.get("tokens", [])],
    )


def _line_to_dict(line: Line) -> dict[str, Any]:
    return {
        "text": line.text,
        "reading_index": line.reading_index,
        "baseline": _baseline_to_dict(line.baseline) if line.baseline is not None else None,
        "polygon": _polygon_to_dict(line.polygon) if line.polygon is not None else None,
        "words": [_word_to_dict(word) for word in line.words],
        "confidence": line.confidence,
    }


def _line_from_dict(data: Mapping[str, Any]) -> Line:
    baseline = data.get("baseline")
    polygon = data.get("polygon")
    return Line(
        text=data["text"],
        reading_index=int(data.get("reading_index", 0)),
        baseline=_baseline_from_dict(baseline) if baseline is not None else None,
        polygon=_polygon_from_dict(polygon) if polygon is not None else None,
        words=[_word_from_dict(word) for word in data.get("words", [])],
        confidence=data.get("confidence"),
    )


def _region_to_dict(region: Region) -> dict[str, Any]:
    return {
        "region_type": region.region_type.value,
        "reading_index": region.reading_index,
        "polygon": _polygon_to_dict(region.polygon) if region.polygon is not None else None,
        "lines": [_line_to_dict(line) for line in region.lines],
    }


def _region_from_dict(data: Mapping[str, Any]) -> Region:
    polygon = data.get("polygon")
    return Region(
        region_type=RegionType(data["region_type"]),
        reading_index=int(data.get("reading_index", 0)),
        polygon=_polygon_from_dict(polygon) if polygon is not None else None,
        lines=[_line_from_dict(line) for line in data.get("lines", [])],
    )


def _page_to_dict(page: Page) -> dict[str, Any]:
    return {
        "page_id": page.page_id,
        "image_ref": page.image_ref,
        "width": page.width,
        "height": page.height,
        "regions": [_region_to_dict(region) for region in page.regions],
    }


def _page_from_dict(data: Mapping[str, Any]) -> Page:
    return Page(
        page_id=data["page_id"],
        image_ref=data.get("image_ref"),
        width=data.get("width"),
        height=data.get("height"),
        regions=[_region_from_dict(region) for region in data.get("regions", [])],
    )


def _document_from_dict(data: Mapping[str, Any]) -> Document:
    return Document(
        doc_id=data["doc_id"],
        pages=[_page_from_dict(page) for page in data.get("pages", [])],
        metadata=dict(data.get("metadata", {})),
        schema_version=data["schema_version"],
    )


# --- public API -------------------------------------------------------------


def to_dict(document: Document) -> dict[str, Any]:
    """Serialise a document to a plain, JSON-compatible dict."""
    return {
        "schema_version": document.schema_version,
        "doc_id": document.doc_id,
        "metadata": dict(document.metadata),
        "pages": [_page_to_dict(page) for page in document.pages],
    }


def from_dict(data: Mapping[str, Any]) -> Document:
    """Reconstruct a document from its dict form.

    Raises:
        SerializationError: if the schema version is unsupported or the data is
            malformed.
    """
    if "schema_version" not in data:
        raise SerializationError("Missing 'schema_version' in document data.")
    version = data["schema_version"]
    if version != SCHEMA_VERSION:
        raise SerializationError(
            f"Unsupported schema_version: {version!r} (expected {SCHEMA_VERSION!r})."
        )
    try:
        return _document_from_dict(data)
    except (KeyError, TypeError, ValueError) as exc:
        raise SerializationError(f"Malformed document data: {exc}") from exc


def to_json(document: Document, *, indent: int | None = None) -> str:
    """Serialise a document to a JSON string (UTF-8, non-ASCII preserved)."""
    return json.dumps(to_dict(document), ensure_ascii=False, indent=indent)


def from_json(text: str) -> Document:
    """Reconstruct a document from a JSON string."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SerializationError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SerializationError("Top-level JSON value must be an object.")
    return from_dict(cast(Mapping[str, Any], data))


__all__ = ["to_dict", "from_dict", "to_json", "from_json"]
