# syntax=docker/dockerfile:1.4

# Choose a python version that you know works with your application
FROM python:3.13-slim

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:0.6.16 /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# Copy requirements file
COPY --link pyproject.toml .

# Install the requirements using uv
RUN uv sync

EXPOSE 8080


CMD [ "uv", "run", "marimo", "edit", "--host", "0.0.0.0", "-p", "8080", "--no-token" ]
