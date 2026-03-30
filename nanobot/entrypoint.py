#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config at runtime, then launches nanobot gateway.
"""

import json
import os
import sys
import tempfile
from pathlib import Path


def main():
    config_dir = Path(__file__).parent
    config_path = config_dir / "config.json"
    workspace = config_dir / "workspace"

    # Read base config
    with open(config_path) as f:
        config = json.load(f)

    # Override provider API key and base URL from env vars
    if "LLM_API_KEY" in os.environ:
        config["providers"]["custom"]["apiKey"] = os.environ["LLM_API_KEY"]
    if "LLM_API_BASE_URL" in os.environ:
        config["providers"]["custom"]["apiBase"] = os.environ["LLM_API_BASE_URL"]
    if "LLM_API_MODEL" in os.environ:
        config["agents"]["defaults"]["model"] = os.environ["LLM_API_MODEL"]

    # Override gateway host and port from env vars
    if "NANOBOT_GATEWAY_CONTAINER_ADDRESS" in os.environ:
        config.setdefault("gateway", {})["host"] = os.environ["NANOBOT_GATEWAY_CONTAINER_ADDRESS"]
    if "NANOBOT_GATEWAY_CONTAINER_PORT" in os.environ:
        config.setdefault("gateway", {})["port"] = int(os.environ["NANOBOT_GATEWAY_CONTAINER_PORT"])

    # Override MCP LMS server env vars
    if "tools" in config and "mcpServers" in config["tools"] and "lms" in config["tools"]["mcpServers"]:
        lms_config = config["tools"]["mcpServers"]["lms"]
        lms_env = lms_config.setdefault("env", {})
        if "NANOBOT_LMS_BACKEND_URL" in os.environ:
            lms_env["NANOBOT_LMS_BACKEND_URL"] = os.environ["NANOBOT_LMS_BACKEND_URL"]
        if "NANOBOT_LMS_API_KEY" in os.environ:
            lms_env["NANOBOT_LMS_API_KEY"] = os.environ["NANOBOT_LMS_API_KEY"]

    # Override MCP OBS server env vars
    if "tools" in config and "mcpServers" in config["tools"] and "obs" in config["tools"]["mcpServers"]:
        obs_config = config["tools"]["mcpServers"]["obs"]
        obs_env = obs_config.setdefault("env", {})
        if "VICTORIALOGS_HOST_ADDRESS" in os.environ:
            obs_env["VICTORIALOGS_HOST_ADDRESS"] = os.environ["VICTORIALOGS_HOST_ADDRESS"]
        if "VICTORIALOGS_HOST_PORT" in os.environ:
            obs_env["VICTORIALOGS_HOST_PORT"] = os.environ["VICTORIALOGS_HOST_PORT"]
        if "VICTORIATRACES_HOST_ADDRESS" in os.environ:
            obs_env["VICTORIATRACES_HOST_ADDRESS"] = os.environ["VICTORIATRACES_HOST_ADDRESS"]
        if "VICTORIATRACES_HOST_PORT" in os.environ:
            obs_env["VICTORIATRACES_HOST_PORT"] = os.environ["VICTORIATRACES_HOST_PORT"]

    # Configure webchat channel if enabled
    if "NANOBOT_WEBCHAT_CONTAINER_ADDRESS" in os.environ:
        config.setdefault("channels", {})["webchat"] = {
            "enabled": True,
            "host": os.environ["NANOBOT_WEBCHAT_CONTAINER_ADDRESS"],
            "port": int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8765")),
            "allowFrom": ["*"],
        }
    elif "channels" not in config:
        config["channels"] = {"webchat": {"enabled": True, "allowFrom": ["*"]}}

    # Configure mcp-webchat MCP server if webchat is enabled
    if "NANOBOT_WS_UI_RELAY_URL" in os.environ or ("channels" in config and "webchat" in config.get("channels", {})):
        mcp_servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
        mcp_servers["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {
                "NANOBOT_WS_UI_RELAY_URL": os.environ.get("NANOBOT_WS_UI_RELAY_URL", "http://localhost:8765"),
                "NANOBOT_WS_UI_TOKEN": os.environ.get("NANOBOT_WS_UI_TOKEN", "webchat-token"),
            },
        }

    # Write resolved config to temp directory (writable by non-root user)
    resolved_path = Path(tempfile.mktemp(suffix=".json", prefix="nanobot_config_"))
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    # Launch nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", str(resolved_path), "--workspace", str(workspace)])


if __name__ == "__main__":
    main()
