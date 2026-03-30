#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('${DB_HOST:-db}', ${DB_PORT:-5432}))
    s.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null; then
        echo "PostgreSQL is ready!"
        break
    fi

    ATTEMPT=$((ATTEMPT + 1))
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS - PostgreSQL not ready, waiting..."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "ERROR: Could not connect to PostgreSQL after $MAX_ATTEMPTS attempts"
    exit 1
fi

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 2 core.wsgi:application
