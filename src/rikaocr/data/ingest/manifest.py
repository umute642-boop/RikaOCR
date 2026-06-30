# SPDX-License-Identifier: Apache-2.0
"""Ingest manifest in JSON Lines (JSONL) format.

JSONL lets us append and stream large ingest catalogues line by line without
loading the whole file into memory. Each line is one ``SourceRecord``.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from rikaocr.common.types import PathLike
from rikaocr.data.ingest.loader import SourceRecord
from rikaocr.data.metadata.rights import RightsStatus
from rikaocr.data.metadata.schema import Provenance


def write_manifest(records: Iterable[SourceRecord], path: PathLike) -> None:
    """Write source records to ``path`` as JSONL (one record per line)."""
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in records:
            data = {
                "source_id": record.source_id,
                "path": record.path,
                "sha256": record.sha256,
                "size_bytes": record.size_bytes,
                "provenance": {
                    "source": record.provenance.source,
                    "accessed_at": record.provenance.accessed_at,
                    "rights_status": record.provenance.rights_status.value,
                    "notes": record.provenance.notes,
                },
            }
            handle.write(json.dumps(data, ensure_ascii=False) + "\n")


def read_manifest(path: PathLike) -> list[SourceRecord]:
    """Read a JSONL manifest and return the list of source records."""
    records: list[SourceRecord] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            data = json.loads(stripped)
            prov_data = data["provenance"]
            provenance = Provenance(
                source=prov_data["source"],
                accessed_at=prov_data["accessed_at"],
                rights_status=RightsStatus(prov_data["rights_status"]),
                notes=prov_data.get("notes"),
            )
            records.append(
                SourceRecord(
                    source_id=data["source_id"],
                    path=data["path"],
                    sha256=data["sha256"],
                    size_bytes=data["size_bytes"],
                    provenance=provenance,
                )
            )
    return records


__all__ = ["write_manifest", "read_manifest"]
