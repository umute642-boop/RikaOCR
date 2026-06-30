# SPDX-License-Identifier: Apache-2.0
"""Shared type aliases and identifier types for RikaOCR.

These aliases give domain identifiers a distinct static type without any runtime
cost, helping prevent accidental mixing of, for example, a document id and a
page id.
"""

from __future__ import annotations

import os
from typing import NewType

DocId = NewType("DocId", str)
"""Stable identifier for a :class:`~rikaocr.core.document.models.Document`."""

PageId = NewType("PageId", str)
"""Stable identifier for a page within a document."""

PathLike = str | os.PathLike[str]
"""A filesystem path accepted as either a string or an ``os.PathLike``."""

__all__ = ["DocId", "PageId", "PathLike"]
