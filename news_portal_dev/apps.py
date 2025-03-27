from django.apps import AppConfig


class NewsPortalDevConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_portal_dev'

    def ready(self):
        from . import signals
