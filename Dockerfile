FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

COPY apps/api apps/api
COPY scripts scripts
RUN uv sync --frozen --no-dev --no-editable


FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends ca-certificates tini && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/apps/api apps/api
COPY --from=builder /app/scripts scripts
COPY --from=builder /app/pyproject.toml .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

ENTRYPOINT ["tini", "--"]
CMD ["./scripts/start.sh"]
