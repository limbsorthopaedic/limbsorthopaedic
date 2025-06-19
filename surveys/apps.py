from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SurveysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'surveys'
    verbose_name = _('Patient Surveys')

    def ready(self):
        try:
            import surveys.signals  # noqa
        except ImportError:
            pass