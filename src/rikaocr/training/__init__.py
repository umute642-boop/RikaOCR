# SPDX-License-Identifier: Apache-2.0
"""Training-side utilities: experiment tracking and engine export helpers.

Importing this package is light: optional heavy dependencies (MLflow, Kraken)
are imported lazily inside the methods that need them, so the package stays
usable without the ``[train]`` extra installed.
"""

from rikaocr.training.tracking import MlflowTracker, NullTracker, Tracker

__all__ = ["Tracker", "NullTracker", "MlflowTracker"]
