from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    path = 'apps/core'
    
    def ready(self):
        # Garantir que os templatetags sejam carregados
        from django.template.defaulttags import register
        import apps.core.templatetags.core_extras