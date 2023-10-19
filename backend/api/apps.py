from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Конфигурация приложения api."""
    name = 'api'
    verbose_name = 'API приложение'
    default_auto_field = 'django.db.models.BigAutoField'
