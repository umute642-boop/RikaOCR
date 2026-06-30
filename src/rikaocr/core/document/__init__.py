# SPDX-License-Identifier: Apache-2.0
"""Document domain model: geometry, entities, alignment, and serialization."""

from rikaocr.core.document.alignment import validate_alignment
from rikaocr.core.document.enums import ReadingDirection, RegionType
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
from rikaocr.core.document.serialization import from_dict, from_json, to_dict, to_json

__all__ = [
    "SCHEMA_VERSION",
    "BBox",
    "Baseline",
    "Document",
    "Line",
    "Page",
    "Point",
    "Polygon",
    "ReadingDirection",
    "Region",
    "RegionType",
    "Token",
    "Word",
    "from_dict",
    "from_json",
    "to_dict",
    "to_json",
    "validate_alignment",
]
