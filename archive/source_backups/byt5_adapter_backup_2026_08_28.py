# SPDX-License-Identifier: Apache-2.0
"""ByT5 adapter for Ottoman Arabic-script to Latin transliteration.

Heavy ML dependencies are imported lazily so importing RikaOCR does not require
PyTorch or Transformers unless this adapter is actually instantiated.
"""

from __future__ import annotations

import unicodedata

from rikaocr.common.types import PathLike
from rikaocr.transliteration.base import TransliterationResult


class ByT5Transliterator:
    """Transliterate Ottoman text with a fine-tuned ByT5 model."""

    def __init__(
        self,
        model_path: PathLike,
        *,
        device: str | None = None,
        max_new_tokens: int = 160,
    ) -> None:
        try:
            import torch
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("ByT5 transliteration requires PyTorch and Transformers.") from exc

        self._torch = torch
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._max_new_tokens = max_new_tokens

        self._tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self._model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path))
        self._model.to(self._device)
        self._model.eval()

    def transliterate(self, text: str) -> TransliterationResult:
        """Return a Latin-script transliteration without modifying the source."""
        source = unicodedata.normalize("NFC", text)
        inputs = self._tokenizer(source, return_tensors="pt").to(self._device)

        with self._torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=self._max_new_tokens,
                num_beams=1,
            )

        prediction = self._tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        )
        return TransliterationResult(text=prediction)


__all__ = ["ByT5Transliterator"]
