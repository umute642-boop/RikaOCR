# SPDX-License-Identifier: Apache-2.0
"""Bind structured metadata to/from a Document's free-form metadata slot.

The metadata is stored under a single reserved key in ``Document.metadata`` as a
JSON-compatible mapping, so it round-trips automatically through the document
serialisation (``to_json`` / ``from_json``).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from rikaocr.common.exceptions import DataError
from rikaocr.core.document.models import Document
from rikaocr.data.metadata.schema import DocumentMetadata, from_mapping, to_mapping

_METADATA_KEY = "rikaocr_metadata"


def attach(document: Document, metadata: DocumentMetadata) -> None:
    """Attach structured metadata to a document (overwrites any existing)."""
    document.metadata[_METADATA_KEY] = to_mapping(metadata)


def extract(document: Document) -> DocumentMetadata | None:
    """Return the document's structured metadata, or ``None`` if absent.

    Raises:
        DataError: if a stored value exists but is not a valid metadata mapping.
    """
    raw = document.metadata.get(_METADATA_KEY)
    if raw is None:
        return None
    if not isinstance(raw, Mapping):
        raise DataError("Stored document metadata is not a mapping.")
    return from_mapping(cast("Mapping[str, Any]", raw))


__all__ = ["attach", "extract"]
