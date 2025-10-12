## Crypto Agency

Automated trading research assistants built with the Google ADK. The workflow stitches together Gemini-based specialists that analyze Bybit markets and produce human-ready trading guidance.

### Features
- Parallel market analyst and position manager agents backed by Gemini 2.5 Pro
- Shared in-memory session + memory services for contextual continuity
- MCP toolset connection to a Bybit MCP server for live market data
- AgentOps telemetry for tracing and reliability insights
- Supervisor agent that combines specialist outputs into an actionable briefing

### Prerequisites
- Python 3.13 (managed by `uv`)
- Google ADK and dependencies installed inside a virtual environment (see `pyproject.toml`)
- Access to the Bybit MCP server via `uvx bybit-mcp`
- Google API key configured for Gemini (follow Google ADK docs)

### Environment Variables
Set the following variables before starting the workflow:

| Variable | Purpose | Default |
| --- | --- | --- |
| `BYBIT_API_KEY` | Bybit API key | _required_ |
| `BYBIT_API_SECRET` | Bybit API secret | _required_ |
| `BYBIT_TESTNET` | Use Bybit testnet | `true` |
| `BYBIT_TRADING_ENABLED` | Enable live trading via MCP tools | `false` |
| `AGENTOPS_API_KEY` | Enables AgentOps session tracking | optional |

Keep trading disabled unless you are certain you want live order flow.

### Project Layout
- `crypto-agency/agent.py` – defines the specialist and supervisor agents and wires the workflow.
- `crypto-agency/config/*.yaml` – prompt and agent configuration files.
- `crypto-agency/tools/` – helper code for the Bybit MCP integration.
- `main.py` – convenience entry point for running the workflow.

### Running the Web UI
```cmd
cd C:\path\to\Cryto-agency
uv sync
set AGENTOPS_API_KEY=your-agentops-key
uv run adk web ./
```

If logging emits emoji or other non-ASCII characters on Windows, the agent setup reconfigures stdout/stderr to UTF-8 to avoid `UnicodeEncodeError` exceptions.

### Tool Filters and MCP Schema Warnings
If the Bybit MCP manifest exposes numeric enum values, Gemini currently expects strings. Trim the affected tool names from each `mcp_tool_filter` list until the MCP server publishes a schema with string enums to avoid Pydantic warnings and `400 INVALID_ARGUMENT` responses.

### Development
- Adjust agent prompts by editing the YAML configs under `crypto-agency/config/`.
- Extend tool coverage by adding wrappers in `crypto-agency/tools/` and referencing them from the configs.
- For debugging, enable higher log verbosity by configuring the root logger before instantiating agents.

### Troubleshooting
- Confirm `uvx bybit-mcp manifest` works; otherwise install/update the Bybit MCP server.
- Verify environment variables are set when running `adk web ./`.
- Check the console for Pydantic warnings; they usually pinpoint malformed tool metadata.
