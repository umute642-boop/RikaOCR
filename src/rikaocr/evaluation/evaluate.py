# SPDX-License-Identifier: Apache-2.0
"""End-to-end evaluation loop: recognise line samples and score CER/WER.

Given a :class:`~rikaocr.recognition.base.Recognizer` and a list of
:class:`~rikaocr.data.dataset.sample.LineSample`, each sample's image is loaded
and recognised, then predictions are scored against the gold transcriptions
using micro-averaged CER/WER (see :mod:`rikaocr.evaluation.metrics`).

Requires the optional ``[data]`` extra (Pillow) for image loading.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from rikaocr.common.exceptions import DataError
from rikaocr.common.types import PathLike
from rikaocr.core.document.models import Document
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


def _line_texts(document: Document) -> Iterator[str]:
    """Yield every line's text in reading order across all pages."""
    for page in document.pages:
        for region in page.iter_in_reading_order():
            for line in region.iter_in_reading_order():
                yield line.text


def evaluate_document(prediction: Document, reference: Document) -> EvalReport:
    """Score a recognised document against a ground-truth document.

    Line texts are paired in reading order across all pages and scored with
    micro-averaged CER/WER. Both documents must contain the same number of
    lines (the pipeline preserves geometry, so the counts must match).

    Raises:
        DataError: if the prediction and reference have different line counts.
    """
    predicted = list(_line_texts(prediction))
    expected = list(_line_texts(reference))
    if len(predicted) != len(expected):
        raise DataError(
            f"Line count mismatch: prediction has {len(predicted)}, "
            f"reference has {len(expected)}."
        )
    pairs = list(zip(predicted, expected, strict=True))
    return EvalReport(
        cer=aggregate_cer(pairs),
        wer=aggregate_wer(pairs),
        num_samples=len(pairs),
    )


__all__ = ["EvalReport", "evaluate", "evaluate_document"]
