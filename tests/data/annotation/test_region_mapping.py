# SPDX-License-Identifier: Apache-2.0
"""Tests for PAGE region-type mapping."""

import pytest

from rikaocr.core.document.enums import RegionType
from rikaocr.data.annotation.region_mapping import region_type_from_page, region_type_to_page


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("paragraph", RegionType.PARAGRAPH),
        ("heading", RegionType.HEADER),
        ("marginalia", RegionType.MARGINALIA),
        ("table", RegionType.TABLE),
        ("stamp", RegionType.SEAL),
    ],
)
def test_from_page_known_values(value: str, expected: RegionType) -> None:
    assert region_type_from_page(value) == expected


def test_from_page_is_case_insensitive() -> None:
    assert region_type_from_page("Paragraph") == RegionType.PARAGRAPH


def test_unknown_value_is_other() -> None:
    assert region_type_from_page("totally-unknown") == RegionType.OTHER


def test_none_value_is_other() -> None:
    assert region_type_from_page(None) == RegionType.OTHER


@pytest.mark.parametrize("region_type", list(RegionType))
def test_region_type_round_trip(region_type: RegionType) -> None:
    assert region_type_from_page(region_type_to_page(region_type)) == region_type
