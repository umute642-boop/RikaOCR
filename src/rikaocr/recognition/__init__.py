# SPDX-License-Identifier: Apache-2.0
"""Recognition: the engine-agnostic Recognizer interface and adapters.

Concrete engines (Kraken, and later TrOCR/CRNN) implement ``Recognizer`` behind
this interface, so the core stays free of heavy ML dependencies. The interface
and ``DummyRecognizer`` require only the ``[data]`` extra (Pillow); the Kraken
adapter additionally requires ``[train]``.
"""

from rikaocr.recognition.base import RecognitionResult, Recognizer, recognize_document
from rikaocr.recognition.dummy import DummyRecognizer

__all__ = ["DummyRecognizer", "RecognitionResult", "Recognizer", "recognize_document"]
