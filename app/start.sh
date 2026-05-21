# Fake all ips migrations — tables are created by the DBA running create_ips_tables.sql.
# This prevents the service account (which lacks CREATE TABLE rights) from failing on startup.
python manage.py migrate ips 0005 --fake
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
