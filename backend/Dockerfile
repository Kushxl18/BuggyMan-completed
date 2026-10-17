# ============================================================================
# BuggyMan Backend Production Multi-Runtime Dockerfile
# Provides both Python 3.12 & Node.js 20 LTS for full code evaluation support
# ============================================================================
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1 \
    PORT=8000

WORKDIR /app

# 1. Install system utilities and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    libpq-dev \
    gcc \
    netcat-openbsd \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Node.js 20 LTS for JavaScript/TypeScript/React challenge evaluation
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && node --version \
    && npm --version

# 3. Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy backend application source
COPY . /app/

# 5. Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
