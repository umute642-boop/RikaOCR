# SPDX-License-Identifier: Apache-2.0
"""Compose augmenters into a seedable, deterministic pipeline."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from PIL import Image

from rikaocr.data.augmentation.transforms import Augmenter


@dataclass(frozen=True, slots=True)
class AugmentationPipeline:
    """Apply a sequence of augmenters in order, seeded for reproducibility."""

    augmenters: Sequence[Augmenter]

    def apply(self, image: Image.Image, seed: int) -> Image.Image:
        """Apply all augmenters to ``image``; the same seed yields the same output."""
        rng = np.random.default_rng(seed)
        result = image
        for augmenter in self.augmenters:
            result = augmenter.apply(result, rng)
        return result


__all__ = ["AugmentationPipeline"]
