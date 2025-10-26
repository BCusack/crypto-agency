"""Utilities for constructing MCP toolsets used by agents."""

from __future__ import annotations

from typing import Iterable

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from .env_vars import build_bybit_env


def build_mcp_toolset(tool_filter: Iterable[str] | None) -> MCPToolset:
    """Create an MCP toolset with the optional filter supplied by configuration."""
    return MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="uvx",
                args=["bybit-mcp==0.1.10", ],
                env=build_bybit_env(),
            )
        ),
        tool_filter=list(tool_filter or []),
    )
