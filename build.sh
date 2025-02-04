#!/usr/bin/env bash
# exit on error
set -o errexit

# Create required directories
mkdir -p ~/.fonts
mkdir -p ~/.cache/matplotlib
mkdir -p staticfiles/media
mkdir -p staticfiles/images

# Download and install Arial font
wget -O ~/.fonts/arial.ttf https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf
wget -O ~/.fonts/arialbd.ttf https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial_Bold.ttf

# Update font cache
fc-cache -f -v ~/.fonts

# Configure matplotlib to use Arial and optimize memory usage
python -c "
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for better memory management
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Clear existing font cache
fm.fontManager.clear()

# Add Arial fonts explicitly
fm.fontManager.addfont('~/.fonts/arial.ttf')
fm.fontManager.addfont('~/.fonts/arialbd.ttf')

# Configure matplotlib with memory-optimized settings
plt.rcParams['font.family'] = ['Arial']
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['agg.path.chunksize'] = 10000  # Optimize memory usage
"

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Ensure static directories exist
mkdir -p staticfiles/images
mkdir -p staticfiles/media

# Copy logo and ensure proper permissions
if [ -f "static/images/logo.png" ]; then
    cp -f static/images/logo.png staticfiles/images/
    chmod 644 staticfiles/images/logo.png
fi

# Create media directory in staticfiles and set permissions
chmod -R 755 staticfiles/media

echo "Running migrations..."
python manage.py migrate 