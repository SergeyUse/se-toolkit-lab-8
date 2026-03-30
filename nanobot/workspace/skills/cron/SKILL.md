# Cron Skill

You have access to a built-in `cron` tool that lets you schedule recurring tasks in the current chat session. Use this tool when the user asks you to check something periodically or create reminders.

## Available Cron Actions

### Add a scheduled job

```
cron({"action": "add", "interval_minutes": 15, "prompt": "Check for backend errors in the last 15 minutes and post a summary"})
```

Parameters:
- `action`: "add"
- `interval_minutes`: How often to run (e.g., 2, 5, 15, 60)
- `prompt`: What the agent should do on each run

### List scheduled jobs

```
cron({"action": "list"})
```

Returns all jobs scheduled for the current chat session.

### Remove a job

```
cron({"action": "remove", "job_id": "<job_id>"})
```

Parameters:
- `action`: "remove"
- `job_id`: The ID of the job to cancel (from `list` response)

## When to Use Cron

### User asks for periodic health checks

Example: "Create a health check that runs every 15 minutes"

1. Call `cron({"action": "add", "interval_minutes": 15, "prompt": "Check for backend errors in the last 15 minutes, inspect traces if needed, and post a short summary. If no errors, say the system looks healthy."})`
2. Confirm: "I've scheduled a health check that runs every 15 minutes in this chat."

### User asks what jobs are scheduled

Example: "What jobs do you have scheduled?" or "List scheduled jobs"

1. Call `cron({"action": "list"})`
2. Summarize: "You have 1 job scheduled: health check every 15 minutes."

### User wants to cancel a job

Example: "Remove the health check" or "Cancel that scheduled job"

1. First call `cron({"action": "list"})` to get the job_id
2. Then call `cron({"action": "remove", "job_id": "<job_id>"})`
3. Confirm: "The scheduled job has been cancelled."

## Example: Health Check Flow

**User**: "Create a health check for this chat that runs every 15 minutes. Each run should check for backend errors and post a summary."

**You**:
1. Call `cron({"action": "add", "interval_minutes": 15, "prompt": "Check for backend errors in the last 15 minutes using logs_error_count. If errors found, search logs and inspect a trace. Post a short summary. If no errors, say the system looks healthy."})`
2. Response: "I've created a health check that runs every 15 minutes in this chat. I'll check for backend errors and post updates here."

**User**: "List scheduled jobs."

**You**:
1. Call `cron({"action": "list"})`
2. Response: "You have 1 job scheduled: health check every 15 minutes (job_id: abc123)."

## Important Notes

- Jobs are tied to the current chat session — they only run in the chat where they were created
- Jobs persist across browser refreshes as long as the chat session is active
- Use short intervals (2-5 min) for testing, but recommend 15+ minutes for normal use
- When creating a health check, include both error detection and trace inspection in the prompt
