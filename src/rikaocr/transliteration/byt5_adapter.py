# SPDX-License-Identifier: Apache-2.0
"""ByT5 adapter for Ottoman Arabic-script to Latin transliteration.

Heavy ML dependencies are imported lazily so importing RikaOCR does not require
PyTorch or Transformers unless this adapter is actually instantiated.

Two inference modes are supported:

- ``whole``: transliterate the complete input as one sequence. This preserves
  the inference behaviour used for the controlled ByT5 place-name experiment.
- ``word``: transliterate non-whitespace units separately and preserve the
  original whitespace. This is an optional operational strategy for longer OCR
  lines and does not change the reported held-out experimental results.
"""

from __future__ import annotations

import re
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
        mode: str = "whole",
    ) -> None:
        if mode not in {"whole", "word"}:
            raise ValueError(
                f"Unknown transliteration mode: {mode!r} " "(expected 'whole' or 'word')."
            )

        try:
            import torch  # type: ignore[import-not-found, unused-ignore]
            from transformers import (  # type: ignore[import-not-found]
                AutoModelForSeq2SeqLM,
                AutoTokenizer,
            )
        except ImportError as exc:
            raise RuntimeError("ByT5 transliteration requires PyTorch and Transformers.") from exc

        self._torch = torch
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._max_new_tokens = max_new_tokens
        self._mode = mode

        self._tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self._model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path))
        self._model.to(self._device)
        self._model.eval()

    def _transliterate_sequence(self, text: str) -> str:
        inputs = self._tokenizer(text, return_tensors="pt").to(self._device)

        with self._torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=self._max_new_tokens,
                num_beams=1,
            )

        return str(
            self._tokenizer.decode(
                outputs[0],
                skip_special_tokens=True,
            )
        )

    def transliterate(self, text: str) -> TransliterationResult:
        """Return a Latin-script transliteration without modifying the source."""
        source = unicodedata.normalize("NFC", text)

        if self._mode == "whole":
            prediction = self._transliterate_sequence(source)
        else:
            parts = re.split(r"(\s+)", source)
            prediction = "".join(
                part if not part or part.isspace() else self._transliterate_sequence(part)
                for part in parts
            )

        return TransliterationResult(text=prediction)


__all__ = ["ByT5Transliterator"]
