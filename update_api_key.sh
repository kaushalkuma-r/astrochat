#!/bin/bash

echo "🔑 Update Gemini API Key"
echo "========================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./run.sh first to set up the environment."
    exit 1
fi

# Ask for new Gemini API key
echo ""
echo "🔑 Please enter your new Google Gemini API key:"
echo "   (You can get one from: https://makersuite.google.com/app/apikey)"
read -p "New API Key: " GEMINI_API_KEY

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ API key cannot be empty."
    exit 1
fi

# Update .env file with new API key
echo "💾 Updating .env file with your new API key..."
sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$GEMINI_API_KEY/" .env

echo "✅ API key updated successfully!"

# Ask if user wants to restart services
echo ""
read -p "🔄 Do you want to restart the services to apply the new API key? (y/n): " RESTART

if [[ $RESTART =~ ^[Yy]$ ]]; then
    echo "🔄 Restarting services..."
    docker-compose restart astrochat
    echo "✅ Services restarted!"
    echo "⏳ Wait a moment for the API to be ready..."
    sleep 10
    echo "🎉 Ready! You can now test the API with the new key."
else
    echo "ℹ️ Services not restarted. You'll need to restart manually with: docker-compose restart astrochat"
fi
