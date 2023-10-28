from django.apps import AppConfig


class PermitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permits'

    def ready(self):
        from . import signals
