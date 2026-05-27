from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0012_ifms_upload'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE ips_profile ADD can_import_ifms_ips BIT NOT NULL DEFAULT 0;",
            reverse_sql="ALTER TABLE ips_profile DROP COLUMN can_import_ifms_ips;",
        ),
    ]
