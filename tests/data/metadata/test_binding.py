# SPDX-License-Identifier: Apache-2.0
"""Tests for binding metadata to a Document (incl. JSON round-trip)."""

from rikaocr.core.document.models import Document
from rikaocr.core.document.serialization import from_json, to_json
from rikaocr.data.metadata.binding import attach, extract
from rikaocr.data.metadata.rights import RightsStatus
from rikaocr.data.metadata.schema import DocumentMetadata, Provenance


def _metadata() -> DocumentMetadata:
    return DocumentMetadata(
        provenance=Provenance(
            source="BOA",
            accessed_at="2026-06-30",
            rights_status=RightsStatus.RESTRICTED,
        )
    )


def test_attach_then_extract() -> None:
    document = Document(doc_id="d")
    metadata = _metadata()
    attach(document, metadata)
    assert extract(document) == metadata


def test_extract_returns_none_when_absent() -> None:
    assert extract(Document(doc_id="d")) is None


def test_metadata_survives_document_json_round_trip() -> None:
    document = Document(doc_id="d")
    attach(document, _metadata())
    restored = from_json(to_json(document))
    assert extract(restored) == _metadata()
