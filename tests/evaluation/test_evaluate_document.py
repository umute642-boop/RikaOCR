# SPDX-License-Identifier: Apache-2.0
"""Tests for document-level evaluation (evaluate_document)."""

import pytest

from rikaocr.common.exceptions import DataError
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.models import Document, Line, Page, Region
from rikaocr.evaluation.evaluate import EvalReport, evaluate_document


def _document(texts: list[str]) -> Document:
    lines = [Line(text=text, reading_index=index) for index, text in enumerate(texts)]
    region = Region(region_type=RegionType.PARAGRAPH, lines=lines)
    return Document(doc_id="d", pages=[Page(page_id="p", regions=[region])])


def test_perfect_match_scores_zero() -> None:
    prediction = _document(["abc", "def"])
    reference = _document(["abc", "def"])
    assert evaluate_document(prediction, reference) == EvalReport(cer=0.0, wer=0.0, num_samples=2)


def test_micro_averaged_errors() -> None:
    # refs "abc"+"abc" = 6 chars; one wrong char each -> 2/6 = 1/3.
    prediction = _document(["abx", "abx"])
    reference = _document(["abc", "abc"])
    report = evaluate_document(prediction, reference)
    assert report.num_samples == 2
    assert report.cer == pytest.approx(1 / 3)


def test_pairs_follow_reading_order() -> None:
    # Prediction lines given out of order but reading_index drives pairing.
    pred_lines = [Line(text="two", reading_index=1), Line(text="one", reading_index=0)]
    prediction = Document(
        doc_id="d",
        pages=[Page(page_id="p", regions=[Region(RegionType.PARAGRAPH, lines=pred_lines)])],
    )
    reference = _document(["one", "two"])
    assert evaluate_document(prediction, reference).cer == 0.0


def test_line_count_mismatch_raises() -> None:
    with pytest.raises(DataError):
        evaluate_document(_document(["a"]), _document(["a", "b"]))
