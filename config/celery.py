import os

from celery import Celery

# Point Celery to the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# Or "config.settings.production" in production

app = Celery("config")

# Load any settings prefixed with CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py files in installed apps
app.autodiscover_tasks()