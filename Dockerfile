FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV FORCE_COLOR=1
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

WORKDIR /bot
COPY pyproject.toml uv.lock* /bot/
RUN uv sync --frozen --no-dev
COPY . /bot
CMD uv run main.py
