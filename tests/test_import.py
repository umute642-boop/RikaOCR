# SPDX-License-Identifier: Apache-2.0
"""Smoke test: the package must be importable and expose its version."""

import rikaocr


def test_package_imports() -> None:
    assert rikaocr.__version__ == "0.1.0"
