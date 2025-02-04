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

# Configure matplotlib to use Arial
python -c "
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import matplotlib.font_manager as fm
# Force matplotlib to find the fonts
for font in fm.findSystemFonts():
    try:
        fm.fontManager.addfont(font)
    except:
        continue
plt.rcParams['font.family'] = ['Arial']
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False
"

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Copy logo to static directory if it exists
if [ -f "static/images/logo.png" ]; then
    cp static/images/logo.png staticfiles/images/
fi

echo "Running migrations..."
python manage.py migrate 