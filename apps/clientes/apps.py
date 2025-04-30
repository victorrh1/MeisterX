from django.apps import AppConfig


class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.clientes'
    path = 'apps/clientes'
    verbose_name = 'Clientes'
