# SPDX-License-Identifier: Apache-2.0
"""Tests for the experiment trackers."""

from pathlib import Path

import pytest
from rikaocr.training.tracking import MlflowTracker, NullTracker, Tracker


def test_null_tracker_is_noop() -> None:
    tracker = NullTracker()
    tracker.start_run()
    with tracker as active:
        assert active is tracker
        tracker.log_params({"lr": 0.001})
        tracker.log_metrics({"cer": 0.1}, step=1)
    # Reaching here without error is the assertion.


def test_null_tracker_satisfies_protocol() -> None:
    assert isinstance(NullTracker(), Tracker)


def test_mlflow_tracker_satisfies_protocol() -> None:
    assert isinstance(MlflowTracker(), Tracker)


def test_mlflow_tracker_round_trip(tmp_path: Path) -> None:
    pytest.importorskip("mlflow")
    import mlflow

    tracker = MlflowTracker(run_name="test", tracking_uri=tmp_path.as_uri())
    tracker.start_run()
    tracker.log_params({"lr": 0.001})
    tracker.log_metrics({"cer": 0.0, "wer": 0.0})
    mlflow.end_run()


def test_mlflow_tracker_context_manager(tmp_path: Path) -> None:
    pytest.importorskip("mlflow")
    tracker = MlflowTracker(run_name="ctx", tracking_uri=tmp_path.as_uri())
    with tracker:
        tracker.log_metrics({"cer": 0.0, "wer": 0.0})
