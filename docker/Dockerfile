# Stage 1: builder
FROM python:3.13-slim AS builder

LABEL authors="Volodymyr Dotsiak"

# System deps needed to compile some Python packages (asyncpg, psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=2.3.2
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /telegram-freelance-hunter-bot

# Copy only dependency manifests first (layer-caching)
COPY pyproject.toml poetry.lock poetry.toml ./

# Install runtime deps only (no dev deps), export to a plain venv
RUN poetry config virtualenvs.in-project true \
    && poetry install --only main --no-root --no-interaction --no-ansi

# Stage 2: runtime
FROM python:3.13-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd --create-home appuser
WORKDIR /telegram-freelance-hunter-bot

# Copy virtualenv from builder
COPY --from=builder /telegram-freelance-hunter-bot/.venv /telegram-freelance-hunter-bot/.venv

# Copy source code and data directory
COPY src/ ./src/
COPY data/ ./data/

# Allow non-root runtime user to write bot.log and other runtime artifacts
RUN touch /telegram-freelance-hunter-bot/bot.log \
    && chown -R appuser:appuser /telegram-freelance-hunter-bot

# Make the venv the active Python environment
ENV PATH="/telegram-freelance-hunter-bot/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/telegram-freelance-hunter-bot"

USER appuser

CMD ["python", "src/main.py"]
