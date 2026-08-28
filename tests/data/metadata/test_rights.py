# SPDX-License-Identifier: Apache-2.0
"""Tests for the distribution-rights gate."""

import pytest
from rikaocr.common.exceptions import DataError
from rikaocr.data.metadata.rights import RightsStatus, require_distributable


def test_cleared_is_distributable() -> None:
    require_distributable(RightsStatus.CLEARED)


@pytest.mark.parametrize("status", [RightsStatus.UNKNOWN, RightsStatus.RESTRICTED])
def test_non_cleared_raises(status: RightsStatus) -> None:
    with pytest.raises(DataError):
        require_distributable(status)
