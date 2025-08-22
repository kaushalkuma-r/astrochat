#!/bin/bash

echo "🚀 Starting Astrochat API..."

# Wait for PostgreSQL to be ready
echo "📊 Waiting for PostgreSQL..."
until pg_isready -h postgres -U astrochat -d astrochat; do
    echo "   PostgreSQL is starting..."
    sleep 5
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "🔴 Waiting for Redis..."
until redis-cli -h redis ping; do
    echo "   Redis is starting..."
    sleep 5
done
echo "✅ Redis is ready!"

# Create database tables
echo "🗄️ Setting up database tables..."
python3 -c "
from app.database import create_tables
create_tables()
print('✅ Database tables created!')
"

# Data loading is now handled during application startup
echo "📄 ChromaDB data loading will be handled during application startup..."

# Start the API
echo "🌐 Starting FastAPI server..."
exec python3 main.py
