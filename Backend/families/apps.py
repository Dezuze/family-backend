from django.apps import AppConfig


class FamiliesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'families'

    def ready(self):
        import families.signals  # noqa: F401
