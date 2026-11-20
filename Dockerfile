FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home vetsys
USER vetsys

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]