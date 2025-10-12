"""Configuration loading helpers for agent YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def load_agent_config(file_name: str) -> dict[str, Any]:
    """Load a YAML configuration file from the local config directory."""
    config_path = _CONFIG_DIR / file_name
    with config_path.open("r", encoding="utf-8") as config_file:
        loaded = yaml.safe_load(config_file)
    return loaded if isinstance(loaded, dict) else {}
