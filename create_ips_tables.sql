-- ============================================================
-- IPS application — one-time table creation script
-- Run this as a user with CREATE TABLE rights (db_owner / db_ddladmin).
-- Every statement is idempotent: safe to re-run if some tables
-- already exist.
-- ============================================================

-- ── ips_returnsupload ─────────────────────────────────────
IF OBJECT_ID(N'ips_returnsupload', N'U') IS NULL
BEGIN
    CREATE TABLE ips_returnsupload (
        id             bigint        IDENTITY(1,1) NOT NULL,
        [file]         nvarchar(100)               NOT NULL DEFAULT '',
        as_of_date     nvarchar(50)                NOT NULL DEFAULT '',
        calendar_years nvarchar(200)               NOT NULL
            DEFAULT '2025,2024,2023,2022,2021,2020,2019',
        uploaded_at    datetime2                   NOT NULL DEFAULT GETUTCDATE(),
        is_active      bit                         NOT NULL DEFAULT 1,
        CONSTRAINT PK_ips_returnsupload PRIMARY KEY (id)
    )
    PRINT 'Created ips_returnsupload'
END
ELSE
BEGIN
    -- Table exists — backfill any columns added after initial deploy
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('ips_returnsupload') AND name = 'as_of_date')
    BEGIN
        ALTER TABLE ips_returnsupload ADD as_of_date nvarchar(50) NOT NULL DEFAULT ''
        PRINT 'Added as_of_date to ips_returnsupload'
    END

    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('ips_returnsupload') AND name = 'calendar_years')
    BEGIN
        ALTER TABLE ips_returnsupload ADD calendar_years nvarchar(200) NOT NULL DEFAULT '2025,2024,2023,2022,2021,2020,2019'
        PRINT 'Added calendar_years to ips_returnsupload'
    END

    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('ips_returnsupload') AND name = 'is_active')
    BEGIN
        ALTER TABLE ips_returnsupload ADD is_active bit NOT NULL DEFAULT 1
        PRINT 'Added is_active to ips_returnsupload'
    END
END
GO

-- ── ips_feecategory ───────────────────────────────────────
IF OBJECT_ID(N'ips_feecategory', N'U') IS NULL
BEGIN
    CREATE TABLE ips_feecategory (
        id   bigint        IDENTITY(1,1) NOT NULL,
        name nvarchar(100)               NOT NULL,
        CONSTRAINT PK_ips_feecategory      PRIMARY KEY (id),
        CONSTRAINT UQ_ips_feecategory_name UNIQUE      (name)
    )
    PRINT 'Created ips_feecategory'
END
GO

-- ── ips_feetier ───────────────────────────────────────────
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
    PRINT 'Created ips_feetier'
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('ips_feetier') AND name = 'ips_feetier_category_id_idx')
    CREATE INDEX ips_feetier_category_id_idx ON ips_feetier (category_id)
GO

-- ── ips_mandate ───────────────────────────────────────────
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
    PRINT 'Created ips_mandate'
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('ips_mandate') AND name = 'ips_mandate_fee_category_id_idx')
    CREATE INDEX ips_mandate_fee_category_id_idx ON ips_mandate (fee_category_id)
GO

-- ── ips_portfolioprofile ──────────────────────────────────
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
    PRINT 'Created ips_portfolioprofile'
END
GO

-- ── ips_ipscopyblock ──────────────────────────────────────
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
    PRINT 'Created ips_ipscopyblock'
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('ips_ipscopyblock') AND name = 'ips_ipscopyblock_category_idx')
    CREATE INDEX ips_ipscopyblock_category_idx ON ips_ipscopyblock (category)
GO

-- ── ips_sitedocument ──────────────────────────────────────
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
    PRINT 'Created ips_sitedocument'
END
GO

-- ── ips_savedproposal ────────────────────────────────────
IF OBJECT_ID(N'ips_savedproposal', N'U') IS NULL
BEGIN
    CREATE TABLE ips_savedproposal (
        id                    bigint        IDENTITY(1,1) NOT NULL,
        user_id               int                         NOT NULL,
        label                 nvarchar(200)               NOT NULL,
        data                  nvarchar(max)               NOT NULL,
        risk_profile_override nvarchar(100)               NOT NULL DEFAULT '',
        portfolio_override    nvarchar(100)               NOT NULL DEFAULT '',
        created_at            datetime2                   NOT NULL DEFAULT GETUTCDATE(),
        updated_at            datetime2                   NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT PK_ips_savedproposal      PRIMARY KEY (id),
        CONSTRAINT FK_ips_savedproposal_user FOREIGN KEY (user_id)
            REFERENCES auth_user(id)
    )
    PRINT 'Created ips_savedproposal'
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('ips_savedproposal') AND name = 'ips_savedproposal_user_id_idx')
    CREATE INDEX ips_savedproposal_user_id_idx ON ips_savedproposal (user_id)
GO

-- ── django_migrations bookkeeping ────────────────────────
-- Tell Django these migrations are done so it doesn't try to run them.
-- Adjust the app column if your Django app label differs from 'ips'.
IF NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='ips' AND name='0001_returns_upload')
    INSERT INTO django_migrations (app, name, applied) VALUES ('ips','0001_returns_upload', GETUTCDATE())

IF NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='ips' AND name='0002_add_admin_models')
    INSERT INTO django_migrations (app, name, applied) VALUES ('ips','0002_add_admin_models', GETUTCDATE())

IF NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='ips' AND name='0003_fix_returnsupload_columns')
    INSERT INTO django_migrations (app, name, applied) VALUES ('ips','0003_fix_returnsupload_columns', GETUTCDATE())

IF NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='ips' AND name='0004_ensure_admin_tables')
    INSERT INTO django_migrations (app, name, applied) VALUES ('ips','0004_ensure_admin_tables', GETUTCDATE())

IF NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='ips' AND name='0005_savedproposal')
    INSERT INTO django_migrations (app, name, applied) VALUES ('ips','0005_savedproposal', GETUTCDATE())

PRINT 'django_migrations records inserted'
GO

PRINT '=== Done. All ips tables are present. ==='
