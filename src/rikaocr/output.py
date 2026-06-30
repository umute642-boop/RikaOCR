# SPDX-License-Identifier: Apache-2.0
"""Persist a recognised :class:`Document` to disk (the pipeline output bridge).

This is the thin seam between the pipeline's in-memory result and on-disk
formats. PAGE-XML serialisation is delegated to the existing
:class:`~rikaocr.data.annotation.page_xml.PageXmlCodec` (no logic duplicated);
plain-text export joins line texts in reading order. Keeping a single, stable
output API here means future formats (ALTO, hOCR, JSONL) can be added in one
place without touching the pipeline.
"""

from __future__ import annotations

from pathlib import Path

from rikaocr.common.types import PathLike
from rikaocr.core.document.models import Document
from rikaocr.data.annotation.page_xml import PageXmlCodec


def write_page_xml(document: Document, path: PathLike, *, indent: bool = True) -> None:
    """Write ``document`` to ``path`` as PAGE-XML via :class:`PageXmlCodec`.

    Raises:
        DataError: if the document does not contain exactly one page.
    """
    PageXmlCodec().save(document, path, indent=indent)


def document_to_text(document: Document) -> str:
    """Return the document's text in reading order.

    Lines within a page are joined by newlines; pages are separated by a blank
    line. Region and line order follow each container's ``reading_index``.
    """
    pages: list[str] = []
    for page in document.pages:
        lines = [
            line.text
            for region in page.iter_in_reading_order()
            for line in region.iter_in_reading_order()
        ]
        pages.append("\n".join(lines))
    return "\n\n".join(pages)


def write_text(document: Document, path: PathLike) -> None:
    """Write the document's reading-order text to ``path`` (UTF-8)."""
    Path(path).write_text(document_to_text(document), encoding="utf-8")


__all__ = ["write_page_xml", "document_to_text", "write_text"]
