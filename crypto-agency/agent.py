import os
import sys
import logging
from pathlib import Path
from typing import Any

import yaml
from google.adk.agents import ParallelAgent, SequentialAgent, LlmAgent
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

from mcp import StdioServerParameters
import agentops

agentops.init(
    api_key=os.getenv("AGENTOOPS_API_KEY"),
    trace_name="crypto_trading_agent",
)

logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool").setLevel(logging.ERROR)

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

logger = logging.getLogger(__name__)


# --- Services ---
# Services must be shared across runners to share state and memory
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()


def _get_env_var(name: str, default: str | None = None) -> str | None:
    """Return an env var or a default when unset/empty."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value


def _build_bybit_env() -> dict[str, str]:
    bybit_env: dict[str, str] = {}
    api_key = _get_env_var("BYBIT_API_KEY")

    api_secret = _get_env_var("BYBIT_API_SECRET")

    if api_key:
        bybit_env["BYBIT_API_KEY"] = api_key
    if api_secret:
        bybit_env["BYBIT_API_SECRET"] = api_secret

    # Default to testnet and keep trading disabled unless explicitly enabled.
    bybit_env["BYBIT_TESTNET"] = _get_env_var("BYBIT_TESTNET", "true") or "true"
    bybit_env["BYBIT_TRADING_ENABLED"] = _get_env_var("BYBIT_TRADING_ENABLED", "false") or "false"

    return bybit_env


def _load_agent_config(file_name: str) -> dict[str, Any]:
    config_path = Path(__file__).resolve().parent / "config" / file_name
    with config_path.open("r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


def _build_mcp_toolset(tool_filter: list[str] | None) -> MCPToolset:
    print(f'tool_filter: {tool_filter}')
    return MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="uvx",
                args=["bybit-mcp"],
                env=_build_bybit_env(),
            )
        ),
        tool_filter=tool_filter or [],
    )


_SUPERVISOR_CONFIG = _load_agent_config("crypto_trading_supervisor.yaml")
_ANALYST_CONFIG = _load_agent_config("market_analyst.yaml")
_POSITION_MANAGER_CONFIG = _load_agent_config("position_manager.yaml")

market_analyst_agent = LlmAgent(
    model=_ANALYST_CONFIG.get("model", "gemini-2.5-pro"),
    name=_ANALYST_CONFIG.get("name", "market_analyst"),
    description=_ANALYST_CONFIG.get("description", ""),
    instruction=_ANALYST_CONFIG.get("instruction", ""),
    tools=[
        _build_mcp_toolset(
            _ANALYST_CONFIG.get("tools", {}).get("mcp_tool_filter")
        ),
    ],
    output_key=_ANALYST_CONFIG.get("output_key"),
)

position_manager_agent = LlmAgent(
    model=_POSITION_MANAGER_CONFIG.get("model", "gemini-2.5-pro"),
    name=_POSITION_MANAGER_CONFIG.get("name", "position_manager"),
    description=_POSITION_MANAGER_CONFIG.get("description", ""),
    instruction=_POSITION_MANAGER_CONFIG.get("instruction", ""),
    tools=[
        _build_mcp_toolset(
            _POSITION_MANAGER_CONFIG.get("tools", {}).get("mcp_tool_filter")
        ),
    ],
    output_key=_POSITION_MANAGER_CONFIG.get("output_key"),
)

parallel_specialists = ParallelAgent(
    name="crypto_parallel_specialists",
    sub_agents=[market_analyst_agent, position_manager_agent],
    description="Runs market analyst and position manager in parallel to accelerate decision-making.",
)


supervisor_agent = LlmAgent(
    model=_SUPERVISOR_CONFIG.get("model", "gemini-2.5-pro"),
    name=_SUPERVISOR_CONFIG.get("name", "crypto_trading_supervisor"),
    description=_SUPERVISOR_CONFIG.get("description", ""),
    instruction=_SUPERVISOR_CONFIG.get("instruction", ""),
)


root_agent = SequentialAgent(
    name="crypto_trading_workflow",
    sub_agents=[parallel_specialists, supervisor_agent],
    description="Supervisor orchestrates analyst and position manager outputs for final guidance.",
)
