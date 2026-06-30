# SPDX-License-Identifier: Apache-2.0
"""A trivial recognizer that returns a fixed result.

Used to exercise the recognition and evaluation pipeline without any model or
heavy dependency; it ignores the image and returns its preset text.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from rikaocr.recognition.base import RecognitionResult


@dataclass(frozen=True, slots=True)
class DummyRecognizer:
    """Always returns the same preset text and confidence."""

    text: str = ""
    confidence: float | None = None

    def recognize(self, image: Image.Image) -> RecognitionResult:
        """Return the preset result, ignoring ``image``."""
        return RecognitionResult(text=self.text, confidence=self.confidence)


__all__ = ["DummyRecognizer"]
