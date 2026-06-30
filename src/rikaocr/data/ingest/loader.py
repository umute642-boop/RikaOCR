# SPDX-License-Identifier: Apache-2.0
"""Register opaque source files as ``SourceRecord``s (hash + size + provenance).

Sources are treated as opaque bytes here (no image decoding); pixel-level work is
deferred to later milestones. Each ingested file gets a fresh UUID id, its
content SHA-256, byte size, and the supplied provenance.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from rikaocr.common.types import PathLike
from rikaocr.data.ingest.hashing import byte_size, sha256_file
from rikaocr.data.metadata.schema import Provenance


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """An ingested source file with its content hash, size, and provenance."""

    source_id: str
    path: str
    sha256: str
    size_bytes: int
    provenance: Provenance


def ingest_source(path: PathLike, *, provenance: Provenance) -> SourceRecord:
    """Hash and measure a file, returning a ``SourceRecord`` with a fresh id."""
    path_str = str(path)
    return SourceRecord(
        source_id=uuid.uuid4().hex,
        path=path_str,
        sha256=sha256_file(path_str),
        size_bytes=byte_size(path_str),
        provenance=provenance,
    )


def deduplicate(
    records: list[SourceRecord],
) -> tuple[list[SourceRecord], list[SourceRecord]]:
    """Split records by content hash into ``(kept, duplicates)``, keeping first seen."""
    seen: set[str] = set()
    kept: list[SourceRecord] = []
    duplicates: list[SourceRecord] = []
    for record in records:
        if record.sha256 in seen:
            duplicates.append(record)
        else:
            seen.add(record.sha256)
            kept.append(record)
    return kept, duplicates


__all__ = ["SourceRecord", "ingest_source", "deduplicate"]
