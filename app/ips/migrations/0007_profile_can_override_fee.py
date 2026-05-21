from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0006_create_savedproposal_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE ips_profile ADD can_override_fee BIT NOT NULL DEFAULT 0;",
            reverse_sql="ALTER TABLE ips_profile DROP COLUMN can_override_fee;",
        ),
    ]
