"""MCP server for observability tools (VictoriaLogs and VictoriaTraces)."""

from mcp_obs.observability import ObsSettings, resolve_settings
from mcp_obs.server import create_server, main

__all__ = ["ObsSettings", "resolve_settings", "create_server", "main"]
