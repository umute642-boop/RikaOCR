# SPDX-License-Identifier: Apache-2.0
"""Mutable document entities forming the core domain aggregate.

The hierarchy is ``Document -> Page -> Region -> Line -> Word -> Token``. Unlike
the geometry value objects, these entities are *mutable*: the document is filled
in progressively by the pipeline (layout adds regions and lines, recognition
fills in text). Each entity exposes a ``validate()`` method that checks its own
invariants and recurses into its children.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Final

from rikaocr.common.exceptions import ValidationError
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Baseline, BBox, Polygon

SCHEMA_VERSION: Final = "1.0"
"""Schema version of the serialised document representation."""


@dataclass(slots=True)
class Token:
    """The smallest recognised unit (a character or sub-word piece)."""

    text: str
    index: int
    bbox: BBox | None = None

    def validate(self) -> None:
        """Validate token invariants."""
        if self.text == "":
            raise ValidationError("Token text must not be empty.")
        if self.index < 0:
            raise ValidationError(f"Token index must be non-negative, got {self.index}.")


@dataclass(slots=True)
class Word:
    """A word, optionally decomposed into ordered tokens."""

    text: str
    bbox: BBox | None = None
    tokens: list[Token] = field(default_factory=list)

    def validate(self) -> None:
        """Validate word invariants and all contained tokens."""
        if self.text == "":
            raise ValidationError("Word text must not be empty.")
        for token in self.tokens:
            token.validate()


@dataclass(slots=True)
class Line:
    """A text line: the fundamental unit of HTR.

    ``text`` holds the Arabic-script (Unicode) transcription; ``baseline`` and
    ``polygon`` anchor it on the page (see ADR-009).
    """

    text: str
    reading_index: int = 0
    baseline: Baseline | None = None
    polygon: Polygon | None = None
    words: list[Word] = field(default_factory=list)
    confidence: float | None = None

    def validate(self) -> None:
        """Validate line invariants and all contained words."""
        if self.reading_index < 0:
            raise ValidationError(
                f"Line reading_index must be non-negative, got {self.reading_index}."
            )
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValidationError(f"Line confidence must be in [0.0, 1.0], got {self.confidence}.")
        for word in self.words:
            word.validate()


@dataclass(slots=True)
class Region:
    """A layout region (text block, marginalia, seal, ...) on a page."""

    region_type: RegionType
    reading_index: int = 0
    polygon: Polygon | None = None
    lines: list[Line] = field(default_factory=list)

    def validate(self) -> None:
        """Validate region invariants and all contained lines."""
        if self.reading_index < 0:
            raise ValidationError(
                f"Region reading_index must be non-negative, got {self.reading_index}."
            )
        for line in self.lines:
            line.validate()

    def iter_in_reading_order(self) -> Iterator[Line]:
        """Yield lines ordered by their ``reading_index``."""
        return iter(sorted(self.lines, key=lambda line: line.reading_index))


@dataclass(slots=True)
class Page:
    """A single page image and its recognised regions."""

    page_id: str
    image_ref: str | None = None
    width: int | None = None
    height: int | None = None
    regions: list[Region] = field(default_factory=list)

    def validate(self) -> None:
        """Validate page invariants and all contained regions."""
        if self.page_id == "":
            raise ValidationError("Page page_id must not be empty.")
        if self.width is not None and self.width < 0:
            raise ValidationError(f"Page width must be non-negative, got {self.width}.")
        if self.height is not None and self.height < 0:
            raise ValidationError(f"Page height must be non-negative, got {self.height}.")
        for region in self.regions:
            region.validate()

    def iter_in_reading_order(self) -> Iterator[Region]:
        """Yield regions ordered by their ``reading_index``."""
        return iter(sorted(self.regions, key=lambda region: region.reading_index))


@dataclass(slots=True)
class Document:
    """The aggregate root: a document and all of its pages.

    ``metadata`` is a free-form slot enriched later by the metadata layer; it is
    intentionally untyped at this stage.
    """

    doc_id: str
    pages: list[Page] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def validate(self) -> None:
        """Validate document invariants and recurse into all pages."""
        if self.doc_id == "":
            raise ValidationError("Document doc_id must not be empty.")
        for page in self.pages:
            page.validate()


__all__ = [
    "SCHEMA_VERSION",
    "Token",
    "Word",
    "Line",
    "Region",
    "Page",
    "Document",
]
