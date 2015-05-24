"""
Django settings for project ers_backend.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ul2)0@*k-3snu(fijr8)9t1ozwuk3&4wmp_l=uikt426boodl@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # REST API
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',

    # Tests
    'testing',
    'model_mommy',

    # Websockets
    'swampdragon',

    # Help
    'annoying',

    # Apps
    'dataset_manager',
    'video_processor',
    'arousal_modeler',
    'timeframe_annotator',
    'emotion_annotator'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ers_backend.urls'

WSGI_APPLICATION = 'ers_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            '()': 'djangocolors_formatter.DjangoColorsFormatter',
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            '()': 'djangocolors_formatter.DjangoColorsFormatter',
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'dataset_manager': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'video_processor': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'ers_backend': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        }
    }
}

# REST
CORS_ORIGIN_WHITELIST = (
    'http://localhost:3333'
)

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'X-CSRFToken'
)
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'UNICODE_JSON': False,
}

# Swampdragon
SWAMP_DRAGON_CONNECTION = ('swampdragon.connections.sockjs_connection.DjangoSubscriberConnection', '/data')
DRAGON_URL = 'http://localhost:9999/'

# Celery
BROKER_URL = 'redis://localhost:6379/1'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ers_backend_db',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '', # If mamp under OS X: /Applications/MAMP/tmp/mysql/mysql.sock
        'PORT': '',
    }
}

# Modify PATH if under OS X to have access to libraries such as ffmpeg
#os.environ["PATH"] += os.pathsep + os.pathsep.join(["/opt/local/bin", "/usr/local/bin"])

# Constants
VIDEO_EXTENSIONS = ("avi", "mkv", "mov", "mp4", "m4v", "mpeg", "mpg", "wmv")
DATASET_DEFAULT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,os.pardir,'datasets'))
WEBCLIENT_VIDEOS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,os.pardir,'ers_frontend/_public/datasets/$datasetId$/videos'))
