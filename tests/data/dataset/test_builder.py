# SPDX-License-Identifier: Apache-2.0
"""End-to-end tests for the dataset builder (synthetic pages, tmp_path)."""

from pathlib import Path

from PIL import Image

from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.geometry import Point, Polygon
from rikaocr.core.document.models import Document, Line, Page, Region
from rikaocr.data.augmentation.pipeline import AugmentationPipeline
from rikaocr.data.augmentation.transforms import Brightness, GaussianNoise
from rikaocr.data.dataset.builder import build_dataset
from rikaocr.data.dataset.sample import read_line_manifest
from rikaocr.data.dataset.splitting import Split, assign_split


def _rect(x0: int, y0: int, x1: int, y1: int) -> Polygon:
    return Polygon((Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1)))


def _document(doc_id: str, line: Line) -> Document:
    region = Region(region_type=RegionType.PARAGRAPH, lines=[line])
    return Document(doc_id=doc_id, pages=[Page(page_id="p", image_ref="p.png", regions=[region])])


def _loader(document: Document, page: Page) -> Image.Image:
    return Image.new("RGB", (200, 60), (255, 255, 255))


def _first_doc_for(split: Split) -> str:
    index = 0
    while True:
        candidate = f"doc-{index}"
        if assign_split(candidate) == split:
            return candidate
        index += 1


def test_build_dataset_end_to_end(tmp_path: Path) -> None:
    croppable = [
        _document(f"doc-{index}", Line(text=f"line-{index}", polygon=_rect(0, 0, 50, 20)))
        for index in range(6)
    ]
    documents = [*croppable, _document("doc-nogeo", Line(text="skip"))]

    report = build_dataset(documents, _loader, tmp_path, version="v1")
    base = tmp_path / "v1"

    for split in Split:
        assert (base / split.value / "lines").is_dir()
        assert (base / "manifests" / f"{split.value}.jsonl").exists()
    assert (base / "datasheet.md").exists()

    assert report.total_lines == 6
    assert report.skipped_lines == 1

    samples = []
    for split in Split:
        samples.extend(read_line_manifest(base / "manifests" / f"{split.value}.jsonl"))
    assert len(samples) == 6
    assert {sample.doc_id for sample in samples} == {f"doc-{index}" for index in range(6)}
    for sample in samples:
        assert (base / sample.image_path).exists()

    assert "Total lines: 6" in (base / "datasheet.md").read_text(encoding="utf-8")


def test_augmentation_only_affects_train(tmp_path: Path) -> None:
    train_id = _first_doc_for(Split.TRAIN)
    val_id = _first_doc_for(Split.VAL)
    documents = [
        _document(train_id, Line(text="t", polygon=_rect(0, 0, 50, 20))),
        _document(val_id, Line(text="v", polygon=_rect(0, 0, 50, 20))),
    ]
    pipeline = AugmentationPipeline([Brightness(0.4, 1.6), GaussianNoise(25.0)])

    build_dataset(documents, _loader, tmp_path / "plain", version="v")
    build_dataset(documents, _loader, tmp_path / "aug", version="v", augment=pipeline)

    plain = tmp_path / "plain" / "v"
    augmented = tmp_path / "aug" / "v"
    train_rel = f"train/lines/{train_id}_p0_r0_l0.png"
    val_rel = f"val/lines/{val_id}_p0_r0_l0.png"

    with Image.open(plain / train_rel) as a, Image.open(augmented / train_rel) as b:
        assert a.tobytes() != b.tobytes()  # train was augmented
    with Image.open(plain / val_rel) as a, Image.open(augmented / val_rel) as b:
        assert a.tobytes() == b.tobytes()  # val left untouched
