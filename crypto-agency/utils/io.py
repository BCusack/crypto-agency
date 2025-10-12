"""IO helpers for standard stream configuration."""

from __future__ import annotations

import sys


def configure_utf8_stdio() -> None:
    """Ensure stdout and stderr emit UTF-8 to avoid Windows console encoding errors."""
    stdout = getattr(sys, "stdout", None)
    if stdout is not None:
        reconfigure_stdout = getattr(stdout, "reconfigure", None)
        if callable(reconfigure_stdout):
            reconfigure_stdout(encoding="utf-8")

    stderr = getattr(sys, "stderr", None)
    if stderr is not None:
        reconfigure_stderr = getattr(stderr, "reconfigure", None)
        if callable(reconfigure_stderr):
            reconfigure_stderr(encoding="utf-8")
