FROM python:3.11-slim AS builder
WORKDIR /app

# Copy requirements early for caching
COPY app/requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron tzdata \
 && ln -fs /usr/share/zoneinfo/UTC /etc/localtime \
 && dpkg-reconfigure --frontend noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy full application
COPY app/ ./app
COPY keys/ ./keys
COPY cron/ ./cron

# Volumes
RUN mkdir -p /data && chmod 755 /data
RUN mkdir -p /cron_output && chmod 755 /cron_output

# Install cron job
RUN chmod 0644 /cron/2fa-cron && crontab /cron/2fa-cron

EXPOSE 8080

CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
