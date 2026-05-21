from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0006_create_savedproposal_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='can_override_fee',
            field=models.BooleanField(
                default=False,
                help_text='Allow this user to override the calculated fee and trailer',
            ),
        ),
    ]
