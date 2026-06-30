# SPDX-License-Identifier: Apache-2.0
"""Tests for deterministic document-level splitting."""

import pytest

from rikaocr.common.exceptions import ValidationError
from rikaocr.data.dataset.splitting import Split, assign_split, split_documents


def test_assignment_is_deterministic() -> None:
    first = assign_split("doc-123")
    for _ in range(5):
        assert assign_split("doc-123") == first


def test_assignment_returns_valid_split() -> None:
    assert assign_split("any-doc") in {Split.TRAIN, Split.VAL, Split.TEST}


def test_split_documents_partitions_all_ids() -> None:
    doc_ids = [f"doc-{index}" for index in range(200)]
    groups = split_documents(doc_ids)
    total = sum(len(ids) for ids in groups.values())
    assert total == len(doc_ids)
    # No document appears in more than one split.
    seen: set[str] = set()
    for ids in groups.values():
        for doc_id in ids:
            assert doc_id not in seen
            seen.add(doc_id)


def test_approximate_distribution() -> None:
    doc_ids = [f"doc-{index}" for index in range(2000)]
    groups = split_documents(doc_ids, train=0.8, val=0.1)
    train_ratio = len(groups[Split.TRAIN]) / len(doc_ids)
    # Hashing is roughly uniform; allow a generous tolerance.
    assert 0.72 < train_ratio < 0.88


@pytest.mark.parametrize(
    ("train", "val"),
    [(0.0, 0.1), (1.0, 0.0), (0.9, 0.2), (-0.1, 0.1)],
)
def test_invalid_ratios_raise(train: float, val: float) -> None:
    with pytest.raises(ValidationError):
        assign_split("doc", train=train, val=val)
