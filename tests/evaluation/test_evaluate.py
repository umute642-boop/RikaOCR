# SPDX-License-Identifier: Apache-2.0
"""End-to-end tests for the evaluation loop with the DummyRecognizer."""

from collections.abc import Mapping
from pathlib import Path
from types import TracebackType

import pytest

from rikaocr.data.dataset.image_io import new_image, save_image
from rikaocr.data.dataset.sample import LineSample
from rikaocr.data.dataset.splitting import Split
from rikaocr.evaluation.evaluate import EvalReport, evaluate
from rikaocr.recognition.dummy import DummyRecognizer


def _make_sample(root: Path, rel: str, text: str, line: int) -> LineSample:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    save_image(new_image(10, 10), path)
    return LineSample(
        image_path=rel,
        text=text,
        doc_id="d",
        page=0,
        region=0,
        line=line,
        split=Split.TEST,
    )


def test_perfect_prediction_scores_zero(tmp_path: Path) -> None:
    samples = [_make_sample(tmp_path, "test/lines/a.png", "ab", 0)]
    report = evaluate(DummyRecognizer(text="ab"), samples, tmp_path)
    assert report == EvalReport(cer=0.0, wer=0.0, num_samples=1)


def test_micro_averaged_cer(tmp_path: Path) -> None:
    # Two refs ("abc", "abc"); dummy predicts "abx" for both -> 1 edit / 3 chars.
    samples = [
        _make_sample(tmp_path, "test/lines/a.png", "abc", 0),
        _make_sample(tmp_path, "test/lines/b.png", "abc", 1),
    ]
    report = evaluate(DummyRecognizer(text="abx"), samples, tmp_path)
    assert report.num_samples == 2
    assert report.cer == pytest.approx(1 / 3)
    assert report.wer == pytest.approx(1.0)


class _SpyTracker:
    """Captures the metrics passed to it (structurally satisfies Tracker)."""

    def __init__(self) -> None:
        self.metrics: dict[str, float] = {}
        self.entered = False

    def log_params(self, params: Mapping[str, object]) -> None:
        return None

    def log_metrics(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        self.metrics.update(metrics)

    def __enter__(self) -> "_SpyTracker":
        self.entered = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


def test_metrics_are_logged_to_tracker(tmp_path: Path) -> None:
    samples = [_make_sample(tmp_path, "test/lines/a.png", "ab", 0)]
    spy = _SpyTracker()
    evaluate(DummyRecognizer(text="ab"), samples, tmp_path, tracker=spy)
    assert spy.entered
    assert spy.metrics == {"cer": 0.0, "wer": 0.0}
