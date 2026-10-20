from pathlib import Path

from django.apps import AppConfig


class CareersConfig(AppConfig):
    """Configure the careers app when the project is mounted through aliased paths."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "careers"
    path = str(Path(__file__).resolve().parent)
