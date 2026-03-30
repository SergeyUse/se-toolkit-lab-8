# Adapted from backend/Dockerfile and qwen-code-api/Dockerfile
# Also see https://docs.astral.sh/uv/guides/integration/docker/

# ---
# Stage 1: build the application in the `/app` directory.
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads - use the system interpreter across both images.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy root workspace files from workspace context (nanobot uses workspace dependencies)
COPY --from=workspace pyproject.toml uv.lock ./

# Copy nanobot package from workspace context
COPY --from=workspace nanobot/pyproject.toml ./nanobot/pyproject.toml
COPY --from=workspace nanobot/entrypoint.py ./nanobot/entrypoint.py

# Copy workspace packages that nanobot depends on
COPY --from=workspace mcp/mcp-lms ./mcp/mcp-lms
COPY --from=workspace mcp/mcp-obs ./mcp/mcp-obs
COPY --from=workspace nanobot-websocket-channel/mcp-webchat ./nanobot-websocket-channel/mcp-webchat
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat ./nanobot-websocket-channel/nanobot-webchat
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol ./nanobot-websocket-channel/nanobot-channel-protocol

# Sync dependencies for the nanobot package (includes workspace dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

# Copy the rest of nanobot source from workspace context
COPY --from=workspace nanobot/ ./nanobot/

# ---
# Stage 2: use a final image without uv
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

# Set environment variables for Python and application
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Make sure we use UTF-8 encoding
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*

# Accept APP_UID and APP_GID as build args for non-root user
ARG APP_UID=1000
ARG APP_GID=1000

# Setup a non-root user with configurable UID/GID
RUN groupadd --system --gid ${APP_GID} appgroup \
    && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home appuser

# Copy the application from the builder
COPY --from=builder --chown=appuser:appgroup /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
# Add src/ to Python path so packages can be imported
ENV PYTHONPATH="/app:/app/nanobot"

WORKDIR /app

# Switch to non-root user
USER appuser

# Run the nanobot gateway via entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
