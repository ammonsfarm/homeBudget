#!/bin/bash

echo "🚀 Deploying Home Budget App to Ubuntu Server..."
echo "=============================================="

# Configuration
REPO_URL="https://github.com/ammonsfarm/homeBudget.git"
APP_DIR="$HOME/home-budget-app"
BACKUP_DIR="$HOME/home-budget-app-backup-$(date +%Y%m%d-%H%M%S)"

# Function to backup existing installation
backup_existing() {
    if [ -d "$APP_DIR" ]; then
        echo "📦 Backing up existing installation..."
        mv "$APP_DIR" "$BACKUP_DIR"
        echo "✅ Backup created at: $BACKUP_DIR"
    fi
}

# Function to restore from backup on failure
restore_backup() {
    if [ -d "$BACKUP_DIR" ]; then
        echo "🔄 Restoring from backup due to deployment failure..."
        rm -rf "$APP_DIR"
        mv "$BACKUP_DIR" "$APP_DIR"
        echo "✅ Restored from backup"
    fi
}

# Function to cleanup backup on success
cleanup_backup() {
    if [ -d "$BACKUP_DIR" ]; then
        echo "🧹 Cleaning up backup..."
        rm -rf "$BACKUP_DIR"
        echo "✅ Backup cleaned up"
    fi
}

# Trap to restore backup on script failure
trap 'restore_backup; exit 1' ERR

echo "🔄 Updating system packages..."
sudo apt update

echo "📥 Cloning/updating repository..."
backup_existing

# Clone fresh copy
git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

echo "⚙️  Setting up environment..."

# Copy environment file if backup exists
if [ -f "$BACKUP_DIR/.env" ]; then
    echo "📋 Copying existing .env configuration..."
    cp "$BACKUP_DIR/.env" .env
else
    echo "📋 Creating new .env from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials:"
    echo "   nano .env"
    echo ""
    echo "Press Enter when you've configured the .env file..."
    read -r
fi

echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh

echo "🚀 Starting application..."
./scripts/dev-start.sh

# If we get here, deployment was successful
cleanup_backup

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your app should be running at:"
echo "   Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "   Backend:  http://$(hostname -I | awk '{print $1}'):8000"
echo "   API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   Check logs:    tail -f ~/home-budget-app/logs/backend.log"
echo "   Stop servers:  ~/home-budget-app/scripts/dev-stop.sh"
echo "   Restart:       ~/home-budget-app/scripts/dev-start.sh"
echo ""
echo "🎉 Happy budgeting!"
