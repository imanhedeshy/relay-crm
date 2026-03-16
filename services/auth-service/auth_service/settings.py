from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent

load_dotenv(REPO_ROOT / ".env")

SECRET_KEY = "relaycrm-auth-service"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "authz",
]

MIDDLEWARE = []
ROOT_URLCONF = "auth_service.urls"
TEMPLATES = []
WSGI_APPLICATION = "auth_service.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("AUTH_DB_NAME", "auth_db"),
        "USER": os.getenv("AUTH_DB_USER", "relay"),
        "PASSWORD": os.getenv("AUTH_DB_PASSWORD", "relay"),
        "HOST": os.getenv("AUTH_DB_HOST", "localhost"),
        "PORT": os.getenv("AUTH_DB_PORT", "5432"),
    }
}

use_postgres = os.getenv("USE_POSTGRES")
should_use_postgres = use_postgres.lower() == "true" if use_postgres is not None else os.getenv("AUTH_DB_HOST") is not None

if not should_use_postgres:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

USE_TZ = True
TIME_ZONE = "UTC"
MIGRATION_MODULES = {"authz": None}
