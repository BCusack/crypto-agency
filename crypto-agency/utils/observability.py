"""Observability helpers (AgentOps integration)."""

from __future__ import annotations

import logging
import os

import agentops

logger = logging.getLogger(__name__)


def init_agentops(trace_name: str) -> None:
    """Initialize AgentOps if an API key is available."""
    api_key = os.getenv("AGENTOPS_API_KEY")
    if not api_key:
        logger.debug("AgentOps API key not set; skipping initialization.")
        return

    agentops.init(api_key=api_key, trace_name=trace_name)
    logger.info("AgentOps initialized with trace '%s'.", trace_name)
