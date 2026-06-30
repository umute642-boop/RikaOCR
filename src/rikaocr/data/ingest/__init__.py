# SPDX-License-Identifier: Apache-2.0
"""Ingest layer: register source documents with provenance and content hashes."""

from rikaocr.data.ingest.hashing import byte_size, sha256_file
from rikaocr.data.ingest.loader import SourceRecord, deduplicate, ingest_source
from rikaocr.data.ingest.manifest import read_manifest, write_manifest

__all__ = [
    "SourceRecord",
    "byte_size",
    "deduplicate",
    "ingest_source",
    "read_manifest",
    "sha256_file",
    "write_manifest",
]
