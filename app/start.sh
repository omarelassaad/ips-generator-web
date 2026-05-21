# Ensure media subdirectories exist and are writable by the app user.
# This must run at container startup (after volume mount) not at build time.
mkdir -p /usr/src/app/media/returns
mkdir -p /usr/src/app/media/fact_sheets
mkdir -p /usr/src/app/media/site_documents

# For SQLite (local dev): run all migrations normally.
# For Azure SQL (production): fake 0001-0004 since DBA created those tables via SQL script.
if [ "$USE_SQLITE" = "True" ]; then
    python manage.py migrate
    python manage.py seed_data
else
    python manage.py migrate ips 0004 --fake
    python manage.py migrate
fi
python manage.py runserver 0.0.0.0:8000
