#!/bin/bash
set -e

# Function to wait for database connection
wait_for_db() {
    if [ "$USE_AURORA" = "true" ]; then
        echo "Waiting for Aurora database connection..."
        DB_HOST=$AURORA_WRITER_ENDPOINT
        DB_PORT=$AURORA_PORT
        DB_USER=$AURORA_USER
        DB_PASSWORD=$AURORA_PASSWORD
        DB_NAME=$AURORA_DB
    else
        echo "Waiting for PostgreSQL database connection..."
        DB_HOST=$POSTGRES_SERVER
        DB_PORT=5432
        DB_USER=$POSTGRES_USER
        DB_PASSWORD=$POSTGRES_PASSWORD
        DB_NAME=$POSTGRES_DB
    fi

    echo "Trying to connect to database at $DB_HOST:$DB_PORT..."
    
    # Wait for database to be ready
    until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
        >&2 echo "Database is unavailable - sleeping"
        sleep 5
    done

    >&2 echo "Database is up - continuing"
}

# Wait for database connection
echo "Checking database connection..."
wait_for_db

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI application..."
exec python run.py