#!/bin/bash

echo "🛑 Stopping Astrochat services..."
docker-compose down

echo "🧹 Cleaning up..."
docker system prune -f

echo "✅ Astrochat services stopped successfully!"
echo ""
echo "💡 To start again, run: ./start.sh"
