FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    redis-tools \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set pip configuration for better network handling
ENV PIP_TIMEOUT=300
ENV PIP_RETRIES=3
ENV PIP_DEFAULT_TIMEOUT=300

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies with retry and timeout settings
RUN pip install --no-cache-dir --timeout 300 --retries 3 -r requirements.txt

# Copy application code
COPY . .

# Run setup script
RUN chmod +x /app/setup.sh && /app/setup.sh

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
