"""Configuração local e PostgreSQL. Segredos devem vir do ambiente."""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent
DEBUG = os.getenv('ELDI_DEBUG', '0') == '1'
TESTING = os.getenv('ELDI_TESTING', '0') == '1'
SECRET_KEY = os.getenv('ELDI_SECRET_KEY', '')
if not SECRET_KEY:
    if not (DEBUG or TESTING):
        raise ImproperlyConfigured('Defina ELDI_SECRET_KEY; para desenvolvimento use ELDI_DEBUG=1.')
    SECRET_KEY = 'local-test-only-not-for-deployment'
ALLOWED_HOSTS = os.getenv('ELDI_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'eldi']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF = 'routes'
WSGI_APPLICATION = 'wsgi.application'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR / 'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
if os.getenv('PGDATABASE'):
    DATABASES = {'default': {'ENGINE':'django.db.backends.postgresql','NAME':os.environ['PGDATABASE'],'USER':os.getenv('PGUSER','eldi'),'PASSWORD':os.getenv('PGPASSWORD',''),'HOST':os.getenv('PGHOST','127.0.0.1'),'PORT':os.getenv('PGPORT','5432')}}
elif DEBUG or TESTING:
    DATABASES = {'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR / 'local.sqlite3'}}
else:
    raise ImproperlyConfigured('Configure PostgreSQL via PGDATABASE, PGUSER, PGPASSWORD, PGHOST e PGPORT.')
AUTH_PASSWORD_VALIDATORS = [{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':15}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
LOGIN_URL = '/entrar/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/entrar/'
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG and not TESTING
CSRF_COOKIE_SECURE = not DEBUG and not TESTING
SECURE_SSL_REDIRECT = not DEBUG and not TESTING
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 11 * 1024 * 1024

from eldi.templates_content import TEMPLATES as ELDI_TEMPLATES
TEMPLATES[0]['APP_DIRS'] = False
TEMPLATES[0]['OPTIONS']['loaders'] = [('django.template.loaders.locmem.Loader', ELDI_TEMPLATES)]
