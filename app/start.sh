# Fake migrations 0001-0003 so they never block startup.
# Migration 0004 is the single authoritative raw-T-SQL script that
# creates / backfills every ips_* table using IF NOT EXISTS guards.
python manage.py migrate ips 0003 --fake
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
