import logging
from google.adk.agents import ParallelAgent, SequentialAgent, LlmAgent
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from utils import (
    build_mcp_toolset,
    configure_utf8_stdio,
    init_agentops,
    load_agent_config,
)

logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

configure_utf8_stdio()
init_agentops(trace_name="crypto_trading_agent")


# --- Services ---
# Services must be shared across runners to share state and memory
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
logger.debug("Initializing agent configurations and services.")


_SUPERVISOR_CONFIG = load_agent_config("crypto_trading_supervisor.yaml")
_ANALYST_CONFIG = load_agent_config("market_analyst.yaml")
_POSITION_MANAGER_CONFIG = load_agent_config("position_manager.yaml")

market_analyst_agent = LlmAgent(
    model=_ANALYST_CONFIG.get("model", "gemini-2.5-pro"),
    name=_ANALYST_CONFIG.get("name", "market_analyst"),
    description=_ANALYST_CONFIG.get("description", ""),
    instruction=_ANALYST_CONFIG.get("instruction", ""),
    tools=[
        build_mcp_toolset(
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
        build_mcp_toolset(
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
