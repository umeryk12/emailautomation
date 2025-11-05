#!/bin/bash
# Google Cloud Deployment Script - Automated Setup
# Run this on your Google Cloud VM after SSH connection

set -e  # Exit on error

echo "=================================="
echo "Email Automation Tool - GCP Deploy"
echo "=================================="
echo ""

# Update system
echo "📦 Updating system..."
sudo apt update
sudo apt upgrade -y

# Install dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git nginx

# Clone repository
echo "📥 Cloning repository..."
cd ~
if [ -d "emailautomation" ]; then
    echo "Repository exists, pulling latest..."
    cd emailautomation
    git pull
else
    git clone https://github.com/umeryk12/emailautomation.git
    cd emailautomation
fi

# Create virtual environment
echo "🔧 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create instance directory
echo "📁 Creating database directory..."
mkdir -p instance

# Create .env file
echo "⚙️ Creating environment variables..."
cat > .env << EOF
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:///instance/email_automation.db
PORT=5000
EOF

# Initialize database
echo "🗄️ Initializing database..."
python3 << PYEOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database created successfully!")
PYEOF

# Get username
USERNAME=$(whoami)
APP_DIR=$(pwd)

# Create systemd service
echo "🚀 Creating systemd service..."
sudo tee /etc/systemd/system/email-automation.service > /dev/null << EOF
[Unit]
Description=Email Automation Tool
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "✅ Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable email-automation
sudo systemctl start email-automation

# Wait a moment
sleep 3

# Check status
echo ""
echo "=================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================="
echo ""
sudo systemctl status email-automation --no-pager
echo ""
echo "📍 Your app is running on port 5000"
echo ""
echo "🌐 Access your app at:"
echo "   http://$(curl -s ifconfig.me):5000"
echo ""
echo "📊 View logs with:"
echo "   sudo journalctl -u email-automation -f"
echo ""
echo "🔄 Restart app with:"
echo "   sudo systemctl restart email-automation"
echo ""
echo "=================================="

