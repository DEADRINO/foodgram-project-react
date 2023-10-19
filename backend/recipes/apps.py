from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Конфигурация приложения recipes."""
    name = 'recipes'
    verbose_name = 'Рецепты'
    default_auto_field = 'django.db.models.BigAutoField'
