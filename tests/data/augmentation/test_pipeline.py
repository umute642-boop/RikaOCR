# SPDX-License-Identifier: Apache-2.0
"""Tests for the seedable augmentation pipeline."""

from PIL import Image
from rikaocr.data.augmentation.pipeline import AugmentationPipeline
from rikaocr.data.augmentation.transforms import (
    Brightness,
    Contrast,
    GaussianNoise,
    Perspective,
    Rotate,
)


def _image() -> Image.Image:
    return Image.new("RGB", (40, 20), (120, 130, 140))


def _pipeline() -> AugmentationPipeline:
    return AugmentationPipeline(
        [Brightness(), Contrast(), GaussianNoise(10.0), Rotate(), Perspective()]
    )


def test_same_seed_is_deterministic() -> None:
    pipeline = _pipeline()
    first = pipeline.apply(_image(), seed=42)
    second = pipeline.apply(_image(), seed=42)
    assert first.tobytes() == second.tobytes()
    assert first.size == (40, 20)


def test_different_seed_differs() -> None:
    pipeline = _pipeline()
    assert pipeline.apply(_image(), seed=42).tobytes() != pipeline.apply(_image(), seed=7).tobytes()


def test_empty_pipeline_is_identity() -> None:
    image = _image()
    result = AugmentationPipeline([]).apply(image, seed=0)
    assert result.tobytes() == image.tobytes()
