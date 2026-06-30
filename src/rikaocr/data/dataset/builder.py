# SPDX-License-Identifier: Apache-2.0
"""End-to-end dataset builder: labeled documents -> split line-image dataset.

Splits documents (document-level, deterministic), crops each croppable line from
its page image, optionally augments the *training* split, and writes the line
images, per-split JSONL manifests, and a summary datasheet under
``<output_dir>/<version>/``. Requires the optional ``[data]`` extra.
"""

from __future__ import annotations

import datetime as dt
import zlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from rikaocr.common.logging import get_logger
from rikaocr.common.types import PathLike
from rikaocr.core.document.models import Document, Page
from rikaocr.data.augmentation.pipeline import AugmentationPipeline
from rikaocr.data.dataset.cropping import crop_line
from rikaocr.data.dataset.image_io import save_image
from rikaocr.data.dataset.sample import LineSample, write_line_manifest
from rikaocr.data.dataset.splitting import Split, assign_split

_logger = get_logger(__name__)

# A callable that returns the page image for a document/page, or None if missing.
ImageLoader = Callable[[Document, Page], "Image.Image | None"]


@dataclass(frozen=True, slots=True)
class DatasetReport:
    """Summary of a dataset build."""

    version: str
    output_dir: str
    line_counts: dict[Split, int]
    skipped_lines: int

    @property
    def total_lines(self) -> int:
        """Total number of line samples written across all splits."""
        return sum(self.line_counts.values())


def build_dataset(
    documents: Sequence[Document],
    image_loader: ImageLoader,
    output_dir: PathLike,
    *,
    version: str,
    mask_polygon: bool = False,
    augment: AugmentationPipeline | None = None,
    train: float = 0.8,
    val: float = 0.1,
) -> DatasetReport:
    """Build a split line-image dataset and return a summary report."""
    base = Path(output_dir) / version
    for split in Split:
        (base / split.value / "lines").mkdir(parents=True, exist_ok=True)
    (base / "manifests").mkdir(parents=True, exist_ok=True)

    samples: dict[Split, list[LineSample]] = {split: [] for split in Split}
    skipped = 0

    for document in documents:
        split = assign_split(document.doc_id, train=train, val=val)
        for page_index, page in enumerate(document.pages):
            page_image = image_loader(document, page)
            if page_image is None:
                _logger.warning("No image for %r page %d; skipping.", document.doc_id, page_index)
                continue
            for region_index, region in enumerate(page.iter_in_reading_order()):
                for line_index, line in enumerate(region.iter_in_reading_order()):
                    cropped = crop_line(page_image, line, mask_polygon=mask_polygon)
                    if cropped is None:
                        skipped += 1
                        continue
                    filename = f"{document.doc_id}_p{page_index}_r{region_index}_l{line_index}.png"
                    if split is Split.TRAIN and augment is not None:
                        cropped = augment.apply(cropped, seed=zlib.crc32(filename.encode("utf-8")))
                    save_image(cropped, base / split.value / "lines" / filename)
                    samples[split].append(
                        LineSample(
                            image_path=f"{split.value}/lines/{filename}",
                            text=line.text,
                            doc_id=document.doc_id,
                            page=page_index,
                            region=region_index,
                            line=line_index,
                            split=split,
                        )
                    )

    for split in Split:
        write_line_manifest(samples[split], base / "manifests" / f"{split.value}.jsonl")
    _write_datasheet(base, version, samples, skipped, augment is not None)

    return DatasetReport(
        version=version,
        output_dir=str(base),
        line_counts={split: len(samples[split]) for split in Split},
        skipped_lines=skipped,
    )


def _write_datasheet(
    base: Path,
    version: str,
    samples: dict[Split, list[LineSample]],
    skipped: int,
    augmented: bool,
) -> None:
    total = sum(len(items) for items in samples.values())
    lines = [
        f"# Dataset {version}",
        "",
        f"- Built: {dt.date.today().isoformat()}",
        f"- Augmentation (train only): {'on' if augmented else 'off'}",
        f"- Skipped lines (no geometry / empty crop): {skipped}",
        "",
        "## Line counts",
        "",
    ]
    lines.extend(f"- {split.value}: {len(samples[split])}" for split in Split)
    lines.extend(["", f"Total lines: {total}"])
    (base / "datasheet.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


__all__ = ["DatasetReport", "ImageLoader", "build_dataset"]
