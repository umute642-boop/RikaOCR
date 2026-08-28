# SPDX-License-Identifier: Apache-2.0
"""Tests for CER/WER metrics."""

import pytest

from rikaocr.evaluation.metrics import aggregate_cer, aggregate_wer, cer, edit_distance, wer


def test_edit_distance_classic() -> None:
    assert edit_distance("kitten", "sitting") == 3


def test_edit_distance_identical_and_empty() -> None:
    assert edit_distance("abc", "abc") == 0
    assert edit_distance("", "abc") == 3
    assert edit_distance("abc", "") == 3
    assert edit_distance("", "") == 0


def test_cer_basic() -> None:
    assert cer("abc", "abc") == 0.0
    assert cer("abd", "abc") == pytest.approx(1 / 3)


def test_cer_empty_reference() -> None:
    assert cer("", "") == 0.0
    assert cer("abc", "") == 1.0  # non-empty prediction against empty reference


def test_cer_unicode() -> None:
    assert cer("بسم", "بسم") == 0.0
    assert cer("بزم", "بسم") == pytest.approx(1 / 3)


def test_wer_basic() -> None:
    assert wer("the cat sat", "the cat sat") == 0.0
    assert wer("the dog sat", "the cat sat") == pytest.approx(1 / 3)


def test_wer_empty_reference() -> None:
    assert wer("", "") == 0.0
    assert wer("word", "") == 1.0


def test_aggregate_cer_is_micro_averaged() -> None:
    # Per-sample rates are 1.0 and 0.0 (mean 0.5); micro-average is 2/3.
    pairs = [("", "ab"), ("x", "x")]
    assert aggregate_cer(pairs) == pytest.approx(2 / 3)


def test_aggregate_wer_is_micro_averaged() -> None:
    pairs = [("the dog sat", "the cat sat"), ("ok", "ok")]
    # distances: 1 + 0 = 1; reference words: 3 + 1 = 4 -> 0.25
    assert aggregate_wer(pairs) == pytest.approx(0.25)


def test_aggregate_empty_is_zero() -> None:
    assert aggregate_cer([]) == 0.0
    assert aggregate_wer([]) == 0.0
