#!/bin/bash

# Astrochat Docker Startup Script
echo "🔮 Welcome to Astrochat Docker Setup!"
echo "======================================"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists, if not create it
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
fi

# Ask for Gemini API key
echo ""
echo "🔑 Please enter your Google Gemini API key:"
echo "   (You can get one from: https://makersuite.google.com/app/apikey)"
read -p "API Key: " GEMINI_API_KEY

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ API key cannot be empty. Please provide a valid Gemini API key."
    exit 1
fi

# Update .env file with API key
echo "💾 Updating .env file with your API key..."
sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$GEMINI_API_KEY/" .env

echo ""
echo "🚀 Starting Astrochat services..."
echo "   This may take a few minutes on first run..."

# Build and start services
docker-compose up --build -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for PostgreSQL
echo "📊 Waiting for PostgreSQL..."
echo "   This may take a minute on first run..."
until docker-compose exec -T postgres pg_isready -U astrochat -d astrochat 2>/dev/null; do
    echo "   PostgreSQL is starting..."
    sleep 10
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis
echo "🔴 Waiting for Redis..."
until docker-compose exec -T redis redis-cli ping 2>/dev/null; do
    echo "   Redis is starting..."
    sleep 5
done
echo "✅ Redis is ready!"

# Wait for API to be ready
echo "🌐 Waiting for Astrochat API..."
until curl -f http://localhost:8000/health &> /dev/null; do
    echo "   Model is loading..."
    sleep 10
done
echo "✅ Astrochat API is ready!"

echo ""
echo "🎉 Astrochat is now running!"
echo "======================================"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo "📈 ChromaDB Info: http://localhost:8000/chroma-info"
echo "💾 Cache Stats: http://localhost:8000/cache-stats"
echo ""
echo "🚀 Test the API:"
echo "curl -X POST \"http://localhost:8000/horoscope\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"name\": \"TestUser\", \"birth_date\": \"1995-08-20\", \"birth_time\": \"14:30\", \"birth_place\": \"Jaipur, India\"}'"
echo ""
echo "🛑 To stop services: docker-compose down"
echo "📋 To view logs: docker-compose logs -f"
echo "======================================"
