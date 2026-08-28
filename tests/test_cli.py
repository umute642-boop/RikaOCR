# SPDX-License-Identifier: Apache-2.0
"""Tests for the rikaocr CLI (dummy engine; no ML inference)."""

from pathlib import Path

import pytest
from PIL import Image
from rikaocr.cli import build_pipeline, main
from rikaocr.data.annotation.page_xml import PageXmlCodec
from rikaocr.pipeline import Pipeline


def _write_image(path: Path, width: int = 80, height: int = 30) -> None:
    Image.new("RGB", (width, height), (255, 255, 255)).save(path)


def test_build_pipeline_dummy_needs_no_kraken() -> None:
    assert isinstance(build_pipeline("dummy"), Pipeline)


def test_build_pipeline_rejects_unknown_engine() -> None:
    with pytest.raises(ValueError):
        build_pipeline("nope")


def test_kraken_engine_requires_rec_model() -> None:
    # The None check precedes the lazy kraken import, so this needs no kraken.
    with pytest.raises(ValueError, match="rec-model"):
        build_pipeline("kraken")


def test_cli_writes_page_xml(tmp_path: Path) -> None:
    image = tmp_path / "rika.png"
    _write_image(image)
    output = tmp_path / "out.xml"

    exit_code = main([str(image), "-o", str(output), "--num-lines", "2"])

    assert exit_code == 0
    document = PageXmlCodec().load(output)
    document.validate()
    assert document.pages[0].image_ref == "rika.png"
    assert len(document.pages[0].regions[0].lines) == 2


def test_cli_writes_plain_text(tmp_path: Path) -> None:
    image = tmp_path / "rika.png"
    _write_image(image)
    output = tmp_path / "out.txt"

    exit_code = main([str(image), "-o", str(output), "--format", "text", "--num-lines", "2"])

    assert exit_code == 0
    # Dummy recognizer yields empty strings: two empty lines joined by newline.
    assert output.read_text(encoding="utf-8") == "\n"
