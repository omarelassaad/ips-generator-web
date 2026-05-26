from django.db import migrations


def add_cds_form3(apps, schema_editor):
    SiteDocument = apps.get_model('ips', 'SiteDocument')
    SiteDocument.objects.get_or_create(
        key='cds_form_3',
        defaults={'label': 'CDS Form 3 (Client-directed Sleeve Request)'},
    )


def remove_cds_form3(apps, schema_editor):
    SiteDocument = apps.get_model('ips', 'SiteDocument')
    SiteDocument.objects.filter(key='cds_form_3').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0007_profile_can_override_fee'),
    ]

    operations = [
        migrations.RunPython(add_cds_form3, reverse_code=remove_cds_form3),
    ]
