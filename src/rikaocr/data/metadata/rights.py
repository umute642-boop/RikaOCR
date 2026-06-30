# SPDX-License-Identifier: Apache-2.0
"""Distribution-rights status for ingested sources.

The data licence is undecided (ADR-014). Until a source is explicitly cleared,
derived data must not be treated as distributable. ``require_distributable``
enforces this gate.
"""

from __future__ import annotations

from enum import StrEnum

from rikaocr.common.exceptions import DataError


class RightsStatus(StrEnum):
    """Whether a source is cleared for redistribution."""

    UNKNOWN = "unknown"
    RESTRICTED = "restricted"
    CLEARED = "cleared"


def require_distributable(rights_status: RightsStatus) -> None:
    """Raise :class:`DataError` unless the source is cleared for distribution."""
    if rights_status is not RightsStatus.CLEARED:
        raise DataError(f"Source is not cleared for distribution: {rights_status.value!r}.")


__all__ = ["RightsStatus", "require_distributable"]
