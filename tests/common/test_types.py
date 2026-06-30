# SPDX-License-Identifier: Apache-2.0
"""Tests for shared type aliases and identifier types."""

from rikaocr.common.types import DocId, PageId


def test_doc_id_behaves_like_str() -> None:
    doc_id = DocId("doc-1")
    assert doc_id == "doc-1"
    assert isinstance(doc_id, str)


def test_page_id_behaves_like_str() -> None:
    page_id = PageId("page-1")
    assert page_id == "page-1"
    assert isinstance(page_id, str)
