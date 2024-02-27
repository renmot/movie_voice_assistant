#!/usr/bin/env bash

set -e

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput

# Copy data from SQLite to Postgres
bash -c "cd sqlite_to_postgres && python load_data.py"

# chown www-data:www-data /var/log

# Start server
echo "Starting server"
uwsgi --strict --ini /opt/app/uwsgi.ini
