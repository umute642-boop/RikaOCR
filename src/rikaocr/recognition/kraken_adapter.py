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
            if str(self.model_path).lower().endswith(".safetensors"):
                from kraken.lib.models import TorchSeqRecognizer
                from kraken.models.loaders import load_safetensors

                loaded = load_safetensors(str(self.model_path), tasks=["recognition"])
                if not loaded:
                    raise RuntimeError("No recognition model found in safetensors file.")
                self._model = TorchSeqRecognizer(loaded[0])
            else:
                from kraken.lib import models

                self._model = models.load_any(str(self.model_path))
        return self._model

    def recognize(self, image: Image.Image) -> RecognitionResult:
        """Recognise ``image`` as one text line and return the transcription.

        The crop is treated as a single pre-segmented, right-to-left line. The
        confidence (when Kraken reports per-character scores) is their mean.
        """
        from kraken import rpred
        from kraken.containers import BBoxLine, Segmentation

        model = self._load()
        rgb = image.convert("L")
        width, height = rgb.size
        line = BBoxLine(
            id="line_0",
            bbox=(0, 0, width, height),
            base_dir="R",
            text_direction="horizontal-rl",
        )
        segmentation = Segmentation(
            type="bbox",
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
