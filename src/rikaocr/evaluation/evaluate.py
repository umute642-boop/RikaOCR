# SPDX-License-Identifier: Apache-2.0
"""End-to-end evaluation loop: recognise line samples and score CER/WER.

Given a :class:`~rikaocr.recognition.base.Recognizer` and a list of
:class:`~rikaocr.data.dataset.sample.LineSample`, each sample's image is loaded
and recognised, then predictions are scored against the gold transcriptions
using micro-averaged CER/WER (see :mod:`rikaocr.evaluation.metrics`).

Requires the optional ``[data]`` extra (Pillow) for image loading.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from rikaocr.common.types import PathLike
from rikaocr.data.dataset.image_io import load_image
from rikaocr.data.dataset.sample import LineSample
from rikaocr.evaluation.metrics import aggregate_cer, aggregate_wer
from rikaocr.recognition.base import Recognizer
from rikaocr.training.tracking import Tracker


@dataclass(frozen=True, slots=True)
class EvalReport:
    """Aggregate evaluation result over a set of line samples."""

    cer: float
    wer: float
    num_samples: int


def evaluate(
    recognizer: Recognizer,
    samples: Sequence[LineSample],
    image_root: PathLike,
    *,
    tracker: Tracker | None = None,
) -> EvalReport:
    """Run ``recognizer`` over ``samples`` and return micro-averaged CER/WER.

    Each sample's ``image_path`` is resolved relative to ``image_root``. If a
    ``tracker`` is given, the resulting metrics are logged within its run.
    """
    root = Path(image_root)
    pairs: list[tuple[str, str]] = []
    for sample in samples:
        image = load_image(root / sample.image_path)
        prediction = recognizer.recognize(image).text
        pairs.append((prediction, sample.text))

    report = EvalReport(
        cer=aggregate_cer(pairs),
        wer=aggregate_wer(pairs),
        num_samples=len(pairs),
    )

    if tracker is not None:
        with tracker:
            tracker.log_metrics({"cer": report.cer, "wer": report.wer})

    return report


__all__ = ["EvalReport", "evaluate"]
