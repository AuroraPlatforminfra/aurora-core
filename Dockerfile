FROM python:3.12-slim as builder

WORKDIR /build
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -e .

FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y libpq5 curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY src/aurora /app/aurora
COPY .env.example /app/.env

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

RUN useradd -m -u 1000 aurora && chown -R aurora:aurora /app
USER aurora

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "aurora.app:app", "--host", "0.0.0.0", "--port", "8000"]
