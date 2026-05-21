"""
Comprehensive migration — the single source of truth for all ips tables.

On Azure SQL: start.sh fakes 0001-0003, this migration runs raw T-SQL
              with IF OBJECT_ID IS NULL guards to create every table.
On SQLite:    start.sh runs all migrations normally; this migration uses
              Django's schema editor to create any tables that are still missing.
"""
from django.db import migrations


def ensure_all_ips_tables(apps, schema_editor):
    from django.db import connection

    # ── SQLite path (local testing) ───────────────────────────────────────────
    # Use plain CREATE TABLE IF NOT EXISTS — simpler and more reliable than
    # schema_editor.create_model() with historical model objects.
    if connection.vendor == 'sqlite':
        sqlite_statements = [
            # ── core pre-existing models (no prior Django migration) ──────────
            """CREATE TABLE IF NOT EXISTS "ips_profile" (
                "id"          integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "user_id"     integer NOT NULL UNIQUE REFERENCES "auth_user" ("id"),
                "is_approved" bool    NOT NULL DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_questionnaireresponse" (
                "id"       integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                "user_id"  integer      NOT NULL REFERENCES "auth_user" ("id"),
                "question" varchar(255) NOT NULL DEFAULT 'Unknown',
                "answer"   varchar(255),
                "score"    integer      NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_choosemyselfdata" (
                "id"             integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                "user_id"        integer      NOT NULL REFERENCES "auth_user" ("id"),
                "account_owner"  varchar(255) NOT NULL,
                "account_type"   varchar(50)  NOT NULL,
                "amount"         decimal      NOT NULL,
                "strategy"       text         NOT NULL,
                "version_number" varchar(50)  NOT NULL DEFAULT 'N/A'
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_letpmchoosedata" (
                "id"              integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                "user_id"         integer      NOT NULL REFERENCES "auth_user" ("id"),
                "account_owner"   varchar(255) NOT NULL,
                "account_type"    varchar(255) NOT NULL,
                "amount"          decimal      NOT NULL,
                "timestamp"       datetime     NOT NULL,
                "additional_info" varchar(255)
            )""",
            # ── returns upload ────────────────────────────────────────────────
            """CREATE TABLE IF NOT EXISTS "ips_returnsupload" (
                "id"             integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "file"           varchar(100) NOT NULL DEFAULT '',
                "as_of_date"     varchar(50)  NOT NULL DEFAULT '',
                "calendar_years" varchar(200) NOT NULL DEFAULT '2025,2024,2023,2022,2021,2020,2019',
                "uploaded_at"    datetime     NOT NULL,
                "is_active"      bool         NOT NULL DEFAULT 1
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_feecategory" (
                "id"   integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" varchar(100) NOT NULL UNIQUE
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_feetier" (
                "id"          integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                "category_id" integer      NOT NULL REFERENCES "ips_feecategory" ("id"),
                "lower"       bigint       NOT NULL,
                "upper"       bigint       NOT NULL,
                "max_fee"     decimal      NOT NULL,
                "max_trailer" decimal      NOT NULL,
                "min_fee"     decimal      NOT NULL,
                "min_trailer" decimal      NOT NULL,
                "admin_fee"   decimal      NOT NULL,
                "order"       smallint     NOT NULL DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_mandate" (
                "id"                   integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name"                 varchar(200) NOT NULL UNIQUE,
                "fee_category_id"      integer      NOT NULL REFERENCES "ips_feecategory" ("id"),
                "cash"                 decimal      NOT NULL DEFAULT 0,
                "fixed_income"         decimal      NOT NULL DEFAULT 0,
                "canadian_equity"      decimal      NOT NULL DEFAULT 0,
                "us_equity"            decimal      NOT NULL DEFAULT 0,
                "international_equity" decimal      NOT NULL DEFAULT 0,
                "alternatives"         decimal      NOT NULL DEFAULT 0,
                "fact_sheet"           varchar(100),
                "disclaimer"           text         NOT NULL DEFAULT '',
                "minimum_investment"   integer      NOT NULL DEFAULT 0,
                "is_active"            bool         NOT NULL DEFAULT 1,
                "display_order"        smallint     NOT NULL DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_portfolioprofile" (
                "id"                       integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name"                     varchar(100) NOT NULL UNIQUE,
                "description"              text         NOT NULL DEFAULT '',
                "order"                    smallint     NOT NULL DEFAULT 0,
                "cash"                     decimal      NOT NULL DEFAULT 0,
                "fixed_income"             decimal      NOT NULL DEFAULT 0,
                "canadian_equity"          decimal      NOT NULL DEFAULT 0,
                "us_equity"               decimal      NOT NULL DEFAULT 0,
                "international_equity"     decimal      NOT NULL DEFAULT 0,
                "alternatives"             decimal      NOT NULL DEFAULT 0,
                "liq_cash"                 decimal      NOT NULL DEFAULT 0,
                "liq_fixed_income"         decimal      NOT NULL DEFAULT 0,
                "liq_canadian_equity"      decimal      NOT NULL DEFAULT 0,
                "liq_us_equity"            decimal      NOT NULL DEFAULT 0,
                "liq_international_equity" decimal      NOT NULL DEFAULT 0,
                "liq_alternatives"         decimal      NOT NULL DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_ipscopyblock" (
                "id"       integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                "category" varchar(50)  NOT NULL,
                "key"      varchar(100) NOT NULL,
                "title"    varchar(200) NOT NULL DEFAULT '',
                "body"     text         NOT NULL DEFAULT '',
                "order"    smallint     NOT NULL DEFAULT 0,
                UNIQUE ("category", "key")
            )""",
            """CREATE TABLE IF NOT EXISTS "ips_sitedocument" (
                "id"          integer     NOT NULL PRIMARY KEY AUTOINCREMENT,
                "key"         varchar(50) NOT NULL UNIQUE,
                "label"       varchar(100) NOT NULL DEFAULT '',
                "file"        varchar(100),
                "uploaded_at" datetime    NOT NULL
            )""",
        ]
        with connection.cursor() as cursor:
            for sql in sqlite_statements:
                cursor.execute(sql)
        return

    # ── SQL Server / Azure SQL path ───────────────────────────────────────────

    statements = [

        # ── ips_returnsupload ─────────────────────────────────────────────────
        # Create the table if it doesn't exist at all
        """
        IF OBJECT_ID(N'ips_returnsupload', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_returnsupload (
                id             bigint        IDENTITY(1,1) NOT NULL,
                [file]         nvarchar(100)               NOT NULL DEFAULT '',
                as_of_date     nvarchar(50)                NOT NULL DEFAULT '',
                calendar_years nvarchar(200)               NOT NULL
                    DEFAULT '2025,2024,2023,2022,2021,2020,2019',
                uploaded_at    datetime2                   NOT NULL
                    DEFAULT GETUTCDATE(),
                is_active      bit                         NOT NULL DEFAULT 1,
                CONSTRAINT PK_ips_returnsupload PRIMARY KEY (id)
            )
        END
        """,
        # Backfill missing columns if the table pre-existed
        """
        IF OBJECT_ID(N'ips_returnsupload', N'U') IS NOT NULL
           AND NOT EXISTS (
               SELECT 1 FROM sys.columns
               WHERE object_id = OBJECT_ID('ips_returnsupload')
                 AND name = 'as_of_date'
           )
            ALTER TABLE ips_returnsupload
                ADD as_of_date nvarchar(50) NOT NULL DEFAULT ''
        """,
        """
        IF OBJECT_ID(N'ips_returnsupload', N'U') IS NOT NULL
           AND NOT EXISTS (
               SELECT 1 FROM sys.columns
               WHERE object_id = OBJECT_ID('ips_returnsupload')
                 AND name = 'calendar_years'
           )
            ALTER TABLE ips_returnsupload
                ADD calendar_years nvarchar(200) NOT NULL
                    DEFAULT '2025,2024,2023,2022,2021,2020,2019'
        """,
        """
        IF OBJECT_ID(N'ips_returnsupload', N'U') IS NOT NULL
           AND NOT EXISTS (
               SELECT 1 FROM sys.columns
               WHERE object_id = OBJECT_ID('ips_returnsupload')
                 AND name = 'is_active'
           )
            ALTER TABLE ips_returnsupload
                ADD is_active bit NOT NULL DEFAULT 1
        """,

        # ── ips_feecategory ───────────────────────────────────────────────────
        """
        IF OBJECT_ID(N'ips_feecategory', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_feecategory (
                id   bigint        IDENTITY(1,1) NOT NULL,
                name nvarchar(100)               NOT NULL,
                CONSTRAINT PK_ips_feecategory      PRIMARY KEY (id),
                CONSTRAINT UQ_ips_feecategory_name UNIQUE      (name)
            )
        END
        """,

        # ── ips_feetier ───────────────────────────────────────────────────────
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

        # ── ips_mandate ───────────────────────────────────────────────────────
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

        # ── ips_portfolioprofile ──────────────────────────────────────────────
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

        # ── ips_ipscopyblock ──────────────────────────────────────────────────
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

        # ── ips_sitedocument ──────────────────────────────────────────────────
        """
        IF OBJECT_ID(N'ips_sitedocument', N'U') IS NULL
        BEGIN
            CREATE TABLE ips_sitedocument (
                id          bigint       IDENTITY(1,1) NOT NULL,
                [key]       nvarchar(50)               NOT NULL,
                label       nvarchar(100)              NOT NULL DEFAULT '',
                [file]      nvarchar(100)                       NULL,
                uploaded_at datetime2                  NOT NULL DEFAULT GETUTCDATE(),
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
        migrations.RunPython(ensure_all_ips_tables, migrations.RunPython.noop),
    ]
