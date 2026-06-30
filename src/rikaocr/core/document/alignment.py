# SPDX-License-Identifier: Apache-2.0
"""Alignment invariants between text and geometry (ADR-009).

These checks are intentionally separate from ``Entity.validate()``: validation
covers structural invariants, while alignment verifies that — *when geometry is
present* — the text and its coordinates agree. Geometry stays optional; only
genuine inconsistencies are reported.

Containment is checked with axis-aligned bounding boxes (a polygon's box must
enclose its children's boxes). Text consistency requires tokens to concatenate
to their word's text, and words to join (with a separator) into their line's
text. The word separator defaults to a single space but can be overridden, since
the precise rule ultimately comes from the script profile (ADR-010).
"""

from __future__ import annotations

from rikaocr.common.exceptions import AlignmentError
from rikaocr.core.document.geometry import BBox
from rikaocr.core.document.models import Document, Line, Region, Word

DEFAULT_WORD_SEPARATOR = " "


def validate_alignment(document: Document, *, word_separator: str = DEFAULT_WORD_SEPARATOR) -> None:
    """Validate text-to-geometry alignment across the whole document.

    Raises:
        AlignmentError: if any text/geometry inconsistency is found.
    """
    for page in document.pages:
        for region in page.regions:
            _check_region(region, word_separator)


def _check_region(region: Region, word_separator: str) -> None:
    region_bbox = region.polygon.bounding_box() if region.polygon is not None else None
    for line in region.lines:
        _check_line(line, region_bbox, word_separator)


def _check_line(line: Line, region_bbox: BBox | None, word_separator: str) -> None:
    line_bbox = line.polygon.bounding_box() if line.polygon is not None else None
    if region_bbox is not None and line_bbox is not None and not region_bbox.contains(line_bbox):
        raise AlignmentError(f"Line polygon is not contained within its region: {line.text!r}.")
    if line.words and line.text != word_separator.join(word.text for word in line.words):
        raise AlignmentError(f"Line text does not match its words: {line.text!r}.")
    for word in line.words:
        _check_word(word, line_bbox)


def _check_word(word: Word, line_bbox: BBox | None) -> None:
    if word.bbox is not None and line_bbox is not None and not line_bbox.contains(word.bbox):
        raise AlignmentError(f"Word box is not contained within its line: {word.text!r}.")
    if word.tokens:
        ordered = sorted(word.tokens, key=lambda token: token.index)
        if word.text != "".join(token.text for token in ordered):
            raise AlignmentError(f"Word text does not match its tokens: {word.text!r}.")
    for token in word.tokens:
        if token.bbox is not None and word.bbox is not None and not word.bbox.contains(token.bbox):
            raise AlignmentError(f"Token box is not contained within its word: {token.text!r}.")


__all__ = ["validate_alignment", "DEFAULT_WORD_SEPARATOR"]
