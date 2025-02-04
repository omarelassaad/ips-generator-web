#!/usr/bin/env bash
# exit on error
set -o errexit

# Create required directories
FONT_DIR="/opt/render/.fonts"
mkdir -p "$FONT_DIR"
mkdir -p ~/.cache/matplotlib
mkdir -p staticfiles/media

# Install system fonts
apt-get update && apt-get install -y fonts-liberation ttf-mscorefonts-installer fontconfig

# Download and install Arial font
wget -O "$FONT_DIR/arial.ttf" https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf
wget -O "$FONT_DIR/arialbd.ttf" https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial_Bold.ttf

# Copy fonts to system font directory
cp "$FONT_DIR"/*.ttf /usr/local/share/fonts/

# Update font cache
fc-cache -f -v

echo "Installing Python dependencies..."
pip install -r requirements.txt

# Now configure matplotlib after dependencies are installed
python -c "
import matplotlib
import os
matplotlib.use('Agg')  # Use Agg backend for better memory management
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Clear and rebuild the font cache
import shutil
cache_dir = matplotlib.get_cachedir()
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
os.makedirs(cache_dir)

# Force matplotlib to find fonts
fm.findSystemFonts(fontpaths=['/usr/local/share/fonts', '/opt/render/.fonts'])

# Configure matplotlib settings
plt.rcParams.update({
    'font.family': 'Arial',
    'font.sans-serif': ['Arial', 'Liberation Sans', 'DejaVu Sans'],
    'font.size': 10,
    'axes.unicode_minus': False,
    'agg.path.chunksize': 10000
})

# Verify font availability
print('Available fonts:', [f.name for f in fm.fontManager.ttflist])
"

# Clear static files directory first
rm -rf staticfiles/*

echo "Collecting static files..."
python manage.py collectstatic --no-input

# Ensure media directory exists with proper permissions
mkdir -p staticfiles/media
chmod -R 755 staticfiles

# Copy any existing media files to staticfiles/media
if [ -d "media" ]; then
    echo "Copying media files..."
    cp -rfv media/* staticfiles/media/ || true
fi

# Set proper permissions
find staticfiles -type f -exec chmod 644 {} \;
find staticfiles -type d -exec chmod 755 {} \;

# Verify static files
echo "Verifying static files structure:"
ls -la staticfiles/

# Print the tree structure of both directories for comparison
echo "Current static files source structure:"
find static -type f
echo "Current staticfiles (collected) structure:"
find staticfiles -type f

echo "Running migrations..."
python manage.py migrate 