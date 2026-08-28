# SPDX-License-Identifier: Apache-2.0
"""Tests for the Kraken segmentation adapter.

The whole module is skipped unless the optional ``[train]`` extra (Kraken) is
installed; the Kraken-dependent ``segment`` path is exercised with a mocked
``blla.segment`` so no trained model is required.
"""

import pytest

pytest.importorskip("kraken")

from types import SimpleNamespace  # noqa: E402

from PIL import Image  # noqa: E402
from rikaocr.core.document.enums import RegionType  # noqa: E402
from rikaocr.layout.base import segment_document  # noqa: E402
from rikaocr.layout.kraken_segmenter import (  # noqa: E402
    KrakenSegmenter,
    map_kraken_segmentation,
)


def _kraken_line(
    baseline: list[tuple[int, int]], boundary: list[tuple[int, int]]
) -> SimpleNamespace:
    return SimpleNamespace(baseline=baseline, boundary=boundary)


def test_maps_lines_into_single_paragraph_region() -> None:
    segmentation = SimpleNamespace(
        lines=[
            _kraken_line([(10, 5), (40, 5)], [(10, 0), (40, 0), (40, 10), (10, 10)]),
            _kraken_line([(10, 25), (40, 25)], [(10, 20), (40, 20), (40, 30), (10, 30)]),
        ],
        regions={},
    )

    result = map_kraken_segmentation(segmentation)

    assert len(result.regions) == 1
    region = result.regions[0]
    assert region.region_type is RegionType.PARAGRAPH
    assert len(region.lines) == 2
    assert region.lines[0].baseline is not None
    assert region.lines[0].polygon is not None
    assert region.lines[0].polygon.bounding_box().y_min == 0
    assert all(line.text == "" for line in region.lines)


def test_segment_document_applies_rtl_reading_order(monkeypatch: pytest.MonkeyPatch) -> None:
    from kraken import blla

    # Kraken returns the bottom line first; reading order must reorder it last.
    segmentation = SimpleNamespace(
        lines=[
            _kraken_line([(10, 25), (40, 25)], [(10, 20), (40, 20), (40, 30), (10, 30)]),
            _kraken_line([(10, 5), (40, 5)], [(10, 0), (40, 0), (40, 10), (10, 10)]),
        ],
        regions={},
    )
    monkeypatch.setattr(blla, "segment", lambda *args, **kwargs: segmentation)

    image = Image.new("RGB", (50, 30), (255, 255, 255))
    document = segment_document(image, KrakenSegmenter(), doc_id="d", page_id="p")

    document.validate()
    lines = document.pages[0].regions[0].lines
    assert lines[0].polygon.bounding_box().y_min == 0  # top line reads first
    assert [line.reading_index for line in lines] == [0, 1]
