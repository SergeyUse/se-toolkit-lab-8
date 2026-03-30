"""Stdio MCP server exposing observability tools as typed tools."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel

from mcp_obs.observability import VictoriaLogsClient, VictoriaTracesClient, resolve_settings
from mcp_obs.tools import TOOL_SPECS, TOOLS_BY_NAME, ToolPayload


def _text(data: ToolPayload) -> list[TextContent]:
    """Convert tool payload to MCP text response."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    elif isinstance(data, dict):
        payload = data
    else:
        payload = [item.model_dump() if isinstance(item, BaseModel) else item for item in data]
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, default=str))]


def create_server(
    logs_client: VictoriaLogsClient,
    traces_client: VictoriaTracesClient,
) -> Server:
    """Create the observability MCP server with all tools registered."""
    server = Server("obs")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [spec.as_tool() for spec in TOOL_SPECS]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[TextContent]:
        spec = TOOLS_BY_NAME.get(name)
        if spec is None:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        try:
            args = spec.model.model_validate(arguments or {})
            return _text(await spec.handler(logs_client, traces_client, args))
        except Exception as exc:
            return [
                TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")
            ]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    """Run the observability MCP server."""
    settings = resolve_settings()
    async with (
        VictoriaLogsClient(settings.victorialogs_url) as logs_client,
        VictoriaTracesClient(settings.victoriatraces_url) as traces_client,
    ):
        server = create_server(logs_client, traces_client)
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
