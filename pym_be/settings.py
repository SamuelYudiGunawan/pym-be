"""
Django settings for pym_be project.
Supports local development (SQLite) and Kubernetes/OKE deployment (PostgreSQL)
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment detection
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'

# Secret key - use environment variable or default for development
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'dev-only-insecure-key-change-in-production')

# Debug mode - automatically False in production
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')
if IS_PRODUCTION:
    DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(
    ',') if os.environ.get('ALLOWED_HOSTS') else []
ALLOWED_HOSTS += [
    'localhost',
    '127.0.0.1',
    'backend',           # Docker service name for Prometheus scraping
    'pym-backend',       # Docker container name
    'pym-backend-version-a',  # Version A container name
    '.ngrok-free.app',
    '.ngrok-free.dev',
    '.ngrok.io',
]

# For Kubernetes or Docker - allow any host
if os.environ.get('KUBERNETES_SERVICE_HOST') or os.environ.get('ENVIRONMENT') == 'production':
    ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_prometheus',  # Prometheus monitoring
    'notes',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',  # Must be last
]

ROOT_URLCONF = 'pym_be.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pym_be.wsgi.application'


# Database configuration
# Uses PostgreSQL in Kubernetes/production, SQLite for local development

if os.environ.get('DATABASE_URL'):
    # Use dj-database-url for DATABASE_URL format
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
elif os.environ.get('POSTGRES_DB'):
    # Kubernetes environment with individual env vars
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'pym_db'),
            'USER': os.environ.get('POSTGRES_USER', 'pym_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'postgres-service'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    # Local development with SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS Configuration

# Frontend URL from environment (for Kubernetes)
FRONTEND_URL = os.environ.get('FRONTEND_URL', '')

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

# Add frontend URL if specified
if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)

# Allow ngrok, Vercel, and OCI Load Balancer URLs (regex pattern)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.ngrok-free\.app$",
    r"^https://.*\.ngrok-free\.dev$",
    r"^https://.*\.ngrok\.io$",
    r"^https://.*\.vercel\.app$",
    r"^http://\d+\.\d+\.\d+\.\d+.*$",  # Allow IP addresses (OCI Load Balancer)
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'ngrok-skip-browser-warning',
]


# CSRF Trusted Origins

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://*.ngrok-free.app",
    "https://*.ngrok-free.dev",
    "https://*.ngrok.io",
    "https://*.vercel.app",
]

# Add frontend URL to CSRF trusted origins
if FRONTEND_URL:
    CSRF_TRUSTED_ORIGINS.append(FRONTEND_URL)

# Add backend URL to CSRF trusted origins (for admin)
BACKEND_URL = os.environ.get('BACKEND_URL', '')
if BACKEND_URL:
    CSRF_TRUSTED_ORIGINS.append(BACKEND_URL)

# Cross-origin cookie settings
# Use SECURE cookies only if USE_HTTPS env var is set
USE_HTTPS = os.environ.get(
    'USE_HTTPS', 'false').lower() in ('true', '1', 'yes')

if USE_HTTPS:
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SECURE = True
else:
    # HTTP mode (no SSL) - for OKE without HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = False


# Logging configuration for Kubernetes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
