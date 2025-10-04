# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for psycopg2 and others)
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip, setuptools, wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy scripts and make them executable
COPY deployment/wait-for-postgres.sh /wait-for-postgres.sh
COPY deployment/entrypoint.sh /entrypoint.sh
RUN chmod +x /wait-for-postgres.sh /entrypoint.sh

EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]