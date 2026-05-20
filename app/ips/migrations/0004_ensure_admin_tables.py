"""
Safety-net migration: creates the 6 admin tables with raw T-SQL IF NOT EXISTS.

If migration 0002 was already marked applied in django_migrations (from a
previous broken run where the RunPython raised LookupError but the transaction
record somehow survived), this migration will still create any missing tables.
"""
from django.db import migrations


def ensure_admin_tables(apps, schema_editor):
    """Idempotent raw-SQL table creation for all 6 admin models."""
    from django.db import connection

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
                CONSTRAINT PK_ips_mandate             PRIMARY KEY (id),
                CONSTRAINT UQ_ips_mandate_name        UNIQUE      (name),
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
                id                       bigint       IDENTITY(1,1) NOT NULL,
                name                     nvarchar(100)              NOT NULL,
                description              nvarchar(max)              NOT NULL DEFAULT '',
                [order]                  smallint                   NOT NULL DEFAULT 0,
                cash                     decimal(5,2)               NOT NULL DEFAULT 0,
                fixed_income             decimal(5,2)               NOT NULL DEFAULT 0,
                canadian_equity          decimal(5,2)               NOT NULL DEFAULT 0,
                us_equity                decimal(5,2)               NOT NULL DEFAULT 0,
                international_equity     decimal(5,2)               NOT NULL DEFAULT 0,
                alternatives             decimal(5,2)               NOT NULL DEFAULT 0,
                liq_cash                 decimal(5,2)               NOT NULL DEFAULT 0,
                liq_fixed_income         decimal(5,2)               NOT NULL DEFAULT 0,
                liq_canadian_equity      decimal(5,2)               NOT NULL DEFAULT 0,
                liq_us_equity            decimal(5,2)               NOT NULL DEFAULT 0,
                liq_international_equity decimal(5,2)               NOT NULL DEFAULT 0,
                liq_alternatives         decimal(5,2)               NOT NULL DEFAULT 0,
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
                CONSTRAINT PK_ips_sitedocument     PRIMARY KEY (id),
                CONSTRAINT UQ_ips_sitedocument_key UNIQUE ([key])
            )
        END
        """,
    ]

    with connection.cursor() as cursor:
        for sql in statements:
            cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0003_fix_returnsupload_columns'),
    ]

    operations = [
        migrations.RunPython(ensure_admin_tables, migrations.RunPython.noop),
    ]
