# SPDX-License-Identifier: Apache-2.0
"""Ingest layer: register source documents with provenance and content hashes."""

from rikaocr.data.ingest.hashing import byte_size, sha256_file

__all__ = ["byte_size", "sha256_file"]
