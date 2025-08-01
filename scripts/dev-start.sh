#!/bin/bash

# Home Budget App - Development Server Start Script
# This script starts both backend and frontend development servers

set -e  # Exit on any error

echo "🚀 Starting Home Budget App Development Servers..."
echo "================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    echo "   cp .env.example .env"
    exit 1
fi

# Load environment variables (filter out comments and empty lines)
set -a
source <(grep -v '^#' .env | grep -v '^$')
set +a

# Check if PostgreSQL is running
if ! sudo systemctl is-active --quiet postgresql; then
    echo "🐘 Starting PostgreSQL..."
    sudo systemctl start postgresql
fi

# Check if Redis is running
if ! sudo systemctl is-active --quiet redis-server; then
    echo "📮 Starting Redis..."
    sudo systemctl start redis-server
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use. Please stop the process or change the port."
        return 1
    fi
    return 0
}

# Check if ports are available
check_port $BACKEND_PORT || exit 1
check_port $FRONTEND_PORT || exit 1

# Create log directory if it doesn't exist
sudo mkdir -p /var/log/budget-app
sudo chown $USER:$USER /var/log/budget-app

# Create uploads directory if it doesn't exist
mkdir -p uploads

echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found. Installing basic dependencies..."
    pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-multipart python-jose[cryptography] passlib[bcrypt] redis python-dotenv
fi

# Run database migrations if available
if [ -d "alembic" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Start backend server in background
echo "🚀 Starting FastAPI backend on port $BACKEND_PORT..."
uvicorn main:app --host $BACKEND_HOST --port $BACKEND_PORT --reload &
BACKEND_PID=$!

cd ..

echo "📦 Setting up Node.js frontend..."
cd frontend

# Install Node.js dependencies
if [ -f "package.json" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "⚠️  package.json not found. Creating basic Next.js app..."
    npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
fi

# Start frontend server in background
echo "🚀 Starting Next.js frontend on port $FRONTEND_PORT..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Development servers started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:$FRONTEND_PORT"
echo "🔧 Backend API: http://localhost:$BACKEND_PORT"
echo "📚 API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "📊 Backend PID: $BACKEND_PID"
echo "🎨 Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop the servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  or use: ./scripts/dev-stop.sh"
echo ""
echo "📝 Logs are available in /var/log/budget-app/"

# Save PIDs for stop script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Wait for user input to stop
echo ""
echo "Press Ctrl+C to stop all servers..."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo 'Servers stopped.'; exit" INT

# Keep script running
wait
