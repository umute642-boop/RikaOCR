# SPDX-License-Identifier: Apache-2.0
"""Tests for CLI line-image mode."""

from pathlib import Path

from PIL import Image

import rikaocr.cli as cli
from rikaocr.transliteration.base import TransliterationResult


class FakeRecognitionResult:
    text = "حضور سامم حضرت صدارتپاهیه"
    confidence = 0.91


class FakeRecognizer:
    def recognize(self, image):
        return FakeRecognitionResult()


class FakeTransliterator:
    def transliterate(self, text: str) -> TransliterationResult:
        return TransliterationResult(text="Hazzur Samim Hazrat Sadartepahya")


def test_cli_line_image_skips_segmentation_and_writes_outputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    image = tmp_path / "line.png"
    Image.new("RGB", (312, 53), (255, 255, 255)).save(image)

    ocr_output = tmp_path / "ocr.txt"
    translit_output = tmp_path / "translit.txt"

    def fake_recognize_line_image(
        image,
        *,
        engine,
        rec_model,
        doc_id,
        page_id,
        image_ref=None,
    ):
        from rikaocr.core.document.enums import RegionType
        from rikaocr.core.document.models import Document, Line, Page, Region

        result = FakeRecognizer().recognize(image)
        return Document(
            doc_id=doc_id,
            pages=[
                Page(
                    page_id=page_id,
                    image_ref=image_ref,
                    regions=[
                        Region(
                            region_type=RegionType.PARAGRAPH,
                            lines=[
                                Line(
                                    text=result.text,
                                    confidence=result.confidence,
                                )
                            ],
                        )
                    ],
                )
            ],
        )

    monkeypatch.setattr(
        cli,
        "recognize_line_image",
        fake_recognize_line_image,
    )
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
            "--engine",
            "kraken",
            "--line-image",
            "--rec-model",
            "fake-model",
            "--transliterate",
            "--translit-model",
            "fake-byt5",
            "--translit-output",
            str(translit_output),
            "--translit-format",
            "text",
            "--translit-mode",
            "word",
        ]
    )

    assert exit_code == 0
    assert ocr_output.read_text(encoding="utf-8") == "حضور سامم حضرت صدارتپاهیه"
    assert translit_output.read_text(encoding="utf-8") == (
        "Hazzur Samim Hazrat Sadartepahya"
    )
