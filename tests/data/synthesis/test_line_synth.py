# SPDX-License-Identifier: Apache-2.0
"""Tests for the crude glyph-concatenation synthetic generator."""

import pytest
from PIL import Image
from rikaocr.common.exceptions import DataError
from rikaocr.data.synthesis.line_synth import GlyphConcatSynth, SynthGenerator


def _glyph(width: int, height: int) -> Image.Image:
    return Image.new("RGB", (width, height), (0, 0, 0))


def test_concatenates_side_by_side() -> None:
    synth = GlyphConcatSynth(spacing=2)
    glyphs = [_glyph(10, 20), _glyph(8, 16), _glyph(12, 18)]

    line = synth.synthesize(glyphs)

    assert line.mode == "RGB"
    assert line.height == 20  # tallest glyph
    assert line.width == 10 + 8 + 12 + 2 * 2  # widths + spacing between three glyphs


def test_single_glyph_has_no_spacing() -> None:
    line = GlyphConcatSynth(spacing=5).synthesize([_glyph(14, 10)])
    assert line.size == (14, 10)


def test_empty_glyphs_raise() -> None:
    with pytest.raises(DataError):
        GlyphConcatSynth().synthesize([])


def test_satisfies_protocol() -> None:
    assert isinstance(GlyphConcatSynth(), SynthGenerator)
