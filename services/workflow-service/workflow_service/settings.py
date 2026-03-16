from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent

load_dotenv(REPO_ROOT / ".env")

SECRET_KEY = "relaycrm-workflow-service"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "workflows",
]

MIDDLEWARE = []
ROOT_URLCONF = "workflow_service.urls"
TEMPLATES = []
WSGI_APPLICATION = "workflow_service.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("WORKFLOW_DB_NAME", "workflow_db"),
        "USER": os.getenv("WORKFLOW_DB_USER", "relay"),
        "PASSWORD": os.getenv("WORKFLOW_DB_PASSWORD", "relay"),
        "HOST": os.getenv("WORKFLOW_DB_HOST", "localhost"),
        "PORT": os.getenv("WORKFLOW_DB_PORT", "5432"),
    }
}

use_postgres = os.getenv("USE_POSTGRES")
should_use_postgres = use_postgres.lower() == "true" if use_postgres is not None else os.getenv("WORKFLOW_DB_HOST") is not None

if not should_use_postgres:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

USE_TZ = True
TIME_ZONE = "UTC"
MIGRATION_MODULES = {"workflows": None}
