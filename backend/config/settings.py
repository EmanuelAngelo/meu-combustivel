import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
BASE_DIR = Path(__file__).resolve().parent.parent
# Backend settings never read frontend .env files. Existing environment wins.
load_dotenv(BASE_DIR / '.env', override=False)
DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() == 'true'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'development-only-never-use-this-key-in-production'
    else:
        raise ImproperlyConfigured('Configure DJANGO_SECRET_KEY or set DJANGO_DEBUG=true locally.')
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',') if h.strip()]
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'rest_framework', 'corsheaders', 'fuel']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', 'django.middleware.security.SecurityMiddleware', 'whitenoise.middleware.WhiteNoiseMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware', 'fuel.middleware.NoStoreMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.environ.get('SQLITE_PATH', str(BASE_DIR / 'data' / 'db.sqlite3')), 'OPTIONS': {'timeout': 20}}}
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
FRONTEND_DIST = BASE_DIR.parent / 'dist'
SERVE_FRONTEND = os.environ.get('DJANGO_SERVE_FRONTEND', 'false').lower() == 'true'
WHITENOISE_ROOT = str(FRONTEND_DIST) if SERVE_FRONTEND else None
WHITENOISE_MAX_AGE = 0
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = os.environ.get('DJANGO_COOKIE_SAMESITE', 'Lax')
if SESSION_COOKIE_SAMESITE not in ('Lax', 'Strict', 'None'):
    raise ImproperlyConfigured('DJANGO_COOKIE_SAMESITE must be Lax, Strict or None.')
if SESSION_COOKIE_SAMESITE == 'None' and DEBUG:
    raise ImproperlyConfigured('Cross-site cookies require HTTPS and DJANGO_DEBUG=false.')
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE
# Cookies remain host-only: the Vercel proxy receives them on the frontend host.
def csv_env(name, default=''):
    return [value.strip() for value in os.environ.get(name, default).split(',') if value.strip()]
LOCAL_FRONTEND_ORIGINS = 'http://localhost:4173,http://127.0.0.1:4173' if DEBUG else ''
CORS_ALLOWED_ORIGINS = csv_env('DJANGO_CORS_ALLOWED_ORIGINS', LOCAL_FRONTEND_ORIGINS)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r'^/api/.*$'
CSRF_TRUSTED_ORIGINS = csv_env('DJANGO_CSRF_TRUSTED_ORIGINS', LOCAL_FRONTEND_ORIGINS)
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'
if os.environ.get('TRUST_PROXY_SSL_HEADER') == 'true':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES': ['fuel.auth.StrictSessionAuthentication'], 'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'], 'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle', 'rest_framework.throttling.UserRateThrottle'], 'DEFAULT_THROTTLE_RATES': {'anon': '100/hour', 'user': '1000/hour', 'auth': '20/hour'}, 'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'], 'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser']}
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_TIMEOUT = 10
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' if EMAIL_HOST else 'django.core.mail.backends.dummy.EmailBackend'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.invalid')
PUBLIC_APP_URL = os.environ.get('PUBLIC_APP_URL', 'http://localhost:4173').rstrip('/')
PASSWORD_RESET_TIMEOUT = 3600
PRICE_MAX_AGE_DAYS = 7
