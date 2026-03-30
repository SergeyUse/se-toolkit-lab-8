"""Tool schemas, handlers, and registry for the observability MCP server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_obs.observability import VictoriaLogsClient, VictoriaTracesClient


class NoArgs(BaseModel):
    """Empty input model for tools that only need server-side configuration."""


class LogsSearchQuery(BaseModel):
    query: str = Field(
        description="LogsQL query string (e.g., 'service.name:\"backend\" severity:ERROR')"
    )
    time_range: str = Field(
        default="1h", description="Time range filter (e.g., '1h', '10m', '1d')"
    )
    limit: int = Field(default=100, ge=1, description="Maximum log entries to return")


class LogsErrorCountQuery(BaseModel):
    service: str | None = Field(
        default=None, description="Optional service name to filter by"
    )
    time_range: str = Field(
        default="1h", description="Time range filter (e.g., '1h', '10m', '1d')"
    )


class TracesListQuery(BaseModel):
    service: str = Field(description="Service name to filter traces")
    limit: int = Field(default=20, ge=1, description="Maximum traces to return")


class TracesGetQuery(BaseModel):
    trace_id: str = Field(description="The trace ID to fetch")


ToolPayload = BaseModel | Sequence[BaseModel]
ToolHandler = Callable[
    [VictoriaLogsClient, VictoriaTracesClient, BaseModel], Awaitable[ToolPayload]
]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _logs_search(
    logs_client: VictoriaLogsClient,
    _traces_client: VictoriaTracesClient,
    args: BaseModel,
) -> ToolPayload:
    """Search logs using LogsQL query."""
    if not isinstance(args, LogsSearchQuery):
        raise TypeError(f"Expected {LogsSearchQuery.__name__}, got {type(args).__name__}")
    return await logs_client.search(
        query=args.query,
        time_range=args.time_range,
        limit=args.limit,
    )


async def _logs_error_count(
    logs_client: VictoriaLogsClient,
    _traces_client: VictoriaTracesClient,
    args: BaseModel,
) -> ToolPayload:
    """Count errors per service over a time window."""
    if not isinstance(args, LogsErrorCountQuery):
        raise TypeError(
            f"Expected {LogsErrorCountQuery.__name__}, got {type(args).__name__}"
        )
    return await logs_client.error_count(
        service=args.service,
        time_range=args.time_range,
    )


async def _traces_list(
    _logs_client: VictoriaLogsClient,
    traces_client: VictoriaTracesClient,
    args: BaseModel,
) -> ToolPayload:
    """List recent traces for a service."""
    if not isinstance(args, TracesListQuery):
        raise TypeError(f"Expected {TracesListQuery.__name__}, got {type(args).__name__}")
    return await traces_client.list_traces(
        service=args.service,
        limit=args.limit,
    )


async def _traces_get(
    _logs_client: VictoriaLogsClient,
    traces_client: VictoriaTracesClient,
    args: BaseModel,
) -> ToolPayload:
    """Fetch a specific trace by ID."""
    if not isinstance(args, TracesGetQuery):
        raise TypeError(f"Expected {TracesGetQuery.__name__}, got {type(args).__name__}")
    result = await traces_client.get_trace(trace_id=args.trace_id)
    return result if result else {"error": f"Trace {args.trace_id} not found"}


TOOL_SPECS = (
    ToolSpec(
        "logs_search",
        "Search logs using LogsQL query. Use for finding specific events, errors, or trace IDs.",
        LogsSearchQuery,
        _logs_search,
    ),
    ToolSpec(
        "logs_error_count",
        "Count errors per service over a time window. Use to quickly see if there are recent errors.",
        LogsErrorCountQuery,
        _logs_error_count,
    ),
    ToolSpec(
        "traces_list",
        "List recent traces for a service. Use to find traces for investigation.",
        TracesListQuery,
        _traces_list,
    ),
    ToolSpec(
        "traces_get",
        "Fetch a specific trace by ID. Use to inspect the full span hierarchy of a request.",
        TracesGetQuery,
        _traces_get,
    ),
)
TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
