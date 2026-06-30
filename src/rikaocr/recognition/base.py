# SPDX-License-Identifier: Apache-2.0
"""Recognition interface and the document-level recognition helper.

``Recognizer`` is the engine-agnostic contract; concrete engines implement it so
the core domain stays free of heavy ML dependencies. Requires the optional
``[data]`` extra (Pillow) for the image type and line cropping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from PIL import Image

from rikaocr.core.document.models import Document
from rikaocr.data.dataset.cropping import crop_line


@dataclass(frozen=True, slots=True)
class RecognitionResult:
    """The recognised text for one line image, with optional confidence."""

    text: str
    confidence: float | None = None


@runtime_checkable
class Recognizer(Protocol):
    """Recognises the text of a single line image."""

    def recognize(self, image: Image.Image) -> RecognitionResult:
        """Return the recognised text (and optional confidence) for ``image``."""
        ...


def recognize_document(
    document: Document,
    page_image: Image.Image,
    recognizer: Recognizer,
    *,
    mask_polygon: bool = False,
) -> Document:
    """Recognise every croppable line of ``document`` and fill in ``line.text``.

    The document is mutated in place (and also returned). Lines that cannot be
    cropped (no geometry or empty area) are left unchanged.
    """
    for page in document.pages:
        for region in page.iter_in_reading_order():
            for line in region.iter_in_reading_order():
                cropped = crop_line(page_image, line, mask_polygon=mask_polygon)
                if cropped is None:
                    continue
                result = recognizer.recognize(cropped)
                line.text = result.text
                line.confidence = result.confidence
    return document


__all__ = ["RecognitionResult", "Recognizer", "recognize_document"]
