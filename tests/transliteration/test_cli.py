# SPDX-License-Identifier: Apache-2.0
"""CLI tests for the optional transliteration stage."""

import json
from pathlib import Path

from PIL import Image

import rikaocr.cli as cli
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.models import Document, Line, Page, Region
from rikaocr.transliteration.base import TransliterationResult


class FakePipeline:
    def run(self, image, *, doc_id, page_id, image_ref=None, mask_polygon=False):
        return Document(
            doc_id=doc_id,
            pages=[
                Page(
                    page_id=page_id,
                    image_ref=image_ref,
                    regions=[
                        Region(
                            region_type=RegionType.PARAGRAPH,
                            lines=[Line(text="آباران")],
                        )
                    ],
                )
            ],
        )


class FakeTransliterator:
    def transliterate(self, text: str) -> TransliterationResult:
        assert text == "آباران"
        return TransliterationResult(text="Abaran")


def test_cli_writes_separate_transliteration_json(
    tmp_path: Path,
    monkeypatch,
) -> None:
    image = tmp_path / "rika.png"
    Image.new("RGB", (80, 30), (255, 255, 255)).save(image)

    ocr_output = tmp_path / "ocr.txt"
    translit_output = tmp_path / "translit.json"

    monkeypatch.setattr(cli, "build_pipeline", lambda *args, **kwargs: FakePipeline())
    monkeypatch.setattr(
        cli,
        "build_transliterator",
        lambda *args, **kwargs: FakeTransliterator(),
    )

    exit_code = cli.main(
        [
            str(image),
            "-o",
            str(ocr_output),
            "--format",
            "text",
            "--transliterate",
            "--translit-model",
            "fake-model",
            "--translit-output",
            str(translit_output),
            "--translit-format",
            "json",
        ]
    )

    assert exit_code == 0
    assert ocr_output.read_text(encoding="utf-8") == "آباران"

    data = json.loads(translit_output.read_text(encoding="utf-8"))
    assert data["lines"][0]["source_text"] == "آباران"
    assert data["lines"][0]["transliteration"] == "Abaran"
