import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SECRET_KEY = "dev-secret-key-change-me"


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_allowed_hosts() -> list[str]:
    raw_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")
    hosts = [host.strip() for host in raw_hosts.split(",") if host.strip()]
    return hosts or ["localhost"]


DEBUG = _get_bool_env("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = _get_allowed_hosts()

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "backend.app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "backend.config.urls"
TEMPLATES: list[dict] = []
WSGI_APPLICATION = "backend.config.wsgi.application"
ASGI_APPLICATION = "backend.config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

TWAPP_DATASETS_FILE = BASE_DIR / "data" / "datasets.yml"
TWAPP_DATA_DIR = BASE_DIR / "data"
TWAPP_CACHE_DIR = BASE_DIR / ".cache"
TWAPP_OUTPUT_DIR = BASE_DIR / "output"
