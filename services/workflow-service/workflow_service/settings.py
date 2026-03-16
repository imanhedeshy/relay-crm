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

if os.getenv("WORKFLOW_DB_HOST") is None and os.getenv("USE_POSTGRES", "false").lower() != "true":
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

USE_TZ = True
TIME_ZONE = "UTC"
MIGRATION_MODULES = {"workflows": None}
