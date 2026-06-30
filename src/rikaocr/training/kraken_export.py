# SPDX-License-Identifier: Apache-2.0
"""Export line samples to Kraken's ``.gt.txt`` sidecar format (see ADR-019).

Kraken's ``ketos train`` consumes a directory of line images, each accompanied
by a ground-truth text file with the same base name and a ``.gt.txt`` suffix
(``rika_0007.png`` -> ``rika_0007.gt.txt``). This module writes those sidecars
next to the existing line images. Pure stdlib -- no Kraken or image dependency.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from rikaocr.common.types import PathLike
from rikaocr.data.dataset.sample import LineSample
from rikaocr.data.dataset.splitting import Split


def gt_sidecar_path(image_path: Path) -> Path:
    """Return the ``.gt.txt`` sidecar path for a given line image path."""
    return image_path.with_suffix(".gt.txt")


def export_gt_sidecars(
    samples: Iterable[LineSample],
    image_root: PathLike,
    *,
    split: Split | None = None,
) -> list[Path]:
    """Write a ``.gt.txt`` sidecar next to each sample's image.

    Each sample's ``image_path`` is resolved relative to ``image_root``; the
    transcription is written UTF-8 with no trailing newline. If ``split`` is
    given, only samples in that split are exported.

    Returns:
        The list of sidecar paths written, in input order.
    """
    root = Path(image_root)
    written: list[Path] = []
    for sample in samples:
        if split is not None and sample.split is not split:
            continue
        sidecar = gt_sidecar_path(root / sample.image_path)
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        sidecar.write_text(sample.text, encoding="utf-8")
        written.append(sidecar)
    return written


__all__ = ["gt_sidecar_path", "export_gt_sidecars"]
