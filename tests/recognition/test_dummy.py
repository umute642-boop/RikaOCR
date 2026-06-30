# SPDX-License-Identifier: Apache-2.0
"""Tests for the DummyRecognizer."""

from PIL import Image

from rikaocr.recognition.base import RecognitionResult, Recognizer
from rikaocr.recognition.dummy import DummyRecognizer


def _image() -> Image.Image:
    return Image.new("RGB", (10, 10), (255, 255, 255))


def test_returns_preset_text() -> None:
    recognizer = DummyRecognizer(text="بسم", confidence=0.5)
    assert recognizer.recognize(_image()) == RecognitionResult(text="بسم", confidence=0.5)


def test_default_is_empty() -> None:
    result = DummyRecognizer().recognize(_image())
    assert result.text == ""
    assert result.confidence is None


def test_satisfies_recognizer_protocol() -> None:
    assert isinstance(DummyRecognizer(), Recognizer)
