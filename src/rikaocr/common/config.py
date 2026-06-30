# SPDX-License-Identifier: Apache-2.0
"""Configuration loading scaffolding.

The concrete configuration backend (for example Hydra/OmegaConf) is introduced
in a later milestone. This module defines a stable loading contract now so that
other modules can depend on it without committing to an implementation yet.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ConfigLoader(Protocol):
    """Contract for loading configuration into a plain mapping."""

    def load(self, path: str) -> dict[str, Any]:
        """Load configuration from ``path`` and return it as a mapping."""
        ...


def load_config(path: str) -> dict[str, Any]:
    """Load configuration from ``path``.

    The configuration backend is selected in a later milestone (see TDD v0.2);
    until then this raises :class:`NotImplementedError`.
    """
    raise NotImplementedError("Configuration loading is introduced in a later milestone.")


__all__ = ["ConfigLoader", "load_config"]
