#!/bin/bash

# Home Budget App - Ubuntu 22.04.5 Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🏠 Setting up Home Budget App on Ubuntu 22.04.5..."
echo "=================================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "🔧 Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    unzip \
    vim \
    htop \
    ufw \
    fail2ban

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install Node.js 18 LTS
echo "📦 Installing Node.js 18 LTS..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL 14
echo "🐘 Installing PostgreSQL 14..."
sudo apt install -y postgresql postgresql-contrib postgresql-client
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Redis (for caching and sessions)
echo "📮 Installing Redis..."
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install Docker and Docker Compose
echo "🐳 Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER

# Install Nginx (for reverse proxy)
echo "🌐 Installing Nginx..."
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Setup firewall
echo "🔒 Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 5432  # PostgreSQL
sudo ufw allow 3000  # Development frontend
sudo ufw allow 8000  # Development backend
sudo ufw --force enable

# Configure fail2ban
echo "🛡️  Configuring fail2ban..."
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# Create application user
echo "👤 Creating application user..."
sudo useradd -m -s /bin/bash budgetapp || true
sudo usermod -aG docker budgetapp

# Create application directories
echo "📁 Creating application directories..."
sudo mkdir -p /opt/budget-app
sudo chown budgetapp:budgetapp /opt/budget-app
sudo mkdir -p /var/log/budget-app
sudo chown budgetapp:budgetapp /var/log/budget-app

# Install Python packages globally needed
echo "🐍 Installing global Python packages..."
sudo pip3 install --upgrade pip
sudo pip3 install virtualenv

# Install global Node.js packages
echo "📦 Installing global Node.js packages..."
sudo npm install -g pm2 yarn

# Setup PostgreSQL database and user
echo "🐘 Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE USER budgetapp WITH PASSWORD 'secure_password_change_me';" || true
sudo -u postgres psql -c "CREATE DATABASE budget_app OWNER budgetapp;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE budget_app TO budgetapp;" || true

# Configure PostgreSQL for security
echo "🔒 Securing PostgreSQL..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/14/main/postgresql.conf
sudo systemctl restart postgresql

# Setup SSL certificates directory
echo "🔐 Setting up SSL certificates directory..."
sudo mkdir -p /etc/ssl/budget-app
sudo chown root:budgetapp /etc/ssl/budget-app
sudo chmod 750 /etc/ssl/budget-app

echo "✅ Ubuntu setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your project to /opt/budget-app"
echo "2. Run the database initialization script"
echo "3. Configure environment variables"
echo "4. Start the development servers"
echo ""
echo "⚠️  Important: Change the default PostgreSQL password!"
echo "   sudo -u postgres psql -c \"ALTER USER budgetapp PASSWORD 'your_secure_password';\""
echo ""
echo "🔄 Please log out and back in for Docker group changes to take effect."
