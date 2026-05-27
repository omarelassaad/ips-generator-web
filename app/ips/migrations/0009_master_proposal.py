from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0008_add_cds_form3_site_document'),
    ]

    operations = [
        # Add can_use_master_proposals flag to Profile via raw SQL (consistent with 0007)
        migrations.RunSQL(
            sql="ALTER TABLE ips_profile ADD can_use_master_proposals BIT NOT NULL DEFAULT 0;",
            reverse_sql="ALTER TABLE ips_profile DROP COLUMN can_use_master_proposals;",
        ),

        # Create MasterProposal table
        migrations.CreateModel(
            name='MasterProposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True, default='', help_text='Short description shown to advisors')),
                ('data', models.TextField(help_text='JSON list of account rows (same format as SavedProposal.data)')),
                ('risk_profile_override', models.CharField(blank=True, default='', max_length=100)),
                ('portfolio_override', models.CharField(blank=True, default='', max_length=100)),
                ('is_active', models.BooleanField(default=True, help_text='Inactive proposals are hidden from advisors')),
                ('display_order', models.PositiveSmallIntegerField(default=0, help_text='Lower = displayed first')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Master Proposal',
                'verbose_name_plural': 'Master Proposals',
                'ordering': ['display_order', 'label'],
            },
        ),
    ]
