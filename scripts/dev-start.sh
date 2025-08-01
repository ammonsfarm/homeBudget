#!/bin/bash

# Home Budget App - Development Server Start Script
# This script starts both backend and frontend development servers

set -e  # Exit on any error

echo "🚀 Starting Home Budget App Development Servers..."
echo "================================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Project root: $PROJECT_ROOT"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "📋 Loading environment variables..."
    set -a
    source <(grep -v '^#' "$PROJECT_ROOT/.env" | grep -v '^$' | grep '=')
    set +a
else
    echo "⚠️  No .env file found. Creating from example..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "Please edit .env file with your configuration"
    exit 1
fi

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set in .env file"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        return 1
    fi
    return 0
}

# Function to kill process by port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "🔪 Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
        sleep 2
    fi
}

echo ""
echo "🔧 Checking system requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed"
    exit 1
fi

echo "✅ System requirements met"

# Clean up any existing processes
echo ""
echo "🧹 Cleaning up existing processes..."
kill_port 8000  # Backend
kill_port 3000  # Frontend

echo ""
echo "🐍 Setting up Python backend..."

cd "$PROJECT_ROOT/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Start backend server in background
echo "🚀 Starting backend server on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PROJECT_ROOT/logs/backend.pid"

echo ""
echo "⚛️  Setting up Node.js frontend..."

cd "$PROJECT_ROOT/frontend"

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Start frontend server in background
echo "🚀 Starting frontend server on port 3000..."
npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PROJECT_ROOT/logs/frontend.pid"

echo ""
echo "✅ Development servers started!"
echo "📊 Backend API: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost'):8000"
echo "🌐 Frontend App: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost'):3000"
echo "📚 API Docs: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost'):8000/docs"
echo ""
echo "📋 Process IDs:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f $PROJECT_ROOT/logs/backend.log"
echo "   Frontend: tail -f $PROJECT_ROOT/logs/frontend.log"
echo ""
echo "🛑 To stop servers: ./scripts/dev-stop.sh"
echo ""
echo "⏳ Waiting for servers to start..."
sleep 5

# Check if servers are running
if check_port 8000; then
    echo "❌ Backend server failed to start on port 8000"
    echo "📝 Check backend log: tail -f $PROJECT_ROOT/logs/backend.log"
else
    echo "✅ Backend server is running on port 8000"
fi

if check_port 3000; then
    echo "❌ Frontend server failed to start on port 3000"
    echo "📝 Check frontend log: tail -f $PROJECT_ROOT/logs/frontend.log"
else
    echo "✅ Frontend server is running on port 3000"
fi

echo ""
echo "🎉 Setup complete! Your budget app is ready to use."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo 'Servers stopped.'; exit" INT

# Keep script running
wait
