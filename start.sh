#!/bin/bash
# Production startup script

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run migrations/create database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Start the application
if [ "$FLASK_ENV" = "production" ]; then
    echo "Starting in production mode with Gunicorn..."
    gunicorn -c gunicorn_config.py app:app
else
    echo "Starting in development mode..."
    python app.py
fi

