# SPDX-License-Identifier: Apache-2.0
"""Tests for the pipeline output bridge (PAGE-XML + plain text)."""

from pathlib import Path

from PIL import Image

from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.models import Document, Line, Page, Region
from rikaocr.data.annotation.page_xml import PageXmlCodec
from rikaocr.layout.dummy import DummySegmenter
from rikaocr.output import document_to_text, write_page_xml, write_text
from rikaocr.pipeline import Pipeline
from rikaocr.recognition.dummy import DummyRecognizer


def _pipeline_document() -> Document:
    pipeline = Pipeline(
        segmenter=DummySegmenter(num_lines=2),
        recognizer=DummyRecognizer(text="بسم", confidence=0.7),
    )
    image = Image.new("RGB", (80, 20), (255, 255, 255))
    # page_id == image_ref keeps the document in the codec's canonical form.
    return pipeline.run(image, doc_id="rika001", page_id="rika001.png", image_ref="rika001.png")


def test_write_page_xml_round_trips_pipeline_output(tmp_path: Path) -> None:
    document = _pipeline_document()
    path = tmp_path / "out.xml"
    write_page_xml(document, path)

    reloaded = PageXmlCodec().load(path)
    reloaded.validate()
    original_lines = document.pages[0].regions[0].lines
    reloaded_lines = reloaded.pages[0].regions[0].lines
    assert [line.text for line in reloaded_lines] == [line.text for line in original_lines]
    assert [line.confidence for line in reloaded_lines] == [0.7, 0.7]
    assert [line.reading_index for line in reloaded_lines] == [0, 1]


def test_document_to_text_joins_lines_in_reading_order() -> None:
    lines = [Line(text="two", reading_index=1), Line(text="one", reading_index=0)]
    region = Region(region_type=RegionType.PARAGRAPH, lines=lines)
    document = Document(doc_id="d", pages=[Page(page_id="p", regions=[region])])
    assert document_to_text(document) == "one\ntwo"


def test_write_text_writes_utf8(tmp_path: Path) -> None:
    document = _pipeline_document()
    path = tmp_path / "out.txt"
    write_text(document, path)
    assert path.read_text(encoding="utf-8") == "بسم\nبسم"
