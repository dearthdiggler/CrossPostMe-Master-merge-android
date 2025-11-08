#!/bin/bash
# Backend server startup script for WSL

# Change to the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || {
	echo "Error: Failed to change to script directory"
	exit 1
}

echo "🚀 Starting CrossPostMe Backend Server..."
echo ""

# Check if MongoDB is running
if ! nc -z localhost 27017 2>/dev/null; then
	echo "⚠️  MongoDB is not running on port 27017"
	echo "   Please start MongoDB first:"
	echo "   - WSL: sudo service mongodb start"
	echo "   - Docker: docker run -d --name mongodb -p 27017:27017 mongo:latest"
	echo ""
	read -p "Do you want to continue anyway? (y/n) " -n 1 -r
	echo ""
	if [[ ! $REPLY =~ ^[Yy]$ ]]; then
		exit 1
	fi
fi

# Check if .env exists
if [ ! -f .env ]; then
	echo "⚠️  .env file not found, creating from .env.example..."
	cp .env.example .env 2>/dev/null || echo "MONGO_URL=mongodb://localhost:27017
DB_NAME=crosspostme
CORS_ORIGINS=http://localhost:3000,http://localhost:8000" >.env
fi

# Install requirements if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
	echo "📦 Installing Python dependencies..."
	pip3 install --user -r requirements.txt
fi

# Start the server
echo "✅ Starting uvicorn server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

python3 -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
