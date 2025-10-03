"""
Django settings for limbs_orthopaedic project.
"""

import os
from pathlib import Path
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# Set DEBUG to False in production
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Configure custom error handlers - these will be used when DEBUG is False
HANDLER404 = 'limbs_orthopaedic.views.handler404'
HANDLER403 = 'limbs_orthopaedic.views.handler403'
HANDLER500 = 'limbs_orthopaedic.views.handler500'

ALLOWED_HOSTS = ['limbsorthopaedic.org', 'www.limbsorthopaedic.org']


# Caching configuration for production
# Use database caching for production to handle high traffic
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Cache middleware settings
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'limbs'
CACHE_MIDDLEWARE_ALIAS = 'default'

# Application definition

INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Other third party apps
    'rest_framework',
    'corsheaders',
    'django_ckeditor_5',

    # Project apps
    'limbs_orthopaedic.apps.LimbsOrthopaedicConfig',
    'core',
    'services',
    'products',
    'appointments',
    'blog',
    'testimonials',
    'accounts',
    'chatbot',
    'content_manager',
    'notifications.apps.NotificationsConfig',
    'surveys.apps.SurveysConfig',
    'staff_chat',
    'analytics',
    'gallery',
    'careers',
    'limbs_cyber',

    # Sitemap
    'django.contrib.sitemaps',
    'django.contrib.sites',
]

SITE_ID = 1

# SEO Settings
META_TITLE = 'LIMBS Orthopaedic - Premier Orthopaedic Care in Nairobi, Kenya'
META_DESCRIPTION = 'Leading orthopaedic facility in Nairobi, Kenya specializing in prosthetics, orthotic devices, Aeroplane splint, AFO, Arch support, Axillary crutch, Calcaneal spur insole, Cockup splint, Derotator Harness, Elbow conformer, Elbow crutch, bow legs, knock knees, Genu Varus, Genu Valgum, Hand resting splint, HKAFO, HTHKAFO, KAFO, Lateral and Medial wedges, Neck collar, Prosthetic Socket replacement, SMAFO, Spinal Brace, Wheelchair, Standing And Sitting AID, THKAFO, Transfemoral prosthesis, Transtibial prosthesis, Walking crutches, GRAFO, and mobility aids. Professional care for independence and enhanced mobility.'
META_KEYWORDS = 'orthopaedic Nairobi, prosthetics Kenya, Aeroplane splint, AFO, Arch support, Axillary crutch, Calcaneal spur insole, Cockup splint, Derotator Harness, Elbow conformer, Elbow crutch, bow legs, knock knees, Genu Varus, Genu Valgum, Hand resting splint, HKAFO, HTHKAFO, KAFO, Lateral and Medial wedges, Neck collar, Prosthetic Socket replacement, SMAFO, Spinal Brace, Wheelchair, Standing And Sitting AID, THKAFO, Transfemoral prosthesis, Transtibial Prosthesis, Walking crutches, GRAFO, mobility aids, physiotherapy, rehabilitation, LIMBS Orthopaedic'

# Additional SEO settings
SITE_NAME = 'LIMBS Orthopaedic'
SITE_URL = 'https://limbsorthopaedic.org'
COMPANY_ADDRESS = 'ICIPE Road, Kasarani, Nairobi, Kenya'
COMPANY_PHONE = ['+254719628276', '+254714663594', '+254705347657']
COMPANY_EMAIL = 'LimbsOrthopaedic@gmail.com'



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'analytics.middleware.VisitTrackingMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
]

# Add caching middleware
if not DEBUG:
    MIDDLEWARE.insert(2, 'django.middleware.cache.UpdateCacheMiddleware')
    MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

# Security settings
# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

ROOT_URLCONF = 'limbs_orthopaedic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': DEBUG,  # Only True in development
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'content_manager.context_processors.site_settings',
                'content_manager.context_processors.page_sections',
                'notifications.context_processors.unread_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'limbs_orthopaedic.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET NAMES 'utf8mb4', sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'  # Kenya's timezone

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise static file settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # Cache static files for 1 year

# Template caching configuration
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = False  # For development only, restrict in production

# CSRF settings
CSRF_TRUSTED_ORIGINS = ['https://limbsorthopaedic.org', 'https://*.replit.dev', 'https://*.replit.app'] if DEBUG else [
    'https://limbsorthopaedic.org',
    'https://www.limbsorthopaedic.org'
]
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGOUT_REDIRECT_URL = '/'

# Base URL for creating absolute URLs in emails
HOST_URL = os.environ.get('HOST_URL')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.limbsorthopaedic.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@limbsorthopaedic.org'
EMAIL_HOST_PASSWORD = os.environ.get('CPANEL_EMAIL_PASSWORD')

DEFAULT_FROM_EMAIL = 'LIMBS Orthopaedic <noreply@limbsorthopaedic.org>'
SERVER_EMAIL = 'noreply@limbsorthopaedic.org'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'CRITICAL',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'mail_admins'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


# CKEditor 5 color palette definition
customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]

# CKEditor 5 Settings
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
        'height': 300,
        'width': '100%',
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

CKEDITOR_5_UPLOAD_PATH = "uploads/"
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"