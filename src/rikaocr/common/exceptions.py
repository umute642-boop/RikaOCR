# SPDX-License-Identifier: Apache-2.0
"""Domain-specific exception hierarchy for RikaOCR.

All errors raised by RikaOCR derive from :class:`RikaOCRError`, so callers can
catch the whole family with a single ``except`` while still being able to handle
specific failure modes.
"""

from __future__ import annotations


class RikaOCRError(Exception):
    """Base class for all RikaOCR domain errors."""


class DataError(RikaOCRError):
    """Raised for ingestion, dataset, or annotation data problems."""


class ValidationError(RikaOCRError):
    """Raised when a domain object violates one of its invariants."""


class AlignmentError(RikaOCRError):
    """Raised when text and geometry alignment is inconsistent."""


class SerializationError(RikaOCRError):
    """Raised when (de)serialization of a domain object fails."""


class ConfigError(RikaOCRError):
    """Raised for configuration loading or validation problems."""


class ModelError(RikaOCRError):
    """Raised for model loading, inference, or training problems."""


__all__ = [
    "RikaOCRError",
    "DataError",
    "ValidationError",
    "AlignmentError",
    "SerializationError",
    "ConfigError",
    "ModelError",
]
