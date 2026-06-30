# SPDX-License-Identifier: Apache-2.0
"""Character- and word-error-rate metrics (pure standard library).

CER and WER are computed from the Levenshtein edit distance between a prediction
and a reference. Aggregate variants use *micro-averaging* (total distance over
total reference length), which is the correct way to combine error rates across
a dataset — not the mean of per-sample rates.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence


def edit_distance(source: Sequence[object], target: Sequence[object]) -> int:
    """Return the Levenshtein edit distance between two sequences."""
    if source == target:
        return 0
    cols = len(target)
    if len(source) == 0:
        return cols
    if cols == 0:
        return len(source)

    previous = list(range(cols + 1))
    for row, source_token in enumerate(source, start=1):
        current = [row, *([0] * cols)]
        for col, target_token in enumerate(target, start=1):
            substitution_cost = 0 if source_token == target_token else 1
            current[col] = min(
                previous[col] + 1,  # deletion
                current[col - 1] + 1,  # insertion
                previous[col - 1] + substitution_cost,  # substitution
            )
        previous = current
    return previous[cols]


def cer(prediction: str, reference: str) -> float:
    """Character Error Rate of ``prediction`` against ``reference``."""
    if not reference:
        return 0.0 if not prediction else 1.0
    return edit_distance(prediction, reference) / len(reference)


def wer(prediction: str, reference: str) -> float:
    """Word Error Rate (whitespace-tokenised) of ``prediction`` vs ``reference``."""
    reference_words = reference.split()
    if not reference_words:
        return 0.0 if not prediction.split() else 1.0
    return edit_distance(prediction.split(), reference_words) / len(reference_words)


def aggregate_cer(pairs: Iterable[tuple[str, str]]) -> float:
    """Micro-averaged CER over ``(prediction, reference)`` pairs."""
    total_distance = 0
    total_reference = 0
    total_prediction = 0
    for prediction, reference in pairs:
        total_distance += edit_distance(prediction, reference)
        total_reference += len(reference)
        total_prediction += len(prediction)
    if total_reference == 0:
        return 0.0 if total_prediction == 0 else 1.0
    return total_distance / total_reference


def aggregate_wer(pairs: Iterable[tuple[str, str]]) -> float:
    """Micro-averaged WER over ``(prediction, reference)`` pairs."""
    total_distance = 0
    total_reference = 0
    total_prediction = 0
    for prediction, reference in pairs:
        prediction_words = prediction.split()
        reference_words = reference.split()
        total_distance += edit_distance(prediction_words, reference_words)
        total_reference += len(reference_words)
        total_prediction += len(prediction_words)
    if total_reference == 0:
        return 0.0 if total_prediction == 0 else 1.0
    return total_distance / total_reference


__all__ = ["edit_distance", "cer", "wer", "aggregate_cer", "aggregate_wer"]
