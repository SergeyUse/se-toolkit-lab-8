# mcp-obs

MCP server for observability tools (VictoriaLogs and VictoriaTraces).

## Tools

- `logs_search` — Search logs using LogsQL query
- `logs_error_count` — Count errors per service over a time window
- `traces_list` — List recent traces for a service
- `traces_get` — Fetch a specific trace by ID

## Usage

```bash
python -m mcp_obs
```
