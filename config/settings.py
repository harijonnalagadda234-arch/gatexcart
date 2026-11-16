
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
import pymysql

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")
pymysql.install_as_MySQLdb()

# Security settings
IS_VERCEL = (
    os.getenv("VERCEL", "").lower() in {"1", "true"}
    or bool(os.getenv("VERCEL_ENV"))
)

DEBUG = os.getenv("DEBUG", "False").lower() == "true" and not IS_VERCEL

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-change-me"
    else:
        raise ImproperlyConfigured(
            "Set SECRET_KEY in the environment when DEBUG is disabled."
        )


def _csv_setting(name, default=""):
    return [
        value.strip()
        for value in os.getenv(name, default).split(",")
        if value.strip()
    ]


# Allowed hosts
vercel_url = os.getenv("VERCEL_URL", "").strip()
vercel_host = (
    vercel_url.split("://")[-1]
    .split("/", 1)[0]
    .split(":", 1)[0]
)

ALLOWED_HOSTS = _csv_setting(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost" if DEBUG else "",
)

if vercel_host and vercel_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(vercel_host)

# Add the assigned Vercel domain
if IS_VERCEL:
    for host in ["gatexcart.vercel.app"]:
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Set ALLOWED_HOSTS or deploy with VERCEL_URL."
    )


# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = _csv_setting("CSRF_TRUSTED_ORIGINS")

if vercel_host:
    vercel_origin = f"https://{vercel_host}"
    if vercel_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(vercel_origin)

if IS_VERCEL:
    custom_origin = "https://gatexcart.vercel.app"
    if custom_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(custom_origin)


# HTTPS and secure cookies
if IS_VERCEL:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "catalog",
    "chatbot",
]


# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# Database - TiDB Cloud / Local MySQL
DB_HOST = os.getenv("DB_HOST", "")

DB_OPTIONS = {
    "charset": "utf8mb4",
}

if DB_HOST.casefold() not in {"", "localhost", "127.0.0.1", "::1"}:
    ssl_ca = os.getenv("DB_SSL_CA", "").strip()

    ssl_ca_path = (
        Path(ssl_ca).expanduser()
        if ssl_ca
        else BASE_DIR / "certs" / "isrgrootx1.pem"
    )

    if not ssl_ca_path.is_absolute():
        ssl_ca_path = BASE_DIR / ssl_ca_path

    if not ssl_ca_path.is_file():
        raise ImproperlyConfigured(
            "DB_SSL_CA must point to a readable CA certificate "
            "for remote MySQL connections."
        )

    DB_OPTIONS.update({
        "ssl_ca": str(ssl_ca_path),
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    })


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "gatexkart_db"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": DB_HOST,
        "PORT": os.getenv("DB_PORT", "4000"),
        "OPTIONS": DB_OPTIONS,
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# Language and timezone
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Website footer settings
SITE_FOOTER_PHONE = os.getenv("SITE_FOOTER_PHONE", "0096566852921")

SITE_FOOTER_EMAIL = os.getenv(
    "SITE_FOOTER_EMAIL",
    "gatexkartprivatelimited@gmail.com",
)

SITE_FOOTER_ADDRESS = os.getenv(
    "SITE_FOOTER_ADDRESS",
    "6/64, Near Z P High School Penagalur, Tirupati, "
    "Andhra Pradesh, PIN 516127",
)

SITE_DESIGNER = os.getenv("SITE_DESIGNER", "").strip()


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
