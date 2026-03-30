"""Observability client for VictoriaLogs and VictoriaTraces."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class ObsSettings:
    """Observability service settings."""

    victorialogs_url: str
    victoriatraces_url: str


def resolve_settings() -> ObsSettings:
    """Resolve observability settings from environment variables."""
    import os

    victorialogs_host = os.getenv("VICTORIALOGS_HOST_ADDRESS", "127.0.0.1")
    victorialogs_port = os.getenv("VICTORIALOGS_HOST_PORT", "42010")
    victoriatraces_host = os.getenv("VICTORIATRACES_HOST_ADDRESS", "127.0.0.1")
    victoriatraces_port = os.getenv("VICTORIATRACES_HOST_PORT", "42011")

    return ObsSettings(
        victorialogs_url=f"http://{victorialogs_host}:{victorialogs_port}",
        victoriatraces_url=f"http://{victoriatraces_host}:{victoriatraces_port}",
    )


class VictoriaLogsClient:
    """Client for querying VictoriaLogs via HTTP API."""

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> VictoriaLogsClient:
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self._client:
            await self._client.aclose()

    async def search(
        self,
        query: str,
        time_range: str = "1h",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search logs using LogsQL query.

        Args:
            query: LogsQL query string (e.g., 'service.name:"backend" severity:ERROR')
            time_range: Time range filter (e.g., '1h', '10m', '1d')
            limit: Maximum number of log entries to return

        Returns:
            List of log entries as dictionaries
        """
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # VictoriaLogs query endpoint
        url = f"{self._base_url}/select/logsql/query"

        # Build query with time range prefix
        full_query = f"_time:{time_range} {query}"

        params = {"query": full_query, "limit": str(limit)}

        response = await self._client.post(url, data=params)
        response.raise_for_status()

        # VictoriaLogs returns newline-delimited JSON (NDJSON)
        lines = response.text.strip().split("\n")
        results = []
        for line in lines:
            if line.strip():
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue
        return results

    async def error_count(
        self,
        service: str | None = None,
        time_range: str = "1h",
    ) -> dict[str, int]:
        """Count errors per service over a time window.

        Args:
            service: Optional service name to filter by
            time_range: Time range filter (e.g., '1h', '10m', '1d')

        Returns:
            Dictionary mapping service names to error counts
        """
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # Build query for errors
        if service:
            query = f'_time:{time_range} service.name:"{service}" severity:ERROR'
        else:
            query = f"_time:{time_range} severity:ERROR"

        url = f"{self._base_url}/select/logsql/query"
        params = {"query": query, "limit": "10000"}

        response = await self._client.post(url, data=params)
        response.raise_for_status()

        # VictoriaLogs returns newline-delimited JSON (NDJSON)
        lines = response.text.strip().split("\n")
        logs = []
        for line in lines:
            if line.strip():
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        # Count errors by service
        error_counts: dict[str, int] = {}
        for entry in logs:
            # Extract service name from log entry
            service_name = entry.get("service.name", "unknown")
            error_counts[service_name] = error_counts.get(service_name, 0) + 1

        return error_counts


class VictoriaTracesClient:
    """Client for querying VictoriaTraces via Jaeger-compatible HTTP API."""

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> VictoriaTracesClient:
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self._client:
            await self._client.aclose()

    async def list_traces(
        self,
        service: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """List recent traces for a service.

        Args:
            service: Service name to filter traces
            limit: Maximum number of traces to return

        Returns:
            List of trace summaries
        """
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # Jaeger-compatible API endpoint
        url = f"{self._base_url}/select/jaeger/api/traces"
        params = {"service": service, "limit": str(limit)}

        response = await self._client.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        # Jaeger API returns {"data": [...]}
        return data.get("data", [])

    async def get_trace(self, trace_id: str) -> dict[str, Any] | None:
        """Fetch a specific trace by ID.

        Args:
            trace_id: The trace ID to fetch

        Returns:
            Full trace data or None if not found
        """
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # Jaeger-compatible API endpoint for single trace
        url = f"{self._base_url}/select/jaeger/api/traces/{trace_id}"

        response = await self._client.get(url)
        response.raise_for_status()

        data = response.json()
        traces = data.get("data", [])
        return traces[0] if traces else None
