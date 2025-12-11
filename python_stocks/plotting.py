"""Centralized matplotlib configuration for the package.

This module switches matplotlib to a non-interactive backend when running in
CI/test mode to avoid GUI requirements. Import ``plt`` from here instead of
``matplotlib.pyplot`` directly so the backend is configured consistently.
"""
import os
from types import SimpleNamespace

TEST_MODE_FLAG = os.getenv("PYTHON_STOCKS_TEST_MODE", "").lower() in {"1", "true", "yes"}


def _fallback_plt():
    def _noop(*args, **kwargs):  # pragma: no cover - trivial pass-through
        return None

    return SimpleNamespace(
        get_backend=lambda: "agg" if TEST_MODE_FLAG else "unavailable",
        plot=_noop,
        legend=_noop,
        title=_noop,
        show=_noop,
        close=_noop,
        figure=_noop,
    )


try:
    import matplotlib

    if TEST_MODE_FLAG:
        matplotlib.use("Agg", force=True)

    import matplotlib.pyplot as plt  # type: ignore
except Exception:
    if not TEST_MODE_FLAG:
        raise
    plt = _fallback_plt()

__all__ = ["plt", "TEST_MODE_FLAG"]
