#!/bin/sh
set -e

echo "=== BuggyMan Backend Initializing ==="

# Wait for database if DATABASE_URL or DB_HOST is configured
if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "localhost" ]; then
    echo "Waiting for database host $DB_HOST:$DB_PORT..."
    while ! nc -z "$DB_HOST" "${DB_PORT:-5432}" 2>/dev/null; do
        sleep 1
    done
    echo "Database is ready!"
fi

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static assets
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

# Check whether to run in dev mode or production Gunicorn
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "1" ] || [ "$DEBUG" = "true" ]; then
    echo "Starting in DEBUG mode with Django runserver on 0.0.0.0:8000..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting in PRODUCTION mode with Gunicorn on 0.0.0.0:8000..."
    WORKERS=${GUNICORN_WORKERS:-3}
    THREADS=${GUNICORN_THREADS:-2}
    TIMEOUT=${GUNICORN_TIMEOUT:-120}
    exec gunicorn backend.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "$WORKERS" \
        --threads "$THREADS" \
        --timeout "$TIMEOUT" \
        --access-logfile - \
        --error-logfile -
fi
