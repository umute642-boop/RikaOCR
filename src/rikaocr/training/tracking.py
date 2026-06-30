# SPDX-License-Identifier: Apache-2.0
"""Experiment-tracking abstraction (see ADR-016).

A minimal, engine-agnostic ``Tracker`` contract with two implementations:

* :class:`NullTracker` -- the default no-op tracker, so callers never need to
  special-case "no tracking configured".
* :class:`MlflowTracker` -- logs to MLflow, imported *lazily* so the package is
  importable (and the tests run) without the optional ``[train]`` extra.

Both are context managers: entering starts a run, exiting ends it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType
from typing import Protocol, runtime_checkable


@runtime_checkable
class Tracker(Protocol):
    """Records parameters and metrics for one experiment run."""

    def start_run(self) -> None:
        """Begin a new run (idempotent for no-op trackers)."""
        ...

    def log_params(self, params: Mapping[str, object]) -> None:
        """Record run parameters (hyper-parameters, config)."""
        ...

    def log_metrics(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        """Record numeric metrics, optionally at a training ``step``."""
        ...

    def __enter__(self) -> Tracker:
        """Start the run and return the active tracker."""
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """End the run."""
        ...


@dataclass(frozen=True, slots=True)
class NullTracker:
    """A tracker that silently discards everything (the default)."""

    def start_run(self) -> None:
        """No run to start."""
        return None

    def log_params(self, params: Mapping[str, object]) -> None:
        """Discard the parameters."""
        return None

    def log_metrics(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        """Discard the metrics."""
        return None

    def __enter__(self) -> NullTracker:
        """Return self; no run to start."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Nothing to end."""
        return None


@dataclass
class MlflowTracker:
    """Logs to MLflow. Requires the optional ``[train]`` extra.

    MLflow is imported lazily inside each method so that merely importing this
    module never pulls in the dependency.
    """

    run_name: str | None = None
    tracking_uri: str | None = None

    def start_run(self) -> None:
        """Start an MLflow run (setting the tracking URI first if given)."""
        import mlflow

        if self.tracking_uri is not None:
            mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.start_run(run_name=self.run_name)

    def log_params(self, params: Mapping[str, object]) -> None:
        """Forward parameters to ``mlflow.log_params``."""
        import mlflow

        mlflow.log_params(dict(params))

    def log_metrics(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        """Forward metrics to ``mlflow.log_metrics``."""
        import mlflow

        mlflow.log_metrics(dict(metrics), step=step)

    def __enter__(self) -> MlflowTracker:
        """Start an MLflow run and return self."""
        self.start_run()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """End the active MLflow run."""
        import mlflow

        mlflow.end_run()
        return None


__all__ = ["Tracker", "NullTracker", "MlflowTracker"]
