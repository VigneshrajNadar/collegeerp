#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate --no-input

# Create admin user (if not exists)
python manage.py create_admin || echo "Admin creation skipped or already exists"
