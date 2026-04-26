#!/bin/bash
set -e
echo "=== EarnWave Release Script ==="
echo "Running migrations..."
python manage.py migrate --no-input
echo "Collecting static files..."
python manage.py collectstatic --no-input
echo "Seeding data..."
python manage.py seed_data
python manage.py seed_content
echo "=== Release complete ==="
