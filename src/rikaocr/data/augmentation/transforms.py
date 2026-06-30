# SPDX-License-Identifier: Apache-2.0
"""Composable, seedable image augmentations for training data.

Each augmenter implements :class:`Augmenter` (``apply(image, rng) -> image``) and
draws its random magnitude from the supplied NumPy generator, so a fixed seed
yields byte-identical output. Photometric ops use Pillow/NumPy; geometric ops use
Pillow transforms. Requires the optional ``[data]`` extra; augmentation is
applied only to the training split (see the M4 plan).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

_WHITE = (255, 255, 255)


@runtime_checkable
class Augmenter(Protocol):
    """A single, composable image augmentation."""

    def apply(self, image: Image.Image, rng: np.random.Generator) -> Image.Image:
        """Return an augmented copy of ``image``, drawing randomness from ``rng``."""
        ...


@dataclass(frozen=True, slots=True)
class Brightness:
    """Scale brightness by a random factor in ``[low, high]``."""

    low: float = 0.7
    high: float = 1.3

    def apply(self, image: Image.Image, rng: np.random.Generator) -> Image.Image:
        factor = float(rng.uniform(self.low, self.high))
        return ImageEnhance.Brightness(image).enhance(factor)


@dataclass(frozen=True, slots=True)
class Contrast:
    """Scale contrast by a random factor in ``[low, high]``."""

    low: float = 0.7
    high: float = 1.3

    def apply(self, image: Image.Image, rng: np.random.Generator) -> Image.Image:
        factor = float(rng.uniform(self.low, self.high))
        return ImageEnhance.Contrast(image).enhance(factor)


@dataclass(frozen=True, slots=True)
class GaussianBlur:
    """Blur with a random radius in ``[0, max_radius]``."""

    max_radius: float = 1.5

    def apply(self, image: Image.Image, rng: np.random.Generator) -> Image.Image:
        radius = float(rng.uniform(0.0, self.max_radius))
        return image.filter(ImageFilter.GaussianBlur(radius))


@dataclass(frozen=True, slots=True)
class GaussianNoise:
    """Add zero-mean Gaussian noise with standard deviation ``sigma``."""

    sigma: float = 12.0

    def apply(self, image: Image.Image, rng: np.random.Generator) -> Image.Image:
        array = np.asarray(image, dtype=np.float32)
        noisy = np.clip(array + rng.normal(0.0, self.sigma, array.shape), 0, 255)
        return Image.fromarray(noisy.astype(np.uint8), mode=image.mode)


@dataclass(frozen=True, slots=True)
class Binarize:
    """Global-threshold binarisation (deterministic; ``rng`` unused)."""

    threshold: int = 128

    def apply(self, image: Image.Image, rng: np.random.Generator) -> Image.Image:
        gray = image.convert("L")
        binary = gray.point(lambda value: 255 if value >= self.threshold else 0)
        return binary.convert(image.mode)


@dataclass(frozen=True, slots=True)
class Rotate:
    """Rotate by a random angle in ``[-max_degrees, max_degrees]`` (white fill)."""

    max_degrees: float = 3.0

    def apply(self, image: Image.Image, rng: np.random.Generator) -> Image.Image:
        angle = float(rng.uniform(-self.max_degrees, self.max_degrees))
        return image.rotate(angle, expand=False, fillcolor=_WHITE)


@dataclass(frozen=True, slots=True)
class Perspective:
    """Apply a small random perspective warp (white fill outside)."""

    magnitude: float = 0.02

    def apply(self, image: Image.Image, rng: np.random.Generator) -> Image.Image:
        width, height = image.size
        dx = self.magnitude * width
        dy = self.magnitude * height
        output_corners = [(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)]
        input_corners = [
            (rng.uniform(-dx, dx), rng.uniform(-dy, dy)),
            (width + rng.uniform(-dx, dx), rng.uniform(-dy, dy)),
            (width + rng.uniform(-dx, dx), height + rng.uniform(-dy, dy)),
            (rng.uniform(-dx, dx), height + rng.uniform(-dy, dy)),
        ]
        coeffs = _perspective_coeffs(output_corners, input_corners)
        return image.transform(
            (width, height),
            Image.Transform.PERSPECTIVE,
            coeffs,
            resample=Image.Resampling.BICUBIC,
            fillcolor=_WHITE,
        )


def _perspective_coeffs(
    output_corners: list[tuple[float, float]],
    input_corners: list[tuple[float, float]],
) -> list[float]:
    matrix: list[list[float]] = []
    for (ox, oy), (ix, iy) in zip(output_corners, input_corners, strict=True):
        matrix.append([ox, oy, 1.0, 0.0, 0.0, 0.0, -ix * ox, -ix * oy])
        matrix.append([0.0, 0.0, 0.0, ox, oy, 1.0, -iy * ox, -iy * oy])
    a = np.array(matrix, dtype=np.float64)
    b = np.array(input_corners, dtype=np.float64).reshape(8)
    return [float(value) for value in np.linalg.solve(a, b)]


__all__ = [
    "Augmenter",
    "Brightness",
    "Contrast",
    "GaussianBlur",
    "GaussianNoise",
    "Binarize",
    "Rotate",
    "Perspective",
]
