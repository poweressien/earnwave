"""
EarnWave Settings — works locally (SQLite) and on Railway (PostgreSQL)
"""
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ── SECURITY ──────────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='django-insecure-earnwave-local-dev-key-2024')
DEBUG = config('DEBUG', default=True, cast=bool)

# Accept localhost + any Railway subdomain automatically
_ALLOWED = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0')
ALLOWED_HOSTS = [h.strip() for h in _ALLOWED.split(',') if h.strip()]
ALLOWED_HOSTS += ['.railway.app', '.up.railway.app']  # catch all Railway URLs

# ── APPS ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',
    'dashboard',
    'surveys',
    'quizzes',
    'games',
    'rewards',
    'referrals',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AntiAbuseMiddleware',
]

ROOT_URLCONF = 'earnwave.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
                'core.context_processors.user_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'earnwave.wsgi.application'

# ── DATABASE ──────────────────────────────────────────────────────────────────
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── AUTH ──────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# ── LOCALISATION ──────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# ── STATIC & MEDIA ────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── MISC ──────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ── EMAIL ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='EarnWave <noreply@earnwave.ng>')

# ── PAYSTACK ──────────────────────────────────────────────────────────────────
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='sk_test_your_key')
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='pk_test_your_key')
PAYSTACK_BASE_URL = 'https://api.paystack.co'

# ── PLATFORM CONFIG ───────────────────────────────────────────────────────────
PLATFORM_NAME = 'EarnWave'
PLATFORM_TAGLINE = 'Earn Airtime. Play. Win. Repeat.'
POINTS_PER_NAIRA = 100
MIN_REDEMPTION_POINTS = 1000
DAILY_TASK_POINTS = 50
REFERRAL_BONUS_INVITER = 100
REFERRAL_BONUS_INVITEE = 50
DAILY_AD_LIMIT = 5
AD_WATCH_POINTS = 10
LEVEL_THRESHOLDS = {'Bronze': 0, 'Silver': 1000, 'Gold': 5000, 'Platinum': 15000}

# ── CSRF ──────────────────────────────────────────────────────────────────────
_CSRF = config('CSRF_TRUSTED_ORIGINS', default='http://localhost,http://127.0.0.1')
CSRF_TRUSTED_ORIGINS = [h.strip() for h in _CSRF.split(',') if h.strip()]

# ── PRODUCTION SECURITY ───────────────────────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# ── CACHE ─────────────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'earnwave-cache',
    }
}
