# SPDX-License-Identifier: Apache-2.0
"""Tests for the LineSample JSONL manifest (round-trip)."""

from pathlib import Path

import pytest

from rikaocr.common.exceptions import DataError
from rikaocr.data.dataset.sample import (
    LineSample,
    read_line_manifest,
    write_line_manifest,
)
from rikaocr.data.dataset.splitting import Split


def _samples() -> list[LineSample]:
    return [
        LineSample(
            image_path="train/lines/doc1_p0_r0_l0.png",
            text="بسم الله",
            doc_id="doc1",
            page=0,
            region=0,
            line=0,
            split=Split.TRAIN,
        ),
        LineSample(
            image_path="val/lines/doc2_p0_r1_l2.png",
            text="لاچين",
            doc_id="doc2",
            page=0,
            region=1,
            line=2,
            split=Split.VAL,
        ),
    ]


def test_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "lines.jsonl"
    samples = _samples()
    write_line_manifest(samples, target)
    assert target.exists()
    assert read_line_manifest(target) == samples


def test_unicode_preserved(tmp_path: Path) -> None:
    target = tmp_path / "lines.jsonl"
    write_line_manifest(_samples(), target)
    assert "بسم الله" in target.read_text(encoding="utf-8")


def test_empty_lines_are_skipped(tmp_path: Path) -> None:
    target = tmp_path / "lines.jsonl"
    write_line_manifest(_samples(), target)
    with target.open("a", encoding="utf-8") as handle:
        handle.write("\n")
    assert len(read_line_manifest(target)) == 2


def test_malformed_entry_raises(tmp_path: Path) -> None:
    target = tmp_path / "bad.jsonl"
    target.write_text('{"image_path": "x"}\n', encoding="utf-8")
    with pytest.raises(DataError):
        read_line_manifest(target)
