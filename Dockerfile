# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder — install dependencies
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime — lean production image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="DevOps Assignment 2 - ACEest Fitness"
LABEL version="1.0.0"
LABEL description="ACEest Fitness & Gym Management Flask Application"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application source
COPY app/ .

# Environment variables
ENV PATH=/root/.local/bin:$PATH
ENV FLASK_APP=ACEest_Fitness.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
