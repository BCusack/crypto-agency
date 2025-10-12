"""Environment variable helpers for Bybit and general runtime settings."""

from __future__ import annotations

import os
from typing import Optional


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """Return an environment variable or fallback to a default when unset/blank."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value


def build_bybit_env() -> dict[str, str]:
    """Construct the environment payload used when spawning the Bybit MCP server."""
    bybit_env: dict[str, str] = {}

    api_key = get_env_var("BYBIT_API_KEY")
    api_secret = get_env_var("BYBIT_API_SECRET")

    if api_key:
        bybit_env["BYBIT_API_KEY"] = api_key
    if api_secret:
        bybit_env["BYBIT_API_SECRET"] = api_secret

    # Default to testnet and keep trading disabled unless explicitly enabled.
    bybit_env["BYBIT_TESTNET"] = get_env_var("BYBIT_TESTNET", "true") or "true"
    bybit_env["BYBIT_TRADING_ENABLED"] = get_env_var("BYBIT_TRADING_ENABLED", "false") or "false"

    return bybit_env
