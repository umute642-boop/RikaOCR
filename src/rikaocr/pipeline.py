# SPDX-License-Identifier: Apache-2.0
"""End-to-end recognition pipeline: image -> geometry -> text -> Document.

The :class:`Pipeline` wires the two engine ports together: a
:class:`~rikaocr.layout.base.Segmenter` produces the region/line geometry of a
page, then a :class:`~rikaocr.recognition.base.Recognizer` fills in each line's
text. Both engines are injected, so the same pipeline runs with the dependency-
free ``Dummy*`` engines (tests, demos) or with the Kraken adapters (real HTR).

Evaluation is intentionally kept separate (see ADR-020): the pipeline produces a
``Document``; scoring it against ground truth is the evaluation layer's job.
Requires the optional ``[data]`` extra (Pillow) for the image type.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from rikaocr.core.document.models import Document
from rikaocr.layout.base import Segmenter, segment_document
from rikaocr.recognition.base import Recognizer, recognize_document


@dataclass(frozen=True, slots=True)
class Pipeline:
    """Composes a segmenter and a recognizer into one image-to-text run."""

    segmenter: Segmenter
    recognizer: Recognizer

    def run(
        self,
        image: Image.Image,
        *,
        doc_id: str,
        page_id: str,
        image_ref: str | None = None,
        mask_polygon: bool = False,
    ) -> Document:
        """Segment then recognise ``image``, returning a filled ``Document``.

        The page is segmented into a single-page document with reading order
        assigned, then every croppable line is recognised and its ``text`` (and
        ``confidence``) filled in.

        Args:
            image: The page image to process.
            doc_id: Identifier for the produced document.
            page_id: Identifier for the single page.
            image_ref: Optional reference (e.g. filename) stored on the page.
            mask_polygon: Whether to mask each line crop to its polygon.

        Returns:
            The recognised :class:`Document` (one page).
        """
        document = segment_document(
            image,
            self.segmenter,
            doc_id=doc_id,
            page_id=page_id,
            image_ref=image_ref,
        )
        recognize_document(document, image, self.recognizer, mask_polygon=mask_polygon)
        return document


__all__ = ["Pipeline"]
