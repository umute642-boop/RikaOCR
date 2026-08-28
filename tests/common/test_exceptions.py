# SPDX-License-Identifier: Apache-2.0
"""Tests for the domain exception hierarchy."""

import pytest

from rikaocr.common.exceptions import (
    AlignmentError,
    ConfigError,
    DataError,
    ModelError,
    RikaOCRError,
    SerializationError,
    ValidationError,
)


@pytest.mark.parametrize(
    "error_cls",
    [
        DataError,
        ValidationError,
        AlignmentError,
        SerializationError,
        ConfigError,
        ModelError,
    ],
)
def test_subclasses_of_base(error_cls: type[RikaOCRError]) -> None:
    assert issubclass(error_cls, RikaOCRError)


def test_message_is_preserved() -> None:
    with pytest.raises(ValidationError, match="bad value"):
        raise ValidationError("bad value")


def test_base_catches_all() -> None:
    with pytest.raises(RikaOCRError):
        raise AlignmentError("misaligned")
