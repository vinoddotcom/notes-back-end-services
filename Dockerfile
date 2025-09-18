FROM python:3.10-slim

WORKDIR /app

# Install system dependencies as root
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY run.py .

# Copy migration script and entrypoint
COPY scripts/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Create a non-root user and set permissions
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose the port the app runs on
EXPOSE 8000

# Switch to non-root user
USER appuser

# Command to run the application
CMD ["/app/docker-entrypoint.sh"]