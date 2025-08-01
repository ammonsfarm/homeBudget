#!/bin/bash

echo "🔧 Setting up .env file for Home Budget App"
echo "==========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"

# Check if .env already exists
if [ -f "$ENV_FILE" ]; then
    echo "📋 .env file already exists"
    echo "Current DATABASE_URL: $(grep '^DATABASE_URL=' "$ENV_FILE" 2>/dev/null || echo 'Not set')"
    echo ""
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Keeping existing .env file"
        exit 0
    fi
fi

# Copy from example
if [ -f "$ENV_EXAMPLE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "📋 Created .env from .env.example"
else
    echo "❌ .env.example not found!"
    exit 1
fi

# Interactive setup
echo ""
echo "🔧 Let's configure your environment variables:"
echo ""

# Database configuration
echo "📊 Database Configuration"
echo "========================="
read -p "Database host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Database port (default: 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}

read -p "Database name (default: home_budget_db): " DB_NAME
DB_NAME=${DB_NAME:-home_budget_db}

read -p "Database user (default: budget_user): " DB_USER
DB_USER=${DB_USER:-budget_user}

read -s -p "Database password: " DB_PASSWORD
echo ""

# JWT Secret
echo ""
echo "🔐 Security Configuration"
echo "========================="
read -p "JWT Secret Key (press Enter to generate): " JWT_SECRET
if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(openssl rand -hex 32)
    echo "Generated JWT secret: $JWT_SECRET"
fi

# Update .env file
DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

# Use sed to update the values
sed -i "s|DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|" "$ENV_FILE"
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$JWT_SECRET|" "$ENV_FILE"

echo ""
echo "✅ .env file configured successfully!"
echo ""
echo "📋 Configuration summary:"
echo "  Database: $DB_HOST:$DB_PORT/$DB_NAME"
echo "  User: $DB_USER"
echo "  JWT Secret: ${JWT_SECRET:0:10}..."
echo ""
echo "🚀 You can now run: ./scripts/dev-start.sh"
