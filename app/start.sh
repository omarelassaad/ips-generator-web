# Fake migrations 0001-0003 (tables created by DBA via create_ips_tables.sql).
# Migration 0004 is a no-op once the DBA script has been run.
python manage.py migrate ips 0003 --fake
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
