"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o9&qvi9-!#bd1l!pckz&f!yd1#za5fc3=u)2rqerzf6(#)0v49'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'chat',
    'graphene_django',
    'graphql_jwt.refresh_token.apps.RefreshTokenConfig',
    'graphql_auth',
    'django_filters', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

# Not using this but no need to comment out. 
WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# TODO Integrate postgres or mysql depending on db used for news sourcing.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'users.ExtendUser' # Extending default user model

GRAPHENE = {
        'SCHEMA': 'users.schema.schema', # Link to schema
        'MIDDLEWARE': [
            'graphql_jwt.middleware.JSONWebTokenMiddleware',
            ],
        }
AUTHENTICATION_BACKEND = [
        #'graphql_jwt.backends.JSONWebTokenBackend', # Utilize tokens, alt approach 
        'graphql_auth.backends.GraphQLAuthBackend',  # Wrapper for auth also uses tokens 
        'django.contrib.auth.backends.ModelBackend',
        ]
GRAPHQL_JWT = {
        'JWT_ALLOW_ANY_CLASSES': [
            'graphql_auth.mutations.Register', # Register mutations with auth.  Provide registered users with JWT.
            'graphql_auth.mutations.VerifyAccount', # Verify Account with JWT.
            'graphql_auth.mutations.ObtainJSONWebToken', # User Login.  Obtain a jwt for them.  
            ],  
        'JWT_VERIFY_EXPIRATION': True, # Required for refresh token. 
        'JWT_LONG_RUNNING_REFRESH_TOKEN': True, # 
        }

# ASGI and Channels
ASGI_APPLICATION = "backend.routing.application"
CHANNEL_LAYERS = {
        'defualt': {
            'BACKEND': 'channels_redis.backend.RedisChannelLayer',
            'CONFIG': {
               # 'hosts': [os.environ['REDIS_URL']], #TODO NEED TO ADD REDIS_URL IN CELERY/TASKS.py
                },
            },
        }
CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            #'LOCATION': os.environ['REDIS_URL'],
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient'
                },
            },
        }


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # NOTE: FOR LOCAL DEV: Will send email to console (Default) TODO: Set up with gmail in production. 


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
