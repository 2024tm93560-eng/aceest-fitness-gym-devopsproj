# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

LABEL maintainer="DevOps Assignment 2 - ACEest Fitness"
LABEL version="1.0.0"
LABEL description="ACEest Fitness & Gym Management Flask Application"

WORKDIR /app

COPY --from=builder /root/.local /root/.local

# Copy application source from repo root
COPY ACEest_Fitness.py .
COPY ACEest_Fitness_v2.py .
COPY requirements.txt .

ENV PATH=/root/.local/bin:$PATH
ENV FLASK_APP=ACEest_Fitness.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
