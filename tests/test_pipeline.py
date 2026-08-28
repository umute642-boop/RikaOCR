# SPDX-License-Identifier: Apache-2.0
"""End-to-end tests for the recognition Pipeline with dependency-free engines."""

from PIL import Image
from rikaocr.layout.dummy import DummySegmenter
from rikaocr.pipeline import Pipeline
from rikaocr.recognition.dummy import DummyRecognizer


def _image(width: int = 90, height: int = 30) -> Image.Image:
    return Image.new("RGB", (width, height), (255, 255, 255))


def test_pipeline_fills_every_line_with_text() -> None:
    pipeline = Pipeline(
        segmenter=DummySegmenter(num_lines=3),
        recognizer=DummyRecognizer(text="بسم", confidence=0.8),
    )
    document = pipeline.run(_image(), doc_id="d", page_id="p")

    document.validate()
    page = document.pages[0]
    assert (page.width, page.height) == (90, 30)
    lines = page.regions[0].lines
    assert len(lines) == 3
    assert [line.reading_index for line in lines] == [0, 1, 2]
    assert all(line.text == "بسم" for line in lines)
    assert all(line.confidence == 0.8 for line in lines)


def test_pipeline_returns_single_page_document() -> None:
    pipeline = Pipeline(segmenter=DummySegmenter(), recognizer=DummyRecognizer(text="x"))
    document = pipeline.run(_image(), doc_id="doc1", page_id="page1", image_ref="page1.png")

    assert document.doc_id == "doc1"
    assert len(document.pages) == 1
    assert document.pages[0].image_ref == "page1.png"
