# SPDX-License-Identifier: Apache-2.0
"""Crude synthetic line generation (v1).

``GlyphConcatSynth`` simply lays isolated glyph images side by side on a white
background. It does NOT model cursive joining (in Rik'a letters connect and
change shape by position), so it is only an auxiliary tool for exercising the
data pipeline — not a realistic renderer. A faithful generator is future work
(see the M4 plan). Requires the optional ``[data]`` extra.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from PIL import Image

from rikaocr.common.exceptions import DataError

_WHITE = (255, 255, 255)


@runtime_checkable
class SynthGenerator(Protocol):
    """Generates a synthetic line image from isolated glyph images."""

    def synthesize(self, glyphs: Sequence[Image.Image]) -> Image.Image:
        """Combine ``glyphs`` into a single line image."""
        ...


@dataclass(frozen=True, slots=True)
class GlyphConcatSynth:
    """Concatenate glyph images left to right, vertically centred, on white."""

    spacing: int = 2
    background: tuple[int, int, int] = _WHITE

    def synthesize(self, glyphs: Sequence[Image.Image]) -> Image.Image:
        """Return a single RGB line image with all glyphs placed side by side."""
        if not glyphs:
            raise DataError("Cannot synthesise a line from zero glyphs.")
        rgb_glyphs = [glyph.convert("RGB") for glyph in glyphs]
        height = max(glyph.height for glyph in rgb_glyphs)
        width = sum(glyph.width for glyph in rgb_glyphs) + self.spacing * (len(rgb_glyphs) - 1)
        canvas = Image.new("RGB", (width, height), self.background)
        offset_x = 0
        for glyph in rgb_glyphs:
            offset_y = (height - glyph.height) // 2
            canvas.paste(glyph, (offset_x, offset_y))
            offset_x += glyph.width + self.spacing
        return canvas


__all__ = ["SynthGenerator", "GlyphConcatSynth"]
