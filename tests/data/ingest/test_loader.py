# SPDX-License-Identifier: Apache-2.0
"""Tests for the ingest loader and deduplication."""

from pathlib import Path

import pytest

from rikaocr.data.ingest.loader import deduplicate, ingest_source
from rikaocr.data.metadata.rights import RightsStatus
from rikaocr.data.metadata.schema import Provenance


@pytest.fixture
def sample_provenance() -> Provenance:
    return Provenance(
        source="BOA_Test_Collection",
        accessed_at="2026-06-30",
        rights_status=RightsStatus.CLEARED,
    )


def test_ingest_source(tmp_path: Path, sample_provenance: Provenance) -> None:
    content = b"dummy image content for ingest"
    test_file = tmp_path / "test_document.jpg"
    test_file.write_bytes(content)

    record = ingest_source(test_file, provenance=sample_provenance)

    assert record.path == str(test_file)
    assert record.size_bytes == len(content)
    assert isinstance(record.sha256, str)
    assert len(record.sha256) == 64
    assert len(record.source_id) == 32  # UUID4 hex length
    assert record.provenance == sample_provenance


def test_deduplicate(tmp_path: Path, sample_provenance: Provenance) -> None:
    file1 = tmp_path / "doc1.txt"
    file2 = tmp_path / "doc2.txt"
    file3 = tmp_path / "doc3.txt"
    file1.write_bytes(b"identical content")
    file2.write_bytes(b"identical content")
    file3.write_bytes(b"different content")

    rec1 = ingest_source(file1, provenance=sample_provenance)
    rec2 = ingest_source(file2, provenance=sample_provenance)
    rec3 = ingest_source(file3, provenance=sample_provenance)

    kept, duplicates = deduplicate([rec1, rec2, rec3])

    assert len(kept) == 2
    assert len(duplicates) == 1
    assert duplicates[0] == rec2
