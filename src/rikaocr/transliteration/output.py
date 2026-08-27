# SPDX-License-Identifier: Apache-2.0
"""Output helpers for document-level transliteration results."""

from __future__ import annotations

import json
from pathlib import Path

from rikaocr.common.types import PathLike
from rikaocr.transliteration.document import DocumentTransliteration


def transliteration_to_text(result: DocumentTransliteration) -> str:
    """Return Latin-script transliteration as plain text."""
    return "\n".join(line.transliteration for line in result.lines)


def transliteration_to_json(
    result: DocumentTransliteration,
    *,
    indent: int | None = 2,
) -> str:
    """Return source OCR and transliteration as JSON."""
    data = {
        "doc_id": result.doc_id,
        "lines": [
            {
                "page_id": line.page_id,
                "region_reading_index": line.region_reading_index,
                "line_reading_index": line.line_reading_index,
                "source_text": line.source_text,
                "transliteration": line.transliteration,
            }
            for line in result.lines
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=indent)


def write_transliteration_text(
    result: DocumentTransliteration,
    path: PathLike,
) -> None:
    """Write Latin-script transliteration to a UTF-8 text file."""
    Path(path).write_text(transliteration_to_text(result), encoding="utf-8")


def write_transliteration_json(
    result: DocumentTransliteration,
    path: PathLike,
) -> None:
    """Write OCR/transliteration pairs to a UTF-8 JSON file."""
    Path(path).write_text(transliteration_to_json(result), encoding="utf-8")


__all__ = [
    "transliteration_to_text",
    "transliteration_to_json",
    "write_transliteration_text",
    "write_transliteration_json",
]
