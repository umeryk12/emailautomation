# Gunicorn configuration file
import multiprocessing
import os

# Server socket - bind to the port provided by the platform (e.g., Railway)
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes - Reduced for Railway free tier
workers = 2  # Reduced from cpu_count * 2 + 1 to prevent OOM
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "email_automation"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

