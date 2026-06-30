# SPDX-License-Identifier: Apache-2.0
"""Content hashing helpers for ingest (standard library only)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rikaocr.common.types import PathLike

_CHUNK_SIZE = 65536


def sha256_file(path: PathLike) -> str:
    """Return the SHA-256 hex digest of a file's contents."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def byte_size(path: PathLike) -> int:
    """Return the size of a file in bytes."""
    return Path(path).stat().st_size


__all__ = ["sha256_file", "byte_size"]
