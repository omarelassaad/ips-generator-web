# IPS Generator Application

A Django-based Investment Policy Statement (IPS) generator application that allows for client management and IPS document creation.

## Features
- Investment Policy Statement Generation
- Client Management
- Questionnaire Response Tracking
- Investment Strategy Management
- Multi-user Support

## Deployment Instructions

### Deploying to Render

1. **Create PostgreSQL Database**
   - Go to Render dashboard
   - Click "New +" → Select "PostgreSQL"
   - Configure:
     - Name: `ips-db`
     - Database: `ips_db`
     - User: `ips_user`
     - Choose Free plan
   - Create Database and note the connection URL

2. **Create Web Service**
   - Click "New +" → Select "Web Service"
   - Connect your GitHub repository
   - Configure:
     - Name: `ips-generator`
     - Environment: `Python`
     - Build Command: `./build.sh`
     - Start Command: `gunicorn ips_generator.wsgi:application`

3. **Environment Variables**
   ```
   PYTHON_VERSION=3.11.0
   DJANGO_DEBUG=false
   DJANGO_SECRET_KEY=[generate a secure key]
   ```
   Note: DATABASE_URL will be automatically set by Render

### Deploying to Azure

1. **Prerequisites**
   - Azure account
   - Azure CLI installed
   - Azure DevOps repository

2. **Create Azure Database**
   ```bash
   az postgres flexible-server create \
     --name ips-db \
     --resource-group your-resource-group \
     --location your-location \
     --admin-user your-admin-user \
     --admin-password your-password \
     --sku-name Standard_B1ms
   ```

3. **Create Azure App Service**
   ```bash
   az webapp create \
     --name ips-generator \
     --resource-group your-resource-group \
     --plan your-app-service-plan \
     --runtime "PYTHON|3.11"
   ```

4. **Configure CI/CD Pipeline**
   Create `azure-pipelines.yml`:
   ```yaml
   trigger:
     - main

   variables:
     pythonVersion: '3.11'

   steps:
   - task: UsePythonVersion@0
     inputs:
       versionSpec: '$(pythonVersion)'
     
   - script: |
       python -m pip install --upgrade pip
       pip install -r requirements.txt
     displayName: 'Install dependencies'

   - script: |
       python manage.py collectstatic --no-input
       python manage.py migrate
     displayName: 'Django commands'

   - task: AzureWebApp@1
     inputs:
       azureSubscription: 'Your-Azure-Subscription'
       appName: 'ips-generator'
       package: '$(System.DefaultWorkingDirectory)'
   ```

5. **Environment Variables in Azure**
   Set these in Azure App Service Configuration:
   ```
   DJANGO_DEBUG=false
   DJANGO_SECRET_KEY=[your-secret-key]
   DATABASE_URL=[your-azure-database-url]
   WEBSITES_PORT=8000
   ```

### Deploying to Azure (Detailed Requirements)

Before switching this application to Azure App Services, please ensure you have completed the following:

- **Azure Account Setup**:
  - Active Azure account and access to Azure DevOps.

- **Database Provisioning**:
  - Create an Azure PostgreSQL (or suitable) managed database.
  - Update the `DATABASE_URL` environment variable with your connection string.

- **App Service Configuration**:
  - Create an Azure App Service instance using the Python 3.11 runtime in a resource plan that meets your needs.

- **Environment Variables**:
  - In the Azure App Service settings, configure the following variables:
    - `DJANGO_DEBUG=false`
    - `DJANGO_SECRET_KEY=<your secret key>`
    - `DATABASE_URL=<your Azure database URL>`
    - `WEBSITES_PORT=8000`

- **Static and Media Files Handling**:
  - Ensure that `STATIC_ROOT` and `MEDIA_ROOT` are correctly configured in `settings.py`.
  - Use WhiteNoise (or an alternative) to serve static files.

- **CI/CD Pipeline Setup**:
  - Create an `azure-pipelines.yml` file to automate dependency installation, static file collection, migrations, and deployment using the `AzureWebApp` task.

- **Production Settings and Testing**:
  - Verify that production configurations in `settings.py` (e.g., allowed hosts, security settings) are correctly set.
  - Test your application locally with `DJANGO_DEBUG=false` to simulate production conditions.

- **Additional Considerations**:
  - Document any differences in file path handling, especially if your Azure environment uses a different OS (Linux vs. Windows containers), and adjust deployment scripts accordingly.

## Local Development

1. **Setup Virtual Environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## Database Configuration

The application uses PostgreSQL in production and SQLite for local development. Database settings are automatically configured based on the environment through `dj_database_url`.

## Security Notes

- Never commit sensitive credentials to the repository
- Use environment variables for all sensitive information
- Keep DEBUG=False in production
- Regularly update dependencies

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 