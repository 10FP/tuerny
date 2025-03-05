from django.apps import AppConfig


class TuernyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tuerny_app'

    def ready(self):
        import tuerny_app.signals