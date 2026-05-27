from django.db import migrations


def add_ar_first_page(apps, schema_editor):
    SiteDocument = apps.get_model('ips', 'SiteDocument')
    SiteDocument.objects.get_or_create(
        key='ar_first_page',
        defaults={'label': 'Annual Review Cover Page'},
    )


def remove_ar_first_page(apps, schema_editor):
    SiteDocument = apps.get_model('ips', 'SiteDocument')
    SiteDocument.objects.filter(key='ar_first_page').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0009_master_proposal'),
    ]

    operations = [
        migrations.RunPython(add_ar_first_page, reverse_code=remove_ar_first_page),
    ]
