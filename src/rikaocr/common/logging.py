# SPDX-License-Identifier: Apache-2.0
"""Structured logging configuration for RikaOCR.

This module centralises logger creation so every module emits records in the
same format. The concrete level and handlers can be tuned later through the
configuration system; for now a sensible default is applied once.
"""

from __future__ import annotations

import logging

_DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_configured: bool = False


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger once with the standard RikaOCR format.

    Repeated calls are no-ops, so importing modules can call this safely.
    """
    global _configured
    if _configured:
        return
    logging.basicConfig(level=level, format=_DEFAULT_FORMAT)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, ensuring base configuration is applied."""
    configure_logging()
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
