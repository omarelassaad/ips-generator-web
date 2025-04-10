# IPS Generator Application

A Django-based Investment Policy Statement (IPS) generator application that allows for client management and IPS document creation.

## Features
- Investment Policy Statement Generation
- Client Management
- Questionnaire Response Tracking
- Investment Strategy Management
- Multi-user Support

## Technical Stack
The stack is conservative and enterprise-friendly, using proven, mainstream libraries:
- Django 4.2.13 (LTS version)
- Python 3.11
- WeasyPrint 62.1 (for PDF generation)
- matplotlib 3.9.0 (for chart generation)
- whitenoise 6.6.0 (for static files)
- gunicorn 21.2.0 (for serving the application)

## Deployment

For detailed deployment instructions, please refer to [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md).

### Quick Start
1. Clone the repository
2. Follow the setup instructions in AZURE_DEPLOYMENT.md
3. Choose your database option:
   - Start with SQLite (simplest)
   - Set up PostgreSQL (for production use)

### Database Options

1. **SQLite (Quick Start)**
   - No additional setup needed
   - Good for testing and development
   - Can migrate to PostgreSQL later

2. **PostgreSQL (Production)**
   - Azure Database for PostgreSQL
   - Better concurrent access
   - Improved backup and recovery
   - Suitable for multiple users

## Local Development

1. **Setup Virtual Environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. **Install MSYS2**
   ```
   Download and install the MYSYS2 installer from https://www.msys2.org/
   ```

3. **Install GTK3*
   ```
   Install the MYSYS2 variant of GTK3 via https://www.gtk.org/docs/installations/windows/#using-gtk-from-msys2-packages
   ```   

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## Database Configuration

The application uses a flexible database configuration through `dj_database_url`:
- Defaults to SQLite for local development
- Can be configured for PostgreSQL via DATABASE_URL environment variable
- Automatic configuration based on environment settings

## Security Notes

- Never commit sensitive credentials to the repository
- Use environment variables for all sensitive information
- Keep DEBUG=False in production
- Regularly update dependencies
- All dependencies are from trusted sources and regularly maintained

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 