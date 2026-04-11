"""
Django settings for modern project.

Environment variables (Vercel / production):
  DJANGO_SECRET_KEY     — required when DJANGO_DEBUG is false
  DJANGO_DEBUG          — set "false" on production
  ALLOWED_HOSTS         — comma-separated hosts (default includes localhost + .vercel.app)
  CSRF_TRUSTED_ORIGINS  — comma-separated origins, e.g. https://your-app.vercel.app
  DATABASE_URL          — Postgres in production; omit for local SQLite
  CLOUDINARY_URL        — required on Vercel for uploads (no persistent disk)
  PUBLIC_SITE_URL       — https://your-deployment.vercel.app (M-Pesa callback URL)
  MPESA_*               — see bottom of this file
"""
import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

import dj_database_url
import cloudinary
import cloudinary.api
import cloudinary.uploader

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


# Local dev: DEBUG on by default. Vercel sets VERCEL=1 — ship with DEBUG off unless overridden.
_default_debug = os.environ.get("VERCEL") != "1"
DEBUG = _env_bool("DJANGO_DEBUG", default=_default_debug)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "").strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-dev-only-not-for-production"
    else:
        raise ImproperlyConfigured(
            "Set the DJANGO_SECRET_KEY environment variable when DJANGO_DEBUG is false."
        )

_allowed = os.environ.get("ALLOWED_HOSTS", "").strip()
if _allowed:
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "[::1]",
        ".vercel.app",
    ]

_csrf = os.environ.get("CSRF_TRUSTED_ORIGINS", "").strip()
if _csrf:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(",") if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []

# Full site URL for M-Pesa callbacks when request.build_absolute_uri is wrong behind proxies / localhost.
PUBLIC_SITE_URL = os.environ.get("PUBLIC_SITE_URL", "").strip().rstrip("/")

# If you set PUBLIC_SITE_URL to https://... we trust it for CSRF (typical Vercel setup with one env var).
if PUBLIC_SITE_URL.startswith("http") and PUBLIC_SITE_URL not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(PUBLIC_SITE_URL)

# Cloudinary
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL")

if CLOUDINARY_URL:
    cloudinary.config(
        CLOUDINARY_URL=CLOUDINARY_URL,
        secure=True,
    )
else:
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def _cloudinary_storage_dict():
    if CLOUDINARY_URL:
        cfg = cloudinary.config()
        return {
            "CLOUD_NAME": cfg.cloud_name,
            "API_KEY": cfg.api_key,
            "API_SECRET": cfg.api_secret,
            "SECURE": True,
        }
    return {
        "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
        "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
        "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
        "SECURE": True,
    }


CLOUDINARY_STORAGE = _cloudinary_storage_dict()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "cloudinary",
    "accounts",
    "dashboard",
    "notes",
    "resources",
    "cart",
    "teacher",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "modern.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "modern.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get(
            "DATABASE_URL",
            f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        ),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

_db = DATABASES["default"]
if _db.get("ENGINE", "").endswith("sqlite3"):
    _db["CONN_MAX_AGE"] = 0
    _db.pop("CONN_HEALTH_CHECKS", None)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CLOUDINARY_ENABLED = bool(
    os.environ.get("CLOUDINARY_URL") or os.environ.get("CLOUDINARY_CLOUD_NAME")
)

if CLOUDINARY_ENABLED:
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            # Compressed without strict manifest — avoids brittle 500s if a hashed name is missing at runtime.
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

if CLOUDINARY_ENABLED:
    from cloudinary_storage.storage import RawMediaCloudinaryStorage

    PDF_STORAGE = RawMediaCloudinaryStorage()
else:
    from django.core.files.storage import FileSystemStorage

    PDF_STORAGE = FileSystemStorage()

MPESA_CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET", "")
MPESA_SHORTCODE = os.environ.get("MPESA_SHORTCODE", "")
MPESA_PASSKEY = os.environ.get("MPESA_PASSKEY", "")
MPESA_ENVIRONMENT = os.environ.get("MPESA_ENVIRONMENT", "sandbox")

# --- HTTPS / proxy (Vercel, Railway, etc.) ---
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Vercel terminates TLS; enabling redirect here can cause loops — opt in with SECURE_SSL_REDIRECT=true if needed.
    SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", default=False)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    if not CSRF_TRUSTED_ORIGINS:
        import warnings

        warnings.warn(
            "CSRF_TRUSTED_ORIGINS is empty while DEBUG is false. Set PUBLIC_SITE_URL or "
            "CSRF_TRUSTED_ORIGINS (e.g. https://your-app.vercel.app) or POST requests may fail with 403.",
            stacklevel=2,
        )

# Warn when deployed to Vercel without Cloudinary (uploads will not persist).
if os.environ.get("VERCEL") == "1" and not CLOUDINARY_ENABLED:
    import warnings

    warnings.warn(
        "VERCEL is set but CLOUDINARY_URL / CLOUDINARY_CLOUD_NAME is missing. "
        "User uploads cannot be stored on Vercel's filesystem.",
        stacklevel=2,
    )

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "payments": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}
