from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0001_returns_upload'),
    ]

    operations = [
        # FeeCategory
        migrations.CreateModel(
            name='FeeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Fee Category',
                'verbose_name_plural': 'Fee Categories',
                'ordering': ['name'],
            },
        ),
        # FeeTier
        migrations.CreateModel(
            name='FeeTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiers', to='ips.feecategory')),
                ('lower', models.BigIntegerField(help_text='Lower AUM bound (inclusive, $)')),
                ('upper', models.BigIntegerField(help_text='Upper AUM bound (inclusive, $). Use 999999999 for no limit.')),
                ('max_fee', models.DecimalField(decimal_places=2, help_text='Max total fee %', max_digits=5)),
                ('max_trailer', models.DecimalField(decimal_places=2, help_text='Max trailer fee %', max_digits=5)),
                ('min_fee', models.DecimalField(decimal_places=2, help_text='Min total fee %', max_digits=5)),
                ('min_trailer', models.DecimalField(decimal_places=2, help_text='Min trailer fee %', max_digits=5)),
                ('admin_fee', models.DecimalField(decimal_places=2, help_text='Admin/platform fee %', max_digits=5)),
                ('order', models.PositiveSmallIntegerField(default=0, help_text='Display order within category')),
            ],
            options={
                'verbose_name': 'Fee Tier',
                'verbose_name_plural': 'Fee Tiers',
                'ordering': ['category', 'order', 'lower'],
            },
        ),
        # Mandate
        migrations.CreateModel(
            name='Mandate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('fee_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='mandates', to='ips.feecategory')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('fixed_income', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('canadian_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('us_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('international_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('alternatives', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('fact_sheet', models.FileField(blank=True, help_text='PDF fact sheet for this mandate', null=True, upload_to='fact_sheets/')),
                ('disclaimer', models.TextField(blank=True, default='', help_text='Strategy-specific disclaimer (HTML allowed). Leave blank if none.')),
                ('minimum_investment', models.PositiveIntegerField(default=0, help_text='Minimum investment amount ($) enforced in the IPS form')),
                ('is_active', models.BooleanField(default=True, help_text='Inactive mandates are hidden from the IPS form')),
                ('display_order', models.PositiveSmallIntegerField(default=0, help_text='Order in dropdown lists (lower = first)')),
            ],
            options={
                'verbose_name': 'Mandate',
                'verbose_name_plural': 'Mandates',
                'ordering': ['display_order', 'name'],
            },
        ),
        # PortfolioProfile
        migrations.CreateModel(
            name='PortfolioProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g. Income, Balanced, Growth', max_length=100, unique=True)),
                ('description', models.TextField(help_text='Narrative shown in the IPS document')),
                ('order', models.PositiveSmallIntegerField(default=0, help_text='Display order (lower = first)')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('fixed_income', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('canadian_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('us_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('international_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('alternatives', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('liq_cash', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Cash (liquidity-adjusted)')),
                ('liq_fixed_income', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Fixed Income (liquidity-adjusted)')),
                ('liq_canadian_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Canadian Equity (liquidity-adjusted)')),
                ('liq_us_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='U.S. Equity (liquidity-adjusted)')),
                ('liq_international_equity', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Intl Equity (liquidity-adjusted)')),
                ('liq_alternatives', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Alternatives (liquidity-adjusted)')),
            ],
            options={
                'verbose_name': 'Portfolio Profile',
                'verbose_name_plural': 'Portfolio Profiles',
                'ordering': ['order', 'name'],
            },
        ),
        # IPSCopyBlock
        migrations.CreateModel(
            name='IPSCopyBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(
                    choices=[
                        ('risk_profile', 'Risk Profile'),
                        ('investment_goal', 'Investment Goal'),
                        ('time_horizon', 'Time Horizon'),
                        ('liquidity_needs', 'Liquidity Needs'),
                        ('responsible_investing', 'Responsible Investing'),
                        ('risk_analytics_disclaimer', 'Risk Analytics Disclaimer'),
                    ],
                    db_index=True,
                    max_length=50,
                )),
                ('key', models.CharField(help_text="Lookup key used in code (e.g. 'Low Risk', 'Retirement', '1', 'RI')", max_length=100)),
                ('title', models.CharField(blank=True, default='', help_text='Short label shown as a heading (leave blank if not needed)', max_length=200)),
                ('body', models.TextField(help_text='Main paragraph text. HTML tags allowed.')),
                ('order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'IPS Copy Block',
                'verbose_name_plural': 'IPS Copy Blocks',
                'ordering': ['category', 'order', 'key'],
                'unique_together': {('category', 'key')},
            },
        ),
        # SiteDocument
        migrations.CreateModel(
            name='SiteDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(
                    choices=[
                        ('ips_first_page', 'IPS Cover Page'),
                        ('ips_last_page', 'IPS Back Page'),
                    ],
                    max_length=50,
                    unique=True,
                )),
                ('label', models.CharField(max_length=100)),
                ('file', models.FileField(blank=True, help_text='Upload a PDF to replace the current file', null=True, upload_to='site_documents/')),
                ('uploaded_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Site Document',
                'verbose_name_plural': 'Site Documents',
            },
        ),
    ]
