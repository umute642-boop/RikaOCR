# SPDX-License-Identifier: Apache-2.0
"""Tests for Kraken ``.gt.txt`` sidecar export (no Kraken dependency)."""

from pathlib import Path

from rikaocr.data.dataset.sample import LineSample
from rikaocr.data.dataset.splitting import Split
from rikaocr.training.kraken_export import export_gt_sidecars, gt_sidecar_path


def _sample(rel: str, text: str, line: int, split: Split = Split.TRAIN) -> LineSample:
    return LineSample(
        image_path=rel,
        text=text,
        doc_id="d",
        page=0,
        region=0,
        line=line,
        split=split,
    )


def test_sidecar_path_swaps_suffix() -> None:
    assert gt_sidecar_path(Path("a/rika_0007.png")) == Path("a/rika_0007.gt.txt")


def test_writes_sidecar_next_to_image(tmp_path: Path) -> None:
    samples = [_sample("train/lines/a.png", "بسم", 0)]
    written = export_gt_sidecars(samples, tmp_path)

    sidecar = tmp_path / "train" / "lines" / "a.gt.txt"
    assert written == [sidecar]
    assert sidecar.read_text(encoding="utf-8") == "بسم"
    assert not sidecar.read_text(encoding="utf-8").endswith("\n")


def test_split_filter(tmp_path: Path) -> None:
    samples = [
        _sample("train/lines/a.png", "a", 0, Split.TRAIN),
        _sample("test/lines/b.png", "b", 1, Split.TEST),
    ]
    written = export_gt_sidecars(samples, tmp_path, split=Split.TRAIN)

    assert written == [tmp_path / "train" / "lines" / "a.gt.txt"]
    assert not (tmp_path / "test" / "lines" / "b.gt.txt").exists()
