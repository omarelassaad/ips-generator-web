#!/usr/bin/env bash
# exit on error
set -o errexit

# Create font directory
mkdir -p ~/.fonts

# Download and install Liberation fonts (Arial alternative)
wget https://github.com/liberationfonts/liberation-fonts/files/7261482/liberation-fonts-ttf-2.1.5.tar.gz
tar xvf liberation-fonts-ttf-2.1.5.tar.gz
cp liberation-fonts-ttf-2.1.5/*.ttf ~/.fonts/
fc-cache -f ~/.fonts

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate 