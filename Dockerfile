############################
# Stage 1: Builder
############################
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python packages inside /install directory
RUN pip install --prefix=/install -r requirements.txt


############################
# Stage 2: Runtime
############################
FROM python:3.11-slim

# Environment
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Set timezone to UTC
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && ln -fs /usr/share/zoneinfo/UTC /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app ./app
COPY keys ./keys
COPY cron ./cron

# Copy cron job into system directory
RUN chmod 0644 /cron/2fa-cron \
    && crontab /cron/2fa-cron

# Create volume mount points
RUN mkdir -p /data /cron_output \
    && chmod 755 /data \
    && chmod 755 /cron_output

# Expose FastAPI port
EXPOSE 8080

# Start cron + FastAPI server together
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8080
