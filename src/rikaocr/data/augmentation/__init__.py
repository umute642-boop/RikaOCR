# SPDX-License-Identifier: Apache-2.0
"""Image augmentation: composable, seedable transforms and a pipeline.

Requires the optional ``[data]`` extra (Pillow, NumPy). Augmentation is applied
only to the training split (see the M4 plan).
"""

from rikaocr.data.augmentation.pipeline import AugmentationPipeline
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

__all__ = [
    "AugmentationPipeline",
    "Augmenter",
    "Binarize",
    "Brightness",
    "Contrast",
    "GaussianBlur",
    "GaussianNoise",
    "Perspective",
    "Rotate",
]
