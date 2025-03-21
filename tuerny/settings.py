"""
Django settings for tuerny project.

Generated by 'django-admin startproject' using Django 3.2.25.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-uv=!a=*9_@r)z&rtncj9deg12$o-n*au_jf8hsj7ra)ejfz8!n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]
AUTH_USER_MODEL = 'tuerny_app.CustomUser'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'tuerny_app',
    'ckeditor',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google'
]
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]
SOCIALACCOUNT_LOGIN_ON_GET=True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE' : [
            'profile',
            'email'
        ],
        'APP': {
            'client_id': os.environ['CLIENT_ID'],
            'secret': os.environ['CLIENT_SECRET'],
        },
        'AUTH_PARAMS': {
            'access_type':'online',
        }
    }
}

SITE_ID = 2
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['Format', 'Font', 'FontSize', 'TextColor', 'BGColor'],
            ['Link', 'Unlink'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
            ['RemoveFormat', 'Source']
        ],
        'height': 300,
        'width': '100%',
        'extraPlugins': 'font,colorbutton',
        'font_names': 'Roboto/Roboto, Arial, sans-serif;'
    }
}

def get_ck_editor_config(user):
    if user.is_superuser:
        # 🔥 Adminler için tam yetkili CKEditor
        return {
            'toolbar': 'Full',
            'toolbar_Full': [
                ['Bold', 'Italic', 'Underline'],
                ['Format', 'Font', 'FontSize', 'TextColor', 'BGColor'],
                ['Link', 'Unlink'],
                ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
                ['RemoveFormat', 'Source'],
                ['Styles', 'Format', 'Blockquote'],
                ['NumberedList', 'BulletedList']
            ],
            'height': 300,
            'width': '100%',
            'extraPlugins': 'font,colorbutton',
        }
    else:
        # ✂️ Editörler için sadece "Heading 1", "Heading 2" ve "Normal"
        return {
            'toolbar': 'Basic',
            'toolbar_Basic': [
                ['Format']
            ],
            'format_tags': 'h1;h2;p',  # Sadece Heading 1, Heading 2 ve Normal (Paragraf)
            'height': 300,
            'width': '100%',
        }

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware'
]

ROOT_URLCONF = 'tuerny.urls'

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
                'tuerny_app.context_processors.categories_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'tuerny.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LOGIN_URL = '/login/'  # Giriş yapılması gereken durumlarda yönlendirilecek URL
LOGIN_REDIRECT_URL = '/'  # Başarılı girişten sonra yönlendirilecek URL

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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATICFILES_DIRS
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

FRONTEND_URL = "http://127.0.0.1:8000"
ACCOUNT_ADAPTER = "tuerny_app.adapters.CustomAccountAdapter"
ACCOUNT_USERNAME_REQUIRED = True

ACCOUNT_SIGNUP_REDIRECT_URL = "/"

# Kullanıcı adı yerine sadece e-posta ile giriş yap
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_MIN_LENGTH = 3  # Kullanıcı adının minimum uzunluğu
ACCOUNT_EMAIL_REQUIRED = True  # E-posta zorunlu olsun
ACCOUNT_UNIQUE_EMAIL = True  # E-posta tekil olsun
ACCOUNT_USERNAME_BLACKLIST = ["admin", "root", "test"]  # Yasaklı kullanıcı adları

# Kullanıcı giriş yaptıktan sonra yönlendirilecek URL
ACCOUNT_SIGNUP_REDIRECT_URL = "/"  
ACCOUNT_LOGIN_REDIRECT_URL = "/"
ACCOUNT_AUTHENTICATION_METHOD = "email"

# Otomatik username oluşturulacağı için username zorunlu olmamalı
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True  
ACCOUNT_UNIQUE_EMAIL = True


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'furkanp2002@gmail.com'
EMAIL_HOST_PASSWORD = 'xecl xryx cbkt ejtt'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
