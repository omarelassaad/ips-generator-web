from django.db import migrations, models


def add_missing_returnsupload_columns(apps, schema_editor):
    """
    The ips_returnsupload table may pre-date the as_of_date and calendar_years
    fields (if 0001 was faked via --fake-initial on an existing table).
    Safely add any missing columns — safe to re-run.
    """
    from django.db import connection

    # Check if the table even exists yet; if not, nothing to do (0001 will create it)
    existing_tables = set(connection.introspection.table_names())
    if 'ips_returnsupload' not in existing_tables:
        return

    with connection.cursor() as cursor:
        existing_cols = {
            col.name
            for col in connection.introspection.get_table_description(cursor, 'ips_returnsupload')
        }

    ReturnsUpload = apps.get_model('ips', 'ReturnsUpload')

    # Map field name → field instance from the historical model state
    field_map = {f.attname: f for f in ReturnsUpload._meta.local_fields}

    for col_name in ['as_of_date', 'calendar_years', 'is_active']:
        if col_name not in existing_cols and col_name in field_map:
            schema_editor.add_field(ReturnsUpload, field_map[col_name])


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0002_add_admin_models'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],   # Model state is already correct from 0001
            database_operations=[
                migrations.RunPython(
                    add_missing_returnsupload_columns,
                    migrations.RunPython.noop,
                ),
            ],
        ),
    ]
