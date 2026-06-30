# SPDX-License-Identifier: Apache-2.0
"""Deterministic, document-level train/val/test splitting.

Splitting by document id (not by line) prevents leakage: every line of a
document lands in the same split. The assignment is deterministic — hashing the
document id yields a stable fraction in ``[0, 1)`` that maps to a split — so the
same corpus always splits the same way (reproducibility, ADR-006). Pure stdlib;
no image dependency.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from enum import StrEnum

from rikaocr.common.exceptions import ValidationError

_HASH_DENOMINATOR = 1 << 32


class Split(StrEnum):
    """The dataset partition a document belongs to."""

    TRAIN = "train"
    VAL = "val"
    TEST = "test"


def _doc_fraction(doc_id: str) -> float:
    digest = hashlib.sha256(doc_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") / _HASH_DENOMINATOR


def assign_split(doc_id: str, *, train: float = 0.8, val: float = 0.1) -> Split:
    """Deterministically assign a document to a split from its id.

    ``train`` and ``val`` are fractions; the remainder is the test fraction.
    Raises :class:`ValidationError` for invalid ratios.
    """
    if not 0.0 < train < 1.0 or not 0.0 <= val < 1.0 or train + val >= 1.0:
        raise ValidationError(f"Invalid split ratios: train={train}, val={val}.")
    fraction = _doc_fraction(doc_id)
    if fraction < train:
        return Split.TRAIN
    if fraction < train + val:
        return Split.VAL
    return Split.TEST


def split_documents(
    doc_ids: Iterable[str], *, train: float = 0.8, val: float = 0.1
) -> dict[Split, list[str]]:
    """Group document ids into train/val/test (each document in exactly one)."""
    groups: dict[Split, list[str]] = {Split.TRAIN: [], Split.VAL: [], Split.TEST: []}
    for doc_id in doc_ids:
        groups[assign_split(doc_id, train=train, val=val)].append(doc_id)
    return groups


__all__ = ["Split", "assign_split", "split_documents"]
