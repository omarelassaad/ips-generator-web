if [ "${USE_SQLITE:-false}" = "true" ]; then
    # SQLite (local testing): run all migrations normally — no special faking needed.
    python manage.py migrate
else
    # Azure SQL: fake 0001-0003 to skip migrations that require CREATE TABLE rights.
    # Migration 0004 uses raw T-SQL with IF OBJECT_ID IS NULL to create every table.
    python manage.py migrate ips 0003 --fake
    python manage.py migrate
fi

python manage.py runserver 0.0.0.0:8000
