# SPDX-License-Identifier: Apache-2.0
"""Layout analysis: turn a page image into region/line geometry (ADR-020).

Segmentation produces *where* the text is (regions and lines), not *what* it
says; recognition (:mod:`rikaocr.recognition`) fills in the text afterwards.
Engines are wrapped behind the :class:`~rikaocr.layout.base.Segmenter` port so
the core stays free of heavy dependencies.
"""

from rikaocr.layout.base import (
    SegmentationResult,
    Segmenter,
    order_reading,
    segment_document,
)
from rikaocr.layout.dummy import DummySegmenter

__all__ = [
    "SegmentationResult",
    "Segmenter",
    "order_reading",
    "segment_document",
    "DummySegmenter",
]
