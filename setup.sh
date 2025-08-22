#!/bin/bash

echo "🔧 Setting up Astrochat environment..."

# Create necessary directories
mkdir -p /app/chroma_db /app/logs

# Set proper permissions
chown -R root:root /app
chmod -R 755 /app

# Make scripts executable
chmod +x /app/docker-entrypoint.sh

echo "✅ Setup complete!"
