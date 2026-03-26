# ── Stage 1 : build ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN pip install --upgrade pip build setuptools wheel

# Copy project files
COPY pyproject.toml setup.py setup.cfg README.md ./
COPY banking_api/ ./banking_api/

# Build the wheel
RUN python -m build --wheel --outdir /app/dist

# ── Stage 2 : runtime ──────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Create non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy the built wheel from builder
COPY --from=builder /app/dist/*.whl /app/dist/

# Install the package
RUN pip install --upgrade pip && \
    pip install /app/dist/*.whl && \
    rm -rf /app/dist

# Create data directory (mount your CSV here at runtime)
RUN mkdir -p /app/data && chown appuser:appgroup /app/data

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Set environment variable for dataset path
ENV TRANSACTIONS_CSV_PATH=/app/data/transactions_data.csv

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/system/health')" || exit 1

# Start uvicorn
CMD ["uvicorn", "banking_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
