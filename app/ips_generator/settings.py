from pathlib import Path
import environ
import os
import dj_database_url
import pyodbc

BASE_DIR = Path(__file__).resolve().parent.parent

# Construct the path to the .env file
ENV_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/ips_generator"
# Properly initialize environ.Env and load .env
env = environ.Env()
env.read_env(os.path.join(ENV_PATH, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-!ycct3=ds7t)02*j+!u^0rqx65e69_&pklfad&zzmfpiq+qd!d")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

# Update ALLOWED_HOSTS to include localhost for development
ALLOWED_HOSTS = ['*']  # Configure this based on your Render URL

CSRF_TRUSTED_ORIGINS = ['https://ipsgenerator-web.nxgcae.dev.cg.net']

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Ensure directories exist
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# WhiteNoise settings
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True
WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds

# WeasyPrint settings
WEASYPRINT_TIMEOUT = 60  # Increase timeout to 60 seconds

# Production settings
if not DEBUG:
    # Force HTTPS for static files in production
    if os.getenv('RENDER'):
        STATIC_URL = 'https://' + os.getenv('RENDER_EXTERNAL_HOSTNAME', '') + '/static/'
        MEDIA_URL = 'https://' + os.getenv('RENDER_EXTERNAL_HOSTNAME', '') + '/media/'

    # In production, media files will be served from staticfiles/media
    MEDIA_ROOT = os.path.join(STATIC_ROOT, 'media')
    # This ensures media files are served through WhiteNoise in production
    WHITENOISE_ROOT = STATIC_ROOT
    # Increase timeout for static file serving
    WHITENOISE_TIMEOUT = 30  # 30 seconds timeout for static files

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ips',
    'django.contrib.humanize',
    'whitenoise.runserver_nostatic',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise must be above all but SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ips_generator.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = "ips_generator.wsgi.application"

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME':  env('SQL_DATABASE_NAME'),
        'HOST': env('SQL_SERVER_NAME'),
        'USER':  env('SQL_USERNAME'),
        'PASSWORD':  env('SQL_PASSWORD'),
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}

# Add SSL configuration for Azure PostgreSQL
if not DEBUG:
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require'
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

LOGIN_URL = '/accounts/login/'

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Security settings for production
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
