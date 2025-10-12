import os
import logging
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools import google_search

from mcp import StdioServerParameters

logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool").setLevel(logging.ERROR)


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


root_agent = Agent(
    model="gemini-2.5-pro",
    name="root_agent",
    description="A helpful crypto analyst that can fetch market data and time information.",
    instruction=(
        "Answer user questions about crypto markets. When you need real data, call the "
        "available Bybit market-data tools."
    ),
    tools=[
        google_search,
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["bybit-mcp"],
                    env=_build_bybit_env(),
                )
            ),
            tool_filter=[
                "get_tickers",
                "get_server_time",
                "get_recent_trades",
                "get_order_book",
                "get_kline",
                "get_mark_price_kline",
                "get_index_price_kline",
                "get_premium_index_price_kline",
                "get_instruments_info",
                "get_funding_rate_history",
                "get_open_interest",
                "get_insurance",
                "get_risk_limit",
                "get_long_short_ratio",
            ],
        )
    ],
)
