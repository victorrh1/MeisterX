from django.apps import AppConfig

class ProdutosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.produtos'
    path = 'apps/produtos'
    verbose_name = 'Produtos' 