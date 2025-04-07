"""
Django settings for Balemuya project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""


from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

import cloudinary
import cloudinary.uploader
import cloudinary.api

import os
from celery.schedules import crontab
from datetime import timedelta

#load environment variable from .env file
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django.contrib.sites',  
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_twilio',
    'cloudinary',
    'channels',
    'django_celery_beat',
    "drf_yasg", 


     #user defined apps
    'common',
    'users',
    'services',
    'notifications',
    'customAdmin',
    

    
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Default
)


REST_FRAMEWORK = {
   'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
   
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
   
}

SITE_ID = 1

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1), 
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),    
    'ROTATE_REFRESH_TOKENS': False,                
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,               
    'AUTH_HEADER_TYPES': ('Bearer',),                
}


ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'SCOPE': [
                'profile',
                'email',
            ],
        }
    }
}


# CELERY_BEAT_SCHEDULE = {
#     'notify-expiring-subscriptions-every-day': {
#         'task': 'users.tasks.notify_expiring_subscriptions',
#         'schedule': crontab(minute=0, hour='*'),
#     },
# }

# CELERY_BROKER_URL = 'redis://red-culq0bt6l47c73dt1nt0:6379/0'
# CELERY_TASK_SERIALIZER = 'json'

# settings.py

# CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'Balemuya.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'Balemuya.wsgi.application'

ASGI_APPLICATION = 'Balemuya.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases



DATABASE_URL = os.getenv(
    'POSTGRES_DATABASE_URL',
    'postgresql://postgres.kakjszylvsswigvfgdiu:balemuya123@aws-0-us-east-1.pooler.supabase.com:5432/postgres'
)

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL)
}




# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.User'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = os.getenv('MEDIA_URL')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ALLOWED_HOSTS = ['balemuya-project.onrender.com', '127.0.0.1', 'localhost']

CSRF_TRUSTED_ORIGINS = [
    'https://balemuya-project.onrender.com',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'https://balemuya-project.onrender.com',
]

CORS_ALLOW_HEADERS = [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'Accept',
]

APPEND_SLASH=False

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS', 
]

# settings.py
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
        }
    },
    'USE_SESSION_AUTH': False,  # Set to False if you're using JWT
}


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# EMAIL_TIMEOUT = 30
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Balemuya.settings')


DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
cloudinary.config(
    cloudinary_url=CLOUDINARY_URL
)




TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_DEFAULT_CALLERID = os.getenv('TWILIO_DEFAULT_CALLERID')


CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')
CHAPA_PUBLIC_KEY = os.getenv('CHAPA_PUBLIC_KEY')

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": os.getenv("FCM_SERVER_KEY"),  
    "FIREBASE_SENDER_ID": os.getenv("FIREBASE_SENDER_ID"), 
    "ONE_DEVICE_PER_USER": False, 
}

CLOUDINARY_CLOUD_NAME = "df5gzlw6m"
CLOUDINARY_API_KEY = "687326949413637"
CLOUDINARY_API_SECRET = "63N1V3qcXoS0UiRo2x0GrlsuzfQ"

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)