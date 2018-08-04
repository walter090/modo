import environ
import logging

BASE_DIR = environ.Path(__file__) - 2

env = environ.Env()

env_file = str(BASE_DIR('.env'))
env.read_env(env_file)

# logging.basicConfig(handlers=[logging.FileHandler(env('LOG_FILE'), 'w', 'utf-8')], level=env('LOG_LEVEL'))

# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('HIDDEN_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')
ADMIN_ENABLED = env.bool('ADMIN_ENABLED')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

AWS_DEFAULT_REGION = env('AWS_DEFAULT_REGION')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'oauth2_provider',
    'rest_framework_social_oauth2',
    'storages',
]

LOCAL_APPS = [
    'person.apps.PersonConfig',
    'home.apps.HomeConfig',
    'news.apps.NewsConfig',
    'posts.apps.PostsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'news.management.paginators.ArticlePaginator',
}

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'rest_framework_social_oauth2.backends.DjangoOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

AUTH_USER_MODEL = 'person.Human'

MIDDLEWARE = [
    'oauth2_provider.middleware.OAuth2TokenMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE_CLASSES = [
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
]

ROOT_URLCONF = 'modo.urls'

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

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'modo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASE_NAME'),
        'USER': env('HIDDEN_USER'),
        'PASSWORD': env('HIDDEN_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    }
}

# CELERY_BROKER_URL = "sqs://{}:{}@".format(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_DEFAULT_QUEUE = 'modo_queue'
# CELERY_RESULT_BACKEND = None
# CELERY_BROKER_TRANSPORT = 'sqs'
# CELERY_BROKER_TRANSPORT_OPTIONS = {
#     'region': 'us-west-2',
#     'polling_interval': 20,
# }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
    },
    'REFRESH_TOKEN_EXPIRE_SECONDS': 604800,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 86400
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

EMAIL_USE_TLS = True
EMAIL_HOST = env('HIDDEN_EMAIL_HOST')
EMAIL_HOST_USER = env('HIDDEN_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('HIDDEN_EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('HIDDEN_EMAIL_PORT')

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('S3_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)
AWS_STATIC_LOCATION = env('AWS_STATIC_LOCATION')

STATIC_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)
STATIC_ROOT = BASE_DIR('staticfiles')
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR('media'))
