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
COPY requirements.txt requirements-minimal.txt ./

# Install Python dependencies with retry and timeout settings
RUN pip install --no-cache-dir --timeout 300 --retries 3 -r requirements-minimal.txt && \
    pip install --no-cache-dir --timeout 300 --retries 3 pandas==2.0.3 numpy==1.24.3 && \
    pip install --no-cache-dir --timeout 300 --retries 3 torch>=2.0.0 transformers>=4.30.0 IndicTransToolkit>=1.0.0 sentencepiece>=0.1.99

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
