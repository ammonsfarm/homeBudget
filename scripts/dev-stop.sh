#!/bin/bash

# Home Budget App - Development Server Stop Script
# This script stops both backend and frontend development servers

echo "🛑 Stopping Home Budget App Development Servers..."
echo "================================================="

# Function to stop process by PID file
stop_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping $service_name (PID: $pid)..."
            kill "$pid"
            sleep 2
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚡ Force killing $service_name..."
                kill -9 "$pid"
            fi
        else
            echo "⚠️  $service_name process (PID: $pid) not found"
        fi
        rm -f "$pid_file"
    else
        echo "⚠️  $service_name PID file not found"
    fi
}

# Stop backend
stop_by_pid_file ".backend.pid" "Backend"

# Stop frontend
stop_by_pid_file ".frontend.pid" "Frontend"

# Kill any remaining processes on our ports
echo "🧹 Cleaning up any remaining processes..."

# Kill processes on backend port (8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🛑 Killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

# Kill processes on frontend port (3000)
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🛑 Killing processes on port 3000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
fi

# Kill any uvicorn processes
pkill -f "uvicorn" 2>/dev/null || true

# Kill any node processes related to our app
pkill -f "next-server" 2>/dev/null || true

echo ""
echo "✅ All development servers stopped!"
echo ""
echo "To restart the servers, run: ./scripts/dev-start.sh"
