if [ "${USE_SQLITE:-false}" = "true" ]; then
    # SQLite (local testing): run all migrations normally.
    python manage.py migrate

    # Create a superuser automatically so the admin is accessible right away.
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created — login: admin / admin')
"
else
    # Azure SQL: fake 0001-0003 to skip migrations that require CREATE TABLE rights.
    # Migration 0004 uses raw T-SQL with IF OBJECT_ID IS NULL to create every table.
    python manage.py migrate ips 0003 --fake
    python manage.py migrate
fi

python manage.py runserver 0.0.0.0:8000
