# SPDX-License-Identifier: Apache-2.0
"""Structured metadata for BOA documents.

Groups provenance, document info, catalog reference, and archive info into a
single ``DocumentMetadata`` aggregate, with lossless conversion to/from a
JSON-compatible mapping. All fields except provenance source/access/rights are
optional and intentionally minimal until real BOA catalogue data is available.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from rikaocr.common.exceptions import DataError
from rikaocr.data.metadata.rights import RightsStatus

METADATA_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Where a source came from and whether it may be redistributed."""

    source: str
    accessed_at: str
    rights_status: RightsStatus
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class DocumentInfo:
    """Document-level descriptive fields (all optional, extensible)."""

    doc_type: str | None = None
    date_text: str | None = None
    language: str | None = None
    hand: str | None = None


@dataclass(frozen=True, slots=True)
class CatalogRef:
    """Minimal BOA catalogue reference (extensible)."""

    fon: str | None = None
    dosya: str | None = None
    gomlek: str | None = None


@dataclass(frozen=True, slots=True)
class ArchiveInfo:
    """Minimal archive-level information (extensible)."""

    collection: str | None = None
    period: str | None = None


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    """Aggregate of all metadata attached to a document."""

    provenance: Provenance
    document_info: DocumentInfo = field(default_factory=DocumentInfo)
    catalog: CatalogRef = field(default_factory=CatalogRef)
    archive: ArchiveInfo = field(default_factory=ArchiveInfo)
    schema_version: str = METADATA_SCHEMA_VERSION


def to_mapping(metadata: DocumentMetadata) -> dict[str, Any]:
    """Serialise ``DocumentMetadata`` to a JSON-compatible mapping."""
    return {
        "schema_version": metadata.schema_version,
        "provenance": {
            "source": metadata.provenance.source,
            "accessed_at": metadata.provenance.accessed_at,
            "rights_status": metadata.provenance.rights_status.value,
            "notes": metadata.provenance.notes,
        },
        "document_info": {
            "doc_type": metadata.document_info.doc_type,
            "date_text": metadata.document_info.date_text,
            "language": metadata.document_info.language,
            "hand": metadata.document_info.hand,
        },
        "catalog": {
            "fon": metadata.catalog.fon,
            "dosya": metadata.catalog.dosya,
            "gomlek": metadata.catalog.gomlek,
        },
        "archive": {
            "collection": metadata.archive.collection,
            "period": metadata.archive.period,
        },
    }


def from_mapping(data: Mapping[str, Any]) -> DocumentMetadata:
    """Reconstruct ``DocumentMetadata`` from a mapping.

    Raises:
        DataError: if a required field is missing or a value is invalid.
    """
    try:
        prov = data["provenance"]
        provenance = Provenance(
            source=prov["source"],
            accessed_at=prov["accessed_at"],
            rights_status=RightsStatus(prov["rights_status"]),
            notes=prov.get("notes"),
        )
        info = data.get("document_info", {})
        document_info = DocumentInfo(
            doc_type=info.get("doc_type"),
            date_text=info.get("date_text"),
            language=info.get("language"),
            hand=info.get("hand"),
        )
        catalog_raw = data.get("catalog", {})
        catalog = CatalogRef(
            fon=catalog_raw.get("fon"),
            dosya=catalog_raw.get("dosya"),
            gomlek=catalog_raw.get("gomlek"),
        )
        archive_raw = data.get("archive", {})
        archive = ArchiveInfo(
            collection=archive_raw.get("collection"),
            period=archive_raw.get("period"),
        )
    except (KeyError, ValueError) as exc:
        raise DataError(f"Malformed document metadata: {exc}") from exc
    return DocumentMetadata(
        provenance=provenance,
        document_info=document_info,
        catalog=catalog,
        archive=archive,
        schema_version=data.get("schema_version", METADATA_SCHEMA_VERSION),
    )


__all__ = [
    "METADATA_SCHEMA_VERSION",
    "Provenance",
    "DocumentInfo",
    "CatalogRef",
    "ArchiveInfo",
    "DocumentMetadata",
    "to_mapping",
    "from_mapping",
]
