# SPDX-License-Identifier: Apache-2.0
"""Metadata layer: provenance, document info, catalogue, and rights."""

from rikaocr.data.metadata.binding import attach, extract
from rikaocr.data.metadata.rights import RightsStatus, require_distributable
from rikaocr.data.metadata.schema import (
    ArchiveInfo,
    CatalogRef,
    DocumentInfo,
    DocumentMetadata,
    Provenance,
    from_mapping,
    to_mapping,
)

__all__ = [
    "ArchiveInfo",
    "CatalogRef",
    "DocumentInfo",
    "DocumentMetadata",
    "Provenance",
    "RightsStatus",
    "attach",
    "extract",
    "from_mapping",
    "require_distributable",
    "to_mapping",
]
