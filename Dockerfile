# Use official Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable stdout/stderr buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Install system dependencies (SQLite, build tools for any wheels if needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libsqlite3-0 \
       gcc \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install Python dependencies first (leverage Docker layer caching)
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

# Expose port
EXPOSE 5000

# Start with Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
