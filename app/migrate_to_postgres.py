"""
One-time script to migrate data from SQLite to PostgreSQL.
Run this BEFORE deploying to Azure if you want to migrate existing data.

Usage:
1. Make sure PostgreSQL is set up in Azure
2. Get the PostgreSQL connection string from Azure
3. Run: python migrate_to_postgres.py "your-connection-string-here"
"""

import os
import sys
import django
from django.core.management import call_command

def migrate_to_postgres(postgres_url):
    # Store current database URL
    old_db_url = os.environ.get('DATABASE_URL')
    
    try:
        # Step 1: Dump data from SQLite
        print("Creating backup of SQLite data...")
        call_command('dumpdata', '--exclude', 'auth.permission', 
                    '--exclude', 'contenttypes', '--indent', '2',
                    output='data_backup.json')
        
        # Step 2: Set up PostgreSQL connection
        print(f"\nConfiguring PostgreSQL connection...")
        os.environ['DATABASE_URL'] = postgres_url
        
        # Step 3: Run migrations on PostgreSQL
        print("\nApplying migrations to PostgreSQL...")
        call_command('migrate')
        
        # Step 4: Load data into PostgreSQL
        print("\nLoading data into PostgreSQL...")
        call_command('loaddata', 'data_backup.json')
        
        print("\nMigration completed successfully!")
        print("\nNext steps:")
        print("1. Deploy your application to Azure")
        print("2. Make sure the DATABASE_URL environment variable is set in Azure App Service")
        
    except Exception as e:
        print(f"\nError during migration: {e}")
        sys.exit(1)
        
    finally:
        # Cleanup
        if os.path.exists('data_backup.json'):
            os.remove('data_backup.json')
        # Restore original database URL if it existed
        if old_db_url:
            os.environ['DATABASE_URL'] = old_db_url
        else:
            os.environ.pop('DATABASE_URL', None)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("\nUsage: python migrate_to_postgres.py \"postgres://user:pass@host:5432/dbname\"")
        sys.exit(1)
    
    postgres_url = sys.argv[1]
    migrate_to_postgres(postgres_url) 