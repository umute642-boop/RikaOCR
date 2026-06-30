# SPDX-License-Identifier: Apache-2.0
"""Tests for the Kraken adapter.

The lazy-import guarantee is checked unconditionally; the kraken-dependent
wiring is skipped when the optional ``[train]`` extra is not installed.
"""

import importlib

import pytest

from rikaocr.recognition.base import Recognizer
from rikaocr.recognition.kraken_adapter import KrakenRecognizer


def test_module_imports_and_constructs_without_kraken() -> None:
    # Importing the adapter and constructing it must not require kraken.
    recognizer = KrakenRecognizer(model_path="model.mlmodel")
    assert isinstance(recognizer, Recognizer)


def test_model_is_not_loaded_until_used() -> None:
    # No kraken import or model load happens at construction time.
    recognizer = KrakenRecognizer(model_path="model.mlmodel")
    assert recognizer._model is None


def test_kraken_recognition_modules_are_importable() -> None:
    pytest.importorskip("kraken")
    # With kraken present, the submodules the adapter imports lazily must exist.
    assert importlib.import_module("kraken.lib.models") is not None
    assert importlib.import_module("kraken.rpred") is not None
