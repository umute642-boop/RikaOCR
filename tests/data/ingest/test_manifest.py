# SPDX-License-Identifier: Apache-2.0
"""Tests for the JSONL ingest manifest (round-trip)."""

from pathlib import Path

from rikaocr.data.ingest.loader import SourceRecord
from rikaocr.data.ingest.manifest import read_manifest, write_manifest
from rikaocr.data.metadata.rights import RightsStatus
from rikaocr.data.metadata.schema import Provenance


def test_manifest_round_trip(tmp_path: Path) -> None:
    manifest_file = tmp_path / "manifest.jsonl"

    prov1 = Provenance(
        source="BOA_Collection_A",
        accessed_at="2026-06-30",
        rights_status=RightsStatus.CLEARED,
    )
    prov2 = Provenance(
        source="Private_Archive",
        accessed_at="2026-06-30",
        rights_status=RightsStatus.RESTRICTED,
        notes="Do not distribute",
    )

    records_in = [
        SourceRecord(
            source_id="id-001",
            path="data/raw/001.jpg",
            sha256="hash-001",
            size_bytes=1024,
            provenance=prov1,
        ),
        SourceRecord(
            source_id="id-002",
            path="data/raw/002.jpg",
            sha256="hash-002",
            size_bytes=2048,
            provenance=prov2,
        ),
    ]

    write_manifest(records_in, manifest_file)
    assert manifest_file.exists()

    records_out = read_manifest(manifest_file)

    assert len(records_out) == 2
    assert records_out[0] == records_in[0]
    assert records_out[1] == records_in[1]
