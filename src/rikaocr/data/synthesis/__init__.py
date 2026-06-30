# SPDX-License-Identifier: Apache-2.0
"""Synthetic line generation (crude v1).

Requires the optional ``[data]`` extra. The current generator only concatenates
isolated glyph images and does not model cursive joining; it is an auxiliary
pipeline-testing tool, not a realistic Rik'a renderer (see the M4 plan).
"""

from rikaocr.data.synthesis.line_synth import GlyphConcatSynth, SynthGenerator

__all__ = ["GlyphConcatSynth", "SynthGenerator"]
