# SPDX-License-Identifier: Apache-2.0
"""Tests for individual augmentation transforms (determinism + shape)."""

import numpy as np
import pytest
from PIL import Image
from rikaocr.data.augmentation.transforms import (
    Augmenter,
    Binarize,
    Brightness,
    Contrast,
    GaussianBlur,
    GaussianNoise,
    Perspective,
    Rotate,
)


def _image() -> Image.Image:
    return Image.new("RGB", (40, 20), (120, 130, 140))


_AUGMENTERS: list[Augmenter] = [
    Brightness(0.5, 1.5),
    Contrast(0.5, 1.5),
    GaussianBlur(2.0),
    GaussianNoise(15.0),
    Binarize(128),
    Rotate(5.0),
    Perspective(0.05),
]


@pytest.mark.parametrize("augmenter", _AUGMENTERS)
def test_preserves_size_and_mode(augmenter: Augmenter) -> None:
    result = augmenter.apply(_image(), np.random.default_rng(0))
    assert result.size == (40, 20)
    assert result.mode == "RGB"


@pytest.mark.parametrize("augmenter", _AUGMENTERS)
def test_same_seed_is_deterministic(augmenter: Augmenter) -> None:
    first = augmenter.apply(_image(), np.random.default_rng(7))
    second = augmenter.apply(_image(), np.random.default_rng(7))
    assert first.tobytes() == second.tobytes()


def test_binarize_produces_two_tone() -> None:
    result = Binarize(128).apply(_image(), np.random.default_rng(0))
    assert set(result.convert("L").tobytes()) <= {0, 255}


def test_runtime_checkable_protocol() -> None:
    assert isinstance(Brightness(), Augmenter)
