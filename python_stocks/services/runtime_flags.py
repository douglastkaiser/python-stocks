"""Environment-based toggles for controlling caching behavior."""
from __future__ import annotations

import os
from typing import Optional


_CACHE_TRUE = {"1", "true", "yes", "on"}


def _env_flag(name: str, default: str = "") -> bool:
    return os.getenv(name, default).strip().lower() in _CACHE_TRUE


#: Prefer cached assets in CI by default to keep jobs fast.
STATIC_ARTIFACT_MODE = _env_flag("PYTHON_STOCKS_STATIC_ARTIFACTS") or _env_flag("CI")
#: Explicit opt-out flag to bypass caches even in CI/static scenarios.
LIVE_COMPUTE_MODE = _env_flag("PYTHON_STOCKS_LIVE_COMPUTE")


def prefer_cached_results(opt_in: Optional[bool] = None) -> bool:
    """Return whether caches should be consulted.

    The optional ``opt_in`` parameter lets callers explicitly choose caching. If
    omitted, the decision is derived from environment variables:

    - ``PYTHON_STOCKS_LIVE_COMPUTE`` disables caching entirely.
    - ``PYTHON_STOCKS_STATIC_ARTIFACTS`` or ``CI`` enables caching for faster,
      deterministic outputs in automation.
    """

    if opt_in is not None:
        return opt_in
    if LIVE_COMPUTE_MODE:
        return False
    return STATIC_ARTIFACT_MODE


__all__ = ["STATIC_ARTIFACT_MODE", "LIVE_COMPUTE_MODE", "prefer_cached_results"]
