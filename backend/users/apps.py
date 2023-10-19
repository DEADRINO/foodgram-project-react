from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Конфигурация приложения users."""
    name = 'users'
    verbose_name = 'Приложение users'
    default_auto_field = 'django.db.models.BigAutoField'
