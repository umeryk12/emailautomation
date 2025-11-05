# Google Cloud Compute Engine Deployment Guide

Complete guide to deploy Email Automation Tool on Google Cloud Compute Engine with Gmail SMTP support.

---

## Prerequisites

1. **Google Cloud Account** with billing enabled
   - Sign up: https://console.cloud.google.com/
   - $300 free credits for 90 days
   - Credit card required

2. **Your Email Credentials**
   - Gmail email address
   - Gmail App Password

---

## Part 1: Create Google Cloud VM (10 minutes)

### Step 1: Create a New Project

1. Go to: https://console.cloud.google.com/
2. Click **"Select a project"** → **"New Project"**
3. Project name: `email-automation-tool`
4. Click **"Create"**
5. Wait for project to be created (30 seconds)

### Step 2: Enable Compute Engine API

1. In your project, go to **"Compute Engine"** → **"VM instances"**
2. Click **"Enable"** (if prompted)
3. Wait 1-2 minutes for API to enable

### Step 3: Create a VM Instance

1. Click **"Create Instance"**
2. Configure:
   - **Name**: `email-automation-vm`
   - **Region**: Choose closest to you (e.g., `us-central1`)
   - **Zone**: `us-central1-a` (or any zone)
   - **Machine type**: 
     - Click **"CHANGE"**
     - Series: **E2**
     - Machine type: **e2-micro** (FREE tier eligible!)
       - 2 vCPU
       - 1 GB RAM
       - Cost: ~$7/month (or FREE with credits)
   - **Boot disk**:
     - Click **"CHANGE"**
     - Operating system: **Ubuntu**
     - Version: **Ubuntu 22.04 LTS**
     - Boot disk type: **Standard persistent disk**
     - Size: **10 GB** (enough for your app)
     - Click **"Select"**
   - **Firewall**:
     - ✅ Check **"Allow HTTP traffic"**
     - ✅ Check **"Allow HTTPS traffic"**
3. Click **"Create"**
4. Wait 1-2 minutes for VM to start

### Step 4: Set Up Firewall Rule for Port 5000

1. Go to **"VPC network"** → **"Firewall"**
2. Click **"Create Firewall Rule"**
3. Configure:
   - **Name**: `allow-flask-5000`
   - **Targets**: All instances in the network
   - **Source IP ranges**: `0.0.0.0/0`
   - **Protocols and ports**: 
     - ✅ Specified protocols and ports
     - **tcp**: `5000`
4. Click **"Create"**

---

## Part 2: Deploy Application (15 minutes)

### Step 5: Connect to Your VM

1. In **Compute Engine** → **VM instances**
2. Find your VM: `email-automation-vm`
3. Click **"SSH"** button (opens browser terminal)
4. A terminal window will open - you're now connected!

### Step 6: Install Dependencies

In the SSH terminal, run these commands one by one:

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and tools
sudo apt install -y python3 python3-pip python3-venv git

# Install PostgreSQL (optional, SQLite works too)
sudo apt install -y postgresql postgresql-contrib

# Check installations
python3 --version
git --version
```

### Step 7: Clone Your Repository

```bash
# Clone your repo
git clone https://github.com/umeryk12/emailautomation.git
cd emailautomation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 8: Set Up Environment Variables

```bash
# Create .env file
nano .env
```

Paste this (replace with your actual values):

```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///instance/email_automation.db
PORT=5000
```

**Press**: `Ctrl+O` (save), `Enter`, `Ctrl+X` (exit)

### Step 9: Create Database

```bash
# Create instance directory
mkdir -p instance

# Initialize database
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created!')"
```

### Step 10: Run Application

```bash
# Run with Gunicorn
gunicorn -c gunicorn_config.py app:app
```

Your app is now running! Keep this terminal open.

### Step 11: Access Your Application

1. Go back to **Compute Engine** → **VM instances**
2. Find your VM's **External IP** (e.g., `34.123.45.67`)
3. Open in browser: `http://YOUR_EXTERNAL_IP:5000`
4. You should see your app! 🎉

---

## Part 3: Keep App Running 24/7 (10 minutes)

### Step 12: Set Up Systemd Service

Open a **NEW SSH session** to your VM, then:

```bash
# Navigate to app directory
cd ~/emailautomation

# Create systemd service file
sudo nano /etc/systemd/system/email-automation.service
```

Paste this:

```ini
[Unit]
Description=Email Automation Tool
After=network.target

[Service]
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/emailautomation
Environment="PATH=/home/YOUR_USERNAME/emailautomation/venv/bin"
ExecStart=/home/YOUR_USERNAME/emailautomation/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME`** with your actual username:
```bash
# Get your username
whoami
```

**Press**: `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 13: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable email-automation

# Start service
sudo systemctl start email-automation

# Check status
sudo systemctl status email-automation
```

You should see **"active (running)"** in green! ✅

### Step 14: Useful Commands

```bash
# View logs
sudo journalctl -u email-automation -f

# Restart service
sudo systemctl restart email-automation

# Stop service
sudo systemctl stop email-automation

# Check status
sudo systemctl status email-automation
```

---

## Part 4: Set Up Domain (Optional, 10 minutes)

### Step 15: Reserve Static IP

1. Go to **VPC network** → **IP addresses**
2. Click **"Reserve External Static Address"**
3. Name: `email-automation-ip`
4. Attached to: `email-automation-vm`
5. Click **"Reserve"**

Your VM now has a permanent IP!

### Step 16: Point Domain (If you have one)

1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Add **A Record**:
   - Type: `A`
   - Host: `@` (or subdomain like `email`)
   - Value: Your static IP
   - TTL: 3600

Wait 5-60 minutes for DNS to propagate.

---

## Part 5: Configure Application (5 minutes)

### Step 17: Sign Up and Configure

1. Go to: `http://YOUR_EXTERNAL_IP:5000`
2. Click **"Sign Up"**
3. Create account
4. In **Email Configuration**:
   - Select: **Gmail SMTP** (works on Google Cloud!)
   - Email: `umer990088u@gmail.com`
   - App Password: (your Gmail app password)
   - Sender Name: `khan`
   - SMTP Server: `smtp.gmail.com`
   - Port: **465** (SSL)
5. Click **"Save Email Settings"**

### Step 18: Test Campaign

1. Select **"YC Startups"**
2. Limit: **5** (for testing)
3. Template: **Use Default**
4. Click **"Start Campaign"**

Watch the logs:
```bash
sudo journalctl -u email-automation -f
```

You should see:
```
✅ Connected to SMTP server using SSL (port 465)
✅ Login successful!
✅ Email sent to xxx@yyy.com
📊 Progress - Sent: 1, Failed: 0
```

---

## Costs Estimate

### Free Tier (with $300 credits):
- **e2-micro VM**: FREE for 1 instance (always)
- **10 GB storage**: FREE (30 GB free)
- **Egress**: 1 GB/month FREE
- **Total**: $0/month for first 90 days!

### After Free Credits:
- **e2-micro VM**: ~$7/month
- **Static IP**: $0 (if attached to running VM)
- **Total**: ~$7-10/month

---

## Troubleshooting

### App not accessible:
```bash
# Check if service is running
sudo systemctl status email-automation

# Check firewall rules in Google Cloud Console
# Make sure port 5000 is open
```

### Gmail SMTP not working:
```bash
# Test connection
curl -v smtp.gmail.com:465

# Check logs
sudo journalctl -u email-automation -f | grep -i smtp
```

### Update app after code changes:
```bash
cd ~/emailautomation
source venv/bin/activate
git pull
pip install -r requirements.txt
sudo systemctl restart email-automation
```

---

## Security Best Practices

1. **Enable HTTPS** (use Nginx + Let's Encrypt)
2. **Set strong SECRET_KEY** in .env
3. **Enable UFW firewall**:
   ```bash
   sudo ufw allow 22
   sudo ufw allow 5000
   sudo ufw enable
   ```
4. **Regular updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## Summary

✅ Google Cloud Compute Engine VM created  
✅ Ubuntu 22.04 installed  
✅ Python app deployed  
✅ Gmail SMTP working (ports 465/587 open!)  
✅ App running 24/7 with systemd  
✅ Cost: FREE with credits, then ~$7-10/month  

Your email automation tool is now live on Google Cloud! 🚀

