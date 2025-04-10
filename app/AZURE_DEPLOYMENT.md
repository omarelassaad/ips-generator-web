# Azure Deployment Guide

## Prerequisites
1. Azure account with necessary permissions
2. Azure CLI installed (optional, for local testing)
3. Access to Azure DevOps repository

## Step 1: Set Up Azure Resources

1. Create Azure App Service:
   - Go to Azure Portal
   - Create new App Service
   - Select Linux as OS
   - Select Python 3.11
   - Select appropriate pricing tier (minimum B1)

2. Database Options:
   
   Option A - Start with SQLite (Simplest):
   - No additional setup needed
   - App will work immediately with SQLite
   - Good for testing or low-traffic scenarios
   
   Option B - Use PostgreSQL from Start:
   - Create Azure Database for PostgreSQL
   - Note down the connection string
   - Set up the database before first deployment

## Step 2: Configure App Service

Set these environment variables in App Service Configuration:
```
DJANGO_SECRET_KEY=<generate-a-secure-key>
DJANGO_DEBUG=False
ALLOWED_HOSTS=<your-app-name>.azurewebsites.net
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=<choose-secure-password>
DJANGO_SUPERUSER_EMAIL=<admin-email>

# Optional: Set only if using PostgreSQL
DATABASE_URL=<postgresql-connection-string>
```

## Step 3: Database Migration (Optional)

If starting with SQLite and want to switch to PostgreSQL later:

1. Get the PostgreSQL connection string from Azure
2. Run the migration script locally:
   ```bash
   python migrate_to_postgres.py "your-postgresql-connection-string"
   ```
3. After successful migration, add the DATABASE_URL to Azure App Service configuration

## Step 4: Deploy

1. Make sure all code is committed to Azure DevOps
2. The pipeline will automatically:
   - Install dependencies
   - Configure the environment
   - Collect static files
   - Run migrations
   - Start the application

## Troubleshooting

Common issues and solutions:

1. If deployment fails:
   - Check App Service logs in Azure Portal
   - Verify environment variables are set correctly
   - Ensure database connection string is correct (if using PostgreSQL)

2. If database migration fails:
   - Check PostgreSQL firewall rules
   - Verify connection string format
   - Check database permissions
   - Try running migration script with --verbosity=2 for more details

3. If using SQLite:
   - Make sure the app has write permissions to the database file
   - Check if the database file exists in the correct location
   - Verify the file permissions are correct

## Support

For issues or questions, contact: [your-contact-info]

## Database Choice Guide

### When to stay with SQLite:
- During initial testing and setup
- For low traffic scenarios
- When simplicity is priority
- For development and staging environments

### When to switch to PostgreSQL:
- For production use with multiple users
- When needing better concurrent access
- For larger datasets
- When requiring better backup and recovery options 