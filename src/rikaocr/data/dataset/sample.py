# SPDX-License-Identifier: Apache-2.0
"""Line-level training samples and their JSONL manifest.

A ``LineSample`` points at one cropped line image and its transcription, plus
provenance (which document/page/region/line) and the split it belongs to. The
manifest is the map the trainer uses to locate data. Pure stdlib — no image
dependency.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from rikaocr.common.exceptions import DataError
from rikaocr.common.types import PathLike
from rikaocr.data.dataset.splitting import Split


@dataclass(frozen=True, slots=True)
class LineSample:
    """One cropped line image with its transcription, provenance, and split."""

    image_path: str
    text: str
    doc_id: str
    page: int
    region: int
    line: int
    split: Split


def write_line_manifest(samples: Iterable[LineSample], path: PathLike) -> None:
    """Write line samples to ``path`` as JSONL (one sample per line)."""
    with Path(path).open("w", encoding="utf-8") as handle:
        for sample in samples:
            data = {
                "image_path": sample.image_path,
                "text": sample.text,
                "doc_id": sample.doc_id,
                "page": sample.page,
                "region": sample.region,
                "line": sample.line,
                "split": sample.split.value,
            }
            handle.write(json.dumps(data, ensure_ascii=False) + "\n")


def read_line_manifest(path: PathLike) -> list[LineSample]:
    """Read a JSONL line manifest into ``LineSample`` objects.

    Raises:
        DataError: if an entry is missing a field or has an invalid value.
    """
    samples: list[LineSample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                data = json.loads(stripped)
                samples.append(
                    LineSample(
                        image_path=data["image_path"],
                        text=data["text"],
                        doc_id=data["doc_id"],
                        page=int(data["page"]),
                        region=int(data["region"]),
                        line=int(data["line"]),
                        split=Split(data["split"]),
                    )
                )
            except (KeyError, ValueError) as exc:
                raise DataError(f"Malformed line manifest entry: {exc}") from exc
    return samples


__all__ = ["LineSample", "write_line_manifest", "read_line_manifest"]
