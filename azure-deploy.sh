#!/bin/bash

echo "Starting deployment script..."

# exit on error
set -o errexit

# Create required directories
echo "Creating required directories..."
mkdir -p staticfiles
mkdir -p staticfiles/media
mkdir -p static/images

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
# Accept EULA for MS fonts
echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections
apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    build-essential \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    shared-mime-info \
    libcairo2 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    ttf-mscorefonts-installer

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Configure matplotlib
echo "Configuring matplotlib..."
python -c "
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Basic configuration with Arial
plt.rcParams.update({
    'font.family': ['Arial'],
    'font.size': 10,
})

# Verify fonts
print('Available fonts:', [f.name for f in fm.fontManager.ttflist if 'Arial' in f.name])
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Set proper permissions
echo "Setting permissions..."
chmod -R 755 staticfiles
find staticfiles -type f -exec chmod 644 {} \;

# Verify directories
echo "Verifying directory structure:"
ls -la staticfiles/
ls -la staticfiles/media/

# Apply migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if environment variables are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || true
fi

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn ips_generator.wsgi:application --timeout 120 --workers 2 --threads 2 --worker-class gthread --bind=0.0.0.0:8000

echo "Deployment script completed." 