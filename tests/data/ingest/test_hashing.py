# SPDX-License-Identifier: Apache-2.0
"""Tests for content hashing helpers."""

from pathlib import Path

from rikaocr.data.ingest.hashing import byte_size, sha256_file

# Known SHA-256 of b"abc".
_ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_same_content_same_hash(tmp_path: Path) -> None:
    first = tmp_path / "a.bin"
    second = tmp_path / "b.bin"
    first.write_bytes(b"hello")
    second.write_bytes(b"hello")
    assert sha256_file(first) == sha256_file(second)


def test_different_content_different_hash(tmp_path: Path) -> None:
    first = tmp_path / "a.bin"
    second = tmp_path / "b.bin"
    first.write_bytes(b"hello")
    second.write_bytes(b"world")
    assert sha256_file(first) != sha256_file(second)


def test_known_hash_value(tmp_path: Path) -> None:
    target = tmp_path / "x.bin"
    target.write_bytes(b"abc")
    assert sha256_file(target) == _ABC_SHA256


def test_byte_size(tmp_path: Path) -> None:
    target = tmp_path / "x.bin"
    target.write_bytes(b"12345")
    assert byte_size(target) == 5
