#!/usr/bin/env bash
# exit on error
set -o errexit

# Create required directories
echo "Creating required directories..."
mkdir -p staticfiles
mkdir -p staticfiles/media
mkdir -p staticfiles/images
mkdir -p static/images

# Install required system packages
echo "Installing system packages..."
apt-get update && apt-get install -y fonts-liberation

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Simple matplotlib configuration
python -c "
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Basic configuration with explicit Liberation Sans
plt.rcParams.update({
    'font.family': ['Liberation Sans'],
    'font.size': 10,
})

# Verify fonts
print('Available fonts:', [f.name for f in fm.fontManager.ttflist if 'Sans' in f.name])
"

# Clear and collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Set proper permissions
echo "Setting permissions..."
chmod -R 755 staticfiles
find staticfiles -type f -exec chmod 644 {} \;

# Verify static files
echo "Verifying static files structure:"
ls -la staticfiles/
ls -la staticfiles/images/

echo "Running migrations..."
python manage.py migrate 