# SPDX-License-Identifier: Apache-2.0
"""Tests for image I/O helpers (requires the [data] extra)."""

from pathlib import Path

from rikaocr.data.dataset.image_io import load_image, new_image, save_image, to_grayscale


def test_new_image_dimensions_and_mode() -> None:
    image = new_image(40, 20)
    assert image.size == (40, 20)
    assert image.mode == "RGB"


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "img.png"
    save_image(new_image(30, 10, color=(10, 20, 30)), target)
    assert target.exists()

    loaded = load_image(target)
    assert loaded.size == (30, 10)
    assert loaded.mode == "RGB"
    assert loaded.getpixel((0, 0)) == (10, 20, 30)


def test_to_grayscale_changes_mode() -> None:
    gray = to_grayscale(new_image(8, 8))
    assert gray.mode == "L"
    assert gray.size == (8, 8)
