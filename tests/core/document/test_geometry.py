# SPDX-License-Identifier: Apache-2.0
"""Tests for immutable geometry value objects."""

from dataclasses import FrozenInstanceError

import pytest

from rikaocr.common.exceptions import ValidationError
from rikaocr.core.document.geometry import Baseline, BBox, Point, Polygon


def test_point_valid() -> None:
    point = Point(3, 4)
    assert point.x == 3
    assert point.y == 4


def test_point_negative_raises() -> None:
    with pytest.raises(ValidationError):
        Point(-1, 0)


def test_point_is_frozen() -> None:
    point = Point(1, 1)
    with pytest.raises(FrozenInstanceError):
        point.x = 2  # type: ignore[misc]


def test_bbox_dimensions() -> None:
    box = BBox(0, 0, 10, 5)
    assert box.width == 10
    assert box.height == 5
    assert box.area == 50


def test_bbox_invalid_raises() -> None:
    with pytest.raises(ValidationError):
        BBox(10, 0, 0, 5)


def test_bbox_contains() -> None:
    outer = BBox(0, 0, 10, 10)
    inner = BBox(2, 2, 5, 5)
    assert outer.contains(inner)
    assert not inner.contains(outer)


def test_bbox_from_points() -> None:
    points = [Point(2, 3), Point(8, 1), Point(5, 9)]
    assert BBox.from_points(points) == BBox(2, 1, 8, 9)


def test_bbox_from_empty_points_raises() -> None:
    with pytest.raises(ValidationError):
        BBox.from_points([])


def test_polygon_requires_three_points() -> None:
    with pytest.raises(ValidationError):
        Polygon((Point(0, 0), Point(1, 1)))


def test_polygon_bounding_box() -> None:
    polygon = Polygon((Point(0, 0), Point(4, 0), Point(4, 3), Point(0, 3)))
    assert polygon.bounding_box() == BBox(0, 0, 4, 3)


def test_baseline_requires_two_points() -> None:
    with pytest.raises(ValidationError):
        Baseline((Point(0, 0),))


def test_baseline_valid() -> None:
    baseline = Baseline((Point(0, 5), Point(10, 5)))
    assert len(baseline.points) == 2
