from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0011_ar_copy_blocks'),
    ]

    operations = [
        # can_import_ifms on Profile — use RunSQL to match the pattern in 0007
        migrations.RunSQL(
            sql="ALTER TABLE ips_profile ADD can_import_ifms BIT NOT NULL DEFAULT 0;",
            reverse_sql="ALTER TABLE ips_profile DROP COLUMN can_import_ifms;",
        ),
        migrations.CreateModel(
            name='IFMSUpload',
            fields=[
                ('id',         models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file',       models.FileField(help_text='Excel file (.xlsx) exported from IFMS', upload_to='ifms/')),
                ('label',      models.CharField(help_text='Descriptive label, e.g. "IFMS 05-21-2026"', max_length=100)),
                ('uploaded_at',models.DateTimeField(auto_now_add=True)),
                ('is_active',  models.BooleanField(
                    default=True,
                    help_text='Only one upload should be active at a time. Saving a new active upload automatically deactivates the previous one.'
                )),
            ],
            options={
                'verbose_name': 'IFMS Upload',
                'verbose_name_plural': 'IFMS Uploads',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
