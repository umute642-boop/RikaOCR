# SPDX-License-Identifier: Apache-2.0
"""Kraken baseline segmentation behind the :class:`Segmenter` port (ADR-020).

This adapter wraps Kraken's ``blla`` baseline segmenter. Like the recognition
adapter, Kraken is a heavy, platform-sensitive dependency (trained on Linux/WSL2
with CUDA), so it is imported *lazily* inside the methods that use it: importing
this module never requires the optional ``[train]`` extra, keeping the core and
the test suite engine-agnostic.

The output mapping (:func:`map_kraken_segmentation`) is a pure, Kraken-free
function: it consumes a duck-typed Kraken ``Segmentation`` and produces our
motor-neutral :class:`~rikaocr.layout.base.SegmentationResult`. Per M6 scope
(see ADR-020) every line is placed in a single ``PARAGRAPH`` region; richer
region classification is deferred.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from PIL import Image

from rikaocr.common.exceptions import RikaOCRError
from rikaocr.common.types import PathLike
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Baseline, Point, Polygon
from rikaocr.core.document.models import Line, Region
from rikaocr.layout.base import SegmentationResult


def _to_points(raw: Sequence[Sequence[float]] | None) -> tuple[Point, ...]:
    """Convert a sequence of ``(x, y)`` pairs to non-negative integer points."""
    if not raw:
        return ()
    return tuple(Point(max(0, round(x)), max(0, round(y))) for x, y in raw)


def map_kraken_segmentation(segmentation: Any) -> SegmentationResult:
    """Map a Kraken ``Segmentation`` to a :class:`SegmentationResult`.

    Reads each Kraken line's ``baseline`` and ``boundary`` polylines and builds a
    core :class:`Line` (text left empty -- recognition fills it later). All lines
    are collected into one :class:`RegionType.PARAGRAPH` region; reading order is
    assigned downstream by :func:`rikaocr.layout.base.segment_document`.

    Args:
        segmentation: A duck-typed Kraken ``Segmentation`` exposing ``lines``,
            each with ``baseline`` and (optionally) ``boundary`` point lists.

    Returns:
        A single-region segmentation result carrying only line geometry.
    """
    lines: list[Line] = []
    for kraken_line in getattr(segmentation, "lines", []):
        baseline_points = _to_points(getattr(kraken_line, "baseline", None))
        boundary_points = _to_points(getattr(kraken_line, "boundary", None))
        baseline = Baseline(baseline_points) if len(baseline_points) >= 2 else None
        polygon = Polygon(boundary_points) if len(boundary_points) >= 3 else None
        lines.append(Line(text="", baseline=baseline, polygon=polygon))
    region = Region(region_type=RegionType.PARAGRAPH, lines=lines)
    return SegmentationResult(regions=[region])


@dataclass(slots=True)
class KrakenSegmenter:
    """Segments a page with Kraken's ``blla`` baseline model.

    The optional segmentation model is loaded lazily on first use and cached.
    When ``model_path`` is ``None``, Kraken's bundled default model is used.

    Raises:
        RikaOCRError: if instantiated while the optional ``[train]`` extra
            (Kraken) is not installed.
    """

    model_path: PathLike | None = None
    text_direction: str = "horizontal-rl"
    _model: object | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if importlib.util.find_spec("kraken") is None:
            raise RikaOCRError(
                "KrakenSegmenter requires the optional [train] extra (kraken). "
                "Install it with: pip install 'rikaocr[train]'."
            )

    def _load_model(self) -> object | None:
        """Load and cache the baseline model (lazy import of ``kraken``)."""
        if self.model_path is None:
            return None
        if self._model is None:
            from kraken.lib.vgsl import TorchVGSLModel

            self._model = TorchVGSLModel.load_model(str(self.model_path))
        return self._model

    def segment(self, image: Image.Image) -> SegmentationResult:
        """Run Kraken baseline segmentation on ``image`` and map the result."""
        from kraken import blla

        segmentation = blla.segment(
            image.convert("RGB"),
            text_direction=self.text_direction,
            model=self._load_model(),
        )
        return map_kraken_segmentation(segmentation)


__all__ = ["KrakenSegmenter", "map_kraken_segmentation"]
