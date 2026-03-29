# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Question 1: "What is the agentic loop?"**

The agentic loop is the fundamental cycle that an AI agent follows to accomplish tasks autonomously. It typically consists of these core stages:

1. **Perceive** — Gather information about the current state (user input, environment, tool outputs, memory)
2. **Reason** — Analyze the situation, plan next steps, and decide what action to take
3. **Act** — Execute the chosen action (call a tool, send a message, modify a file, etc.)
4. **Observe** — Receive feedback from the action (success, error, output data)
5. **Repeat** — Loop back to reason with the new information until the task is complete

This loop enables agents to:
- Handle multi-step tasks
- Adapt based on feedback
- Recover from errors
- Make decisions dynamically

**Question 2: "What labs are available in our LMS?"**

The bare agent (without MCP tools) could not return real LMS data. It searched local files and returned information from the course documentation instead, describing Lab 8 and mentioning there are 10 labs total in the SET course. This demonstrates the agent needs MCP tools to access live backend data.

## Task 1B — Agent with LMS tools

**Question 1: "What labs are available?"**

The agent with MCP tools returned real lab data from the LMS backend:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

**Question 2: "Is the LMS backend healthy?"**

The agent called the `lms_health` tool and responded:

> Yes, the LMS backend is healthy! It's currently tracking 56 items.

## Task 1C — Skill prompt

**Question: "Show me the scores" (without specifying a lab)**

With the LMS skill prompt, the agent correctly:
1. Called `lms_labs` first to get available labs
2. Listed all 8 labs with their titles
3. Asked the user to choose which lab they want to see scores for

This demonstrates the skill prompt successfully teaches the agent to ask for the lab parameter when it's missing, rather than failing or guessing.

## Task 2A — Deployed agent

Nanobot gateway startup log showing successful deployment:

```
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | 2026-03-29 21:02:29.703 | INFO | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | 2026-03-29 21:02:32.373 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_health' from server 'lms'
nanobot-1  | 2026-03-29 21:02:32.373 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
nanobot-1  | 2026-03-29 21:02:34.205 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_webchat_ui_message' from server 'webchat'
nanobot-1  | 2026-03-29 21:02:34.205 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'webchat': connected, 1 tools registered
nanobot-1  | 2026-03-29 21:02:34.205 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

## Task 2B — Web client

WebSocket endpoint test showing successful agent response:

```
Request: {"content": "What labs are available?"}
Response: {"type":"text","content":"Here are the available labs in the LMS:\n\n1. **Lab 01** – Products, Architecture & Roles\n2. **Lab 02** — Run, Fix, and Deploy a Backend Service\n3. **Lab 03** — Backend API: Explore, Debug, Implement, Deploy\n4. **Lab 04** — Testing, Front-end, and AI Agents\n5. **Lab 05** — Data Pipeline and Analytics Dashboard\n6. **Lab 06** — Build Your Own Agent\n7. **Lab 07** — Build a Client with an AI Coding Agent\n8. **Lab 08** — lab-08\n\nIs there a specific lab you'd like to know more about? I can show you pass rates, completion rates, submission timelines, group performance, or top learners for any of these labs.","format":"markdown"}
```

The Flutter web client is accessible at `http://localhost:42002/flutter/` and returns the expected HTML page with the Nanobot web interface.

**Verification checklist:**
- [x] `docker compose ps` shows nanobot service running
- [x] Nanobot logs show "Channels enabled: webchat" and MCP servers connected
- [x] WebSocket endpoint at `/ws/chat` responds with real LMS data
- [x] Flutter client accessible at `/flutter`
- [x] Agent answers backed by LMS backend data (not generic responses)

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
