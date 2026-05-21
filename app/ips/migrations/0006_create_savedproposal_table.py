"""
Creates ips_savedproposal using raw SQL so the service account's
CREATE TABLE rights are used directly — no Django schema editor involved.
Safe to re-run (IF OBJECT_ID / CREATE TABLE IF NOT EXISTS guards).
"""
from django.db import migrations


def create_savedproposal(apps, schema_editor):
    from django.db import connection

    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS "ips_savedproposal" (
                    "id"                    integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "user_id"               integer      NOT NULL REFERENCES "auth_user" ("id"),
                    "label"                 varchar(200) NOT NULL,
                    "data"                  text         NOT NULL,
                    "risk_profile_override" varchar(100) NOT NULL DEFAULT '',
                    "portfolio_override"    varchar(100) NOT NULL DEFAULT '',
                    "created_at"            datetime     NOT NULL,
                    "updated_at"            datetime     NOT NULL
                )
            """)
        return

    with connection.cursor() as cursor:
        cursor.execute("""
            IF OBJECT_ID(N'ips_savedproposal', N'U') IS NULL
            BEGIN
                CREATE TABLE ips_savedproposal (
                    id                    bigint        IDENTITY(1,1) NOT NULL,
                    user_id               bigint                      NOT NULL,
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
            END
        """)
        cursor.execute("""
            IF NOT EXISTS (
                SELECT 1 FROM sys.indexes
                WHERE object_id = OBJECT_ID('ips_savedproposal')
                  AND name = 'ips_savedproposal_user_id_idx'
            )
                CREATE INDEX ips_savedproposal_user_id_idx ON ips_savedproposal (user_id)
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0005_savedproposal'),
    ]

    operations = [
        migrations.RunPython(create_savedproposal, migrations.RunPython.noop),
    ]
