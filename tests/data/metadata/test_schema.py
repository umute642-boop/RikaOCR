# SPDX-License-Identifier: Apache-2.0
"""Tests for document metadata schema (de)serialisation."""

import pytest

from rikaocr.common.exceptions import DataError
from rikaocr.data.metadata.rights import RightsStatus
from rikaocr.data.metadata.schema import (
    ArchiveInfo,
    CatalogRef,
    DocumentInfo,
    DocumentMetadata,
    Provenance,
    from_mapping,
    to_mapping,
)


def _full_metadata() -> DocumentMetadata:
    return DocumentMetadata(
        provenance=Provenance(
            source="BOA",
            accessed_at="2026-06-30",
            rights_status=RightsStatus.RESTRICTED,
            notes="ornek",
        ),
        document_info=DocumentInfo(doc_type="arz", date_text="1290", language="ota", hand="rika"),
        catalog=CatalogRef(fon="A.MKT", dosya="12", gomlek="3"),
        archive=ArchiveInfo(collection="BOA", period="19c"),
    )


def test_full_round_trip() -> None:
    metadata = _full_metadata()
    assert from_mapping(to_mapping(metadata)) == metadata


def test_minimal_round_trip() -> None:
    metadata = DocumentMetadata(
        provenance=Provenance(source="s", accessed_at="t", rights_status=RightsStatus.UNKNOWN)
    )
    assert from_mapping(to_mapping(metadata)) == metadata


def test_missing_required_field_raises() -> None:
    with pytest.raises(DataError):
        from_mapping({"provenance": {"source": "s"}})


def test_invalid_rights_value_raises() -> None:
    payload = {"provenance": {"source": "s", "accessed_at": "t", "rights_status": "bogus"}}
    with pytest.raises(DataError):
        from_mapping(payload)
