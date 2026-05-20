from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ReturnsUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(help_text='Excel file (.xlsx) with Sheet1 performance data', upload_to='returns/')),
                ('as_of_date', models.CharField(help_text='e.g. "March 31, 2026"', max_length=50)),
                ('calendar_years', models.CharField(
                    default='2025,2024,2023,2022,2021,2020,2019',
                    help_text='Comma-separated list of calendar years to show in the performance table, most recent first.',
                    max_length=200,
                )),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Only one upload should be active at a time. Saving a new active upload automatically deactivates the previous one.',
                )),
            ],
            options={
                'verbose_name': 'Returns Upload',
                'verbose_name_plural': 'Returns Uploads',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
