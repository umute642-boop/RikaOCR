# SPDX-License-Identifier: Apache-2.0
"""Immutable geometry value objects for the document model.

These objects describe *where* something is on a page. They are frozen (and thus
hashable) because a coordinate's identity must never change once created; the
mutable document entities (Line, Region, ...) reference them.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from rikaocr.common.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class Point:
    """A 2D pixel coordinate with non-negative integer components."""

    x: int
    y: int

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0:
            raise ValidationError(f"Point coordinates must be non-negative: {self!r}")


@dataclass(frozen=True, slots=True)
class BBox:
    """An axis-aligned bounding box in pixel coordinates."""

    x_min: int
    y_min: int
    x_max: int
    y_max: int

    def __post_init__(self) -> None:
        if self.x_min < 0 or self.y_min < 0:
            raise ValidationError(f"BBox coordinates must be non-negative: {self!r}")
        if self.x_max < self.x_min or self.y_max < self.y_min:
            raise ValidationError(f"BBox max must be >= min: {self!r}")

    @property
    def width(self) -> int:
        """Horizontal extent of the box in pixels."""
        return self.x_max - self.x_min

    @property
    def height(self) -> int:
        """Vertical extent of the box in pixels."""
        return self.y_max - self.y_min

    @property
    def area(self) -> int:
        """Area of the box in square pixels."""
        return self.width * self.height

    def contains(self, other: BBox) -> bool:
        """Return ``True`` if ``other`` lies fully within this box."""
        return (
            self.x_min <= other.x_min
            and self.y_min <= other.y_min
            and self.x_max >= other.x_max
            and self.y_max >= other.y_max
        )

    @classmethod
    def from_points(cls, points: Sequence[Point]) -> BBox:
        """Build the tight bounding box around a non-empty set of points."""
        if not points:
            raise ValidationError("Cannot build a BBox from an empty point set.")
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return cls(min(xs), min(ys), max(xs), max(ys))


@dataclass(frozen=True, slots=True)
class Polygon:
    """A closed polygon defined by at least three points."""

    points: tuple[Point, ...]

    def __post_init__(self) -> None:
        if len(self.points) < 3:
            raise ValidationError(f"Polygon requires at least 3 points, got {len(self.points)}.")

    def bounding_box(self) -> BBox:
        """Return the axis-aligned bounding box enclosing the polygon."""
        return BBox.from_points(self.points)


@dataclass(frozen=True, slots=True)
class Baseline:
    """A polyline baseline defined by at least two points.

    A baseline is the notional line a scribe writes on; in HTR it anchors a text
    line independently of its full polygon.
    """

    points: tuple[Point, ...]

    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValidationError(f"Baseline requires at least 2 points, got {len(self.points)}.")


__all__ = ["Point", "BBox", "Polygon", "Baseline"]
