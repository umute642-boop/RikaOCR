# SPDX-License-Identifier: Apache-2.0
"""Kraken recognition engine behind the :class:`Recognizer` interface (ADR-019).

This adapter keeps Kraken — a heavy, platform-sensitive dependency trained on
Linux/WSL2 with CUDA — fully isolated from the core. Kraken is imported *lazily*
inside the methods that use it, so importing this module (and running the test
suite) never requires the optional ``[train]`` extra to be installed.

The recognition path here is exercised end-to-end only once a trained model is
available (milestone F1, on WSL2); until then its kraken-dependent behaviour is
covered by a ``pytest.importorskip`` test.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image

from rikaocr.common.types import PathLike
from rikaocr.recognition.base import RecognitionResult


@dataclass(slots=True)
class KrakenRecognizer:
    """Recognises a single line image with a trained Kraken model.

    The model is loaded lazily on first use and cached for subsequent calls.
    """

    model_path: PathLike
    _model: object | None = field(default=None, init=False, repr=False)

    def _load(self) -> object:
        """Load and cache the Kraken model (lazy import of ``kraken``)."""
        if self._model is None:
            from kraken.lib import models

            self._model = models.load_any(str(self.model_path))
        return self._model

    def recognize(self, image: Image.Image) -> RecognitionResult:
        """Recognise ``image`` as one text line and return the transcription.

        The crop is treated as a single pre-segmented, right-to-left line. The
        confidence (when Kraken reports per-character scores) is their mean.
        """
        from kraken import rpred
        from kraken.containers import BaselineLine, Segmentation

        model = self._load()
        rgb = image.convert("RGB")
        width, height = rgb.size
        line = BaselineLine(
            id="line_0",
            baseline=[(0, height // 2), (width, height // 2)],
            boundary=[(0, 0), (width, 0), (width, height), (0, height)],
        )
        segmentation = Segmentation(
            type="baselines",
            imagename="",
            text_direction="horizontal-rl",
            script_detection=False,
            lines=[line],
            regions={},
        )
        records = list(rpred.rpred(model, rgb, segmentation))
        if not records:
            return RecognitionResult(text="")
        record = records[0]
        confidences = getattr(record, "confidences", None)
        confidence = sum(confidences) / len(confidences) if confidences else None
        return RecognitionResult(text=str(record), confidence=confidence)


__all__ = ["KrakenRecognizer"]
