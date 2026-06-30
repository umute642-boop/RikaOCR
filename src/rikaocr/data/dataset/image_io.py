# SPDX-License-Identifier: Apache-2.0
"""Image input/output helpers, isolating the Pillow dependency.

All direct use of Pillow is confined to this module, so the rest of the codebase
(and its strict type checking) stays insulated from third-party typing gaps.
Requires the optional ``[data]`` extra.
"""

from __future__ import annotations

from PIL import Image

from rikaocr.common.types import PathLike

_WHITE = (255, 255, 255)


def load_image(path: PathLike) -> Image.Image:
    """Load an image from disk as an RGB copy."""
    with Image.open(path) as image:
        return image.convert("RGB")


def save_image(image: Image.Image, path: PathLike) -> None:
    """Save an image to disk (format inferred from the path suffix)."""
    image.save(path)


def to_grayscale(image: Image.Image) -> Image.Image:
    """Return a grayscale (``"L"`` mode) copy of the image."""
    return image.convert("L")


def new_image(width: int, height: int, color: tuple[int, int, int] = _WHITE) -> Image.Image:
    """Create a new blank RGB image (useful for tests and synthesis)."""
    return Image.new("RGB", (width, height), color)


__all__ = ["load_image", "save_image", "to_grayscale", "new_image"]
