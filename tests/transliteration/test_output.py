# SPDX-License-Identifier: Apache-2.0
"""Tests for transliteration output helpers."""

import json
from pathlib import Path

from rikaocr.transliteration.document import (
    DocumentTransliteration,
    LineTransliteration,
)
from rikaocr.transliteration.output import (
    transliteration_to_json,
    transliteration_to_text,
    write_transliteration_json,
    write_transliteration_text,
)


def _result() -> DocumentTransliteration:
    return DocumentTransliteration(
        doc_id="doc-1",
        lines=(
            LineTransliteration(
                page_id="p1",
                region_reading_index=0,
                line_reading_index=0,
                source_text="آباران",
                transliteration="Abaran",
            ),
        ),
    )


def test_transliteration_to_text() -> None:
    assert transliteration_to_text(_result()) == "Abaran"


def test_transliteration_to_json_preserves_source_and_latin() -> None:
    data = json.loads(transliteration_to_json(_result()))
    assert data["doc_id"] == "doc-1"
    assert data["lines"][0]["source_text"] == "آباران"
    assert data["lines"][0]["transliteration"] == "Abaran"


def test_write_transliteration_outputs(tmp_path: Path) -> None:
    text_path = tmp_path / "out.txt"
    json_path = tmp_path / "out.json"

    write_transliteration_text(_result(), text_path)
    write_transliteration_json(_result(), json_path)

    assert text_path.read_text(encoding="utf-8") == "Abaran"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["lines"][0]["source_text"] == "آباران"
