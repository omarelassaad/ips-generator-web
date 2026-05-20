from django.db import migrations, models
import django.db.models.deletion


def create_tables_if_needed(apps, schema_editor):
    """
    Create each table using raw T-SQL IF NOT EXISTS so this is safe to re-run.
    NOTE: We use raw cursor SQL instead of schema_editor.create_model() because
    RunPython inside SeparateDatabaseAndState receives from_state.apps (before
    state_operations are applied), so apps.get_model() would raise LookupError.
    On SQLite this is a no-op — migration 0004 handles table creation there.
    """
    from django.db import connection
    if connection.vendor == 'sqlite':
        return  # SQLite: 0004 handles table creation via schema_editor.create_model()
    statements = [
        # ── FeeCategory ──────────────────────────────────────────────────────
        """
        IF OBJECT_ID(N'ips_feecategory', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_feecategory (
                id       bigint IDENTITY(1,1) NOT NULL,
                name     nvarchar(100)        NOT NULL,
                CONSTRAINT PK_ips_feecategory      PRIMARY KEY (id),
                CONSTRAINT UQ_ips_feecategory_name UNIQUE      (name)
            )
        END
        """,
        # ── FeeTier ──────────────────────────────────────────────────────────
        """
        IF OBJECT_ID(N'ips_feetier', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_feetier (
                id          bigint       IDENTITY(1,1) NOT NULL,
                category_id bigint                     NOT NULL,
                lower       bigint                     NOT NULL,
                upper       bigint                     NOT NULL,
                max_fee     decimal(5,2)               NOT NULL,
                max_trailer decimal(5,2)               NOT NULL,
                min_fee     decimal(5,2)               NOT NULL,
                min_trailer decimal(5,2)               NOT NULL,
                admin_fee   decimal(5,2)               NOT NULL,
                [order]     smallint                   NOT NULL DEFAULT 0,
                CONSTRAINT PK_ips_feetier          PRIMARY KEY (id),
                CONSTRAINT FK_ips_feetier_category FOREIGN KEY (category_id)
                    REFERENCES ips_feecategory(id) ON DELETE CASCADE
            )
        END
        """,
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
            WHERE object_id = OBJECT_ID('ips_feetier')
              AND name = 'ips_feetier_category_id_idx'
        )
            CREATE INDEX ips_feetier_category_id_idx ON ips_feetier (category_id)
        """,
        # ── Mandate ──────────────────────────────────────────────────────────
        """
        IF OBJECT_ID(N'ips_mandate', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_mandate (
                id                   bigint       IDENTITY(1,1) NOT NULL,
                name                 nvarchar(200)              NOT NULL,
                fee_category_id      bigint                     NOT NULL,
                cash                 decimal(5,2)               NOT NULL DEFAULT 0,
                fixed_income         decimal(5,2)               NOT NULL DEFAULT 0,
                canadian_equity      decimal(5,2)               NOT NULL DEFAULT 0,
                us_equity            decimal(5,2)               NOT NULL DEFAULT 0,
                international_equity decimal(5,2)               NOT NULL DEFAULT 0,
                alternatives         decimal(5,2)               NOT NULL DEFAULT 0,
                fact_sheet           nvarchar(100)                       NULL,
                disclaimer           nvarchar(max)              NOT NULL DEFAULT '',
                minimum_investment   int                        NOT NULL DEFAULT 0,
                is_active            bit                        NOT NULL DEFAULT 1,
                display_order        smallint                   NOT NULL DEFAULT 0,
                CONSTRAINT PK_ips_mandate            PRIMARY KEY (id),
                CONSTRAINT UQ_ips_mandate_name       UNIQUE      (name),
                CONSTRAINT FK_ips_mandate_feecategory FOREIGN KEY (fee_category_id)
                    REFERENCES ips_feecategory(id)
            )
        END
        """,
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
            WHERE object_id = OBJECT_ID('ips_mandate')
              AND name = 'ips_mandate_fee_category_id_idx'
        )
            CREATE INDEX ips_mandate_fee_category_id_idx ON ips_mandate (fee_category_id)
        """,
        # ── PortfolioProfile ─────────────────────────────────────────────────
        """
        IF OBJECT_ID(N'ips_portfolioprofile', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_portfolioprofile (
                id                   bigint       IDENTITY(1,1) NOT NULL,
                name                 nvarchar(100)              NOT NULL,
                description          nvarchar(max)              NOT NULL DEFAULT '',
                [order]              smallint                   NOT NULL DEFAULT 0,
                cash                 decimal(5,2)               NOT NULL DEFAULT 0,
                fixed_income         decimal(5,2)               NOT NULL DEFAULT 0,
                canadian_equity      decimal(5,2)               NOT NULL DEFAULT 0,
                us_equity            decimal(5,2)               NOT NULL DEFAULT 0,
                international_equity decimal(5,2)               NOT NULL DEFAULT 0,
                alternatives         decimal(5,2)               NOT NULL DEFAULT 0,
                liq_cash                 decimal(5,2)           NOT NULL DEFAULT 0,
                liq_fixed_income         decimal(5,2)           NOT NULL DEFAULT 0,
                liq_canadian_equity      decimal(5,2)           NOT NULL DEFAULT 0,
                liq_us_equity            decimal(5,2)           NOT NULL DEFAULT 0,
                liq_international_equity decimal(5,2)           NOT NULL DEFAULT 0,
                liq_alternatives         decimal(5,2)           NOT NULL DEFAULT 0,
                CONSTRAINT PK_ips_portfolioprofile      PRIMARY KEY (id),
                CONSTRAINT UQ_ips_portfolioprofile_name UNIQUE      (name)
            )
        END
        """,
        # ── IPSCopyBlock ─────────────────────────────────────────────────────
        """
        IF OBJECT_ID(N'ips_ipscopyblock', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_ipscopyblock (
                id       bigint       IDENTITY(1,1) NOT NULL,
                category nvarchar(50)               NOT NULL,
                [key]    nvarchar(100)              NOT NULL,
                title    nvarchar(200)              NOT NULL DEFAULT '',
                body     nvarchar(max)              NOT NULL DEFAULT '',
                [order]  smallint                   NOT NULL DEFAULT 0,
                CONSTRAINT PK_ips_ipscopyblock              PRIMARY KEY (id),
                CONSTRAINT UQ_ips_ipscopyblock_category_key UNIQUE (category, [key])
            )
        END
        """,
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
            WHERE object_id = OBJECT_ID('ips_ipscopyblock')
              AND name = 'ips_ipscopyblock_category_idx'
        )
            CREATE INDEX ips_ipscopyblock_category_idx ON ips_ipscopyblock (category)
        """,
        # ── SiteDocument ─────────────────────────────────────────────────────
        """
        IF OBJECT_ID(N'ips_sitedocument', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_sitedocument (
                id          bigint       IDENTITY(1,1) NOT NULL,
                [key]       nvarchar(50)               NOT NULL,
                label       nvarchar(100)              NOT NULL DEFAULT '',
                file        nvarchar(100)                       NULL,
                uploaded_at datetime2                  NOT NULL,
                CONSTRAINT PK_ips_sitedocument      PRIMARY KEY (id),
                CONSTRAINT UQ_ips_sitedocument_key  UNIQUE ([key])
            )
        END
        """,
    ]
    with connection.cursor() as cursor:
        for sql in statements:
            cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0001_returns_upload'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # State operations: tell Django's ORM about all 6 models
            state_operations=[
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
                            db_index=True, max_length=50,
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
                migrations.CreateModel(
                    name='SiteDocument',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('key', models.CharField(
                            choices=[
                                ('ips_first_page', 'IPS Cover Page'),
                                ('ips_last_page', 'IPS Back Page'),
                            ],
                            max_length=50, unique=True,
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
            ],
            # Database operations: conditionally create tables
            database_operations=[
                migrations.RunPython(create_tables_if_needed, migrations.RunPython.noop),
            ],
        ),
    ]
