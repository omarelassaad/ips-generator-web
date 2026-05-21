# Fake migrations 0001-0004 (tables created by DBA via create_ips_tables.sql).
# Migrations 0005+ run normally — the service account now has CREATE TABLE rights.
python manage.py migrate ips 0004 --fake
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
