from django.apps import AppConfig


class VendasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vendas'
    verbose_name = 'Vendas'
    
    def ready(self):
        import apps.vendas.signals  # noqa 