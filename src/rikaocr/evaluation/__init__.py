# SPDX-License-Identifier: Apache-2.0
"""Evaluation: error-rate metrics (CER/WER) and the evaluation loop.

``metrics`` is pure standard library (no image or ML dependency); the evaluation
loop (added later) needs the optional ``[data]`` extra to load images.
"""

from rikaocr.evaluation.metrics import (
    aggregate_cer,
    aggregate_wer,
    cer,
    edit_distance,
    wer,
)

__all__ = ["aggregate_cer", "aggregate_wer", "cer", "edit_distance", "wer"]
