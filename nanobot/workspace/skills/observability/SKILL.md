# Observability Skill

You have access to observability tools that let you query **VictoriaLogs** and **VictoriaTraces**. Use these tools when the user asks about system health, errors, logs, or traces.

## Available Tools

### Log Tools (VictoriaLogs)

- **`logs_search`** — Search logs using LogsQL query
  - `query`: LogsQL query string (e.g., `service.name:"backend" severity:ERROR`)
  - `time_range`: Time range filter (e.g., `1h`, `10m`, `1d`) — default `1h`
  - `limit`: Maximum log entries to return — default `100`

- **`logs_error_count`** — Count errors per service over a time window
  - `service`: Optional service name to filter by
  - `time_range`: Time range filter (e.g., `1h`, `10m`, `1d`) — default `1h`

### Trace Tools (VictoriaTraces)

- **`traces_list`** — List recent traces for a service
  - `service`: Service name to filter traces
  - `limit`: Maximum traces to return — default `20`

- **`traces_get`** — Fetch a specific trace by ID
  - `trace_id`: The trace ID to fetch

## When to Use These Tools

### User asks about errors or system health

1. **Start with `logs_error_count`** to quickly see if there are recent errors and which services are affected.

2. **Use `logs_search`** to inspect the relevant service logs and extract recent `trace_id` values from error entries.

3. **Use `traces_get`** to inspect the full request path for a failing trace.

### User asks about a specific request or trace

1. If they provide a **trace ID**, use `traces_get` directly.

2. If they describe a request (e.g., "the failed lab submission from 5 minutes ago"), use `logs_search` to find matching log entries and extract the `trace_id`.

### User asks about service behavior or performance

1. Use `traces_list` to see recent traces for that service.

2. Use `traces_get` to inspect specific traces for span timing and hierarchy.

## Query Patterns

### Find recent errors in LMS backend

```
logs_error_count(service="Learning Management Service", time_range="10m")
```

### Search for specific events

```
logs_search(query='service.name:"Learning Management Service" severity:ERROR', time_range="10m", limit=50)
```

### Find trace ID in logs, then fetch trace

```
logs_search(query='service.name:"Learning Management Service" severity:ERROR', time_range="10m")
# Extract trace_id from results, then:
traces_get(trace_id="<extracted_trace_id>")
```

## Response Style

- **Summarize findings concisely** — don't dump raw JSON.
- **Highlight what matters**: error messages, failed spans, timing bottlenecks.
- **Connect logs to traces**: "Found 3 errors in the last 10 minutes. The most recent has trace_id `abc123`. Fetching full trace..."
- **Be actionable**: "The error occurs in the database query span — PostgreSQL may be down or unreachable."

## Example Interaction

**User**: "Any LMS backend errors in the last 10 minutes?"

**You**:
1. Call `logs_error_count(service="Learning Management Service", time_range="10m")`
2. If errors found: "Yes, found 5 errors in the last 10 minutes."
3. Call `logs_search(query='service.name:"Learning Management Service" severity:ERROR', time_range="10m", limit=10)`
4. Extract key details: "Most errors are 'connection refused' from database queries."
5. If trace_id present: "Fetching trace `abc123` to see the full request path..."
6. Call `traces_get(trace_id="abc123")`
7. Summarize: "The trace shows the request failed at the db_query span after 30ms timeout."
