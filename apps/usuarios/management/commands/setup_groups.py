from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Cria os grupos padrão do sistema'

    def handle(self, *args, **kwargs):
        groups = ['Admin', 'Equipe', 'Cliente']
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{group_name}" criado com sucesso!'))
            else:
                self.stdout.write(self.style.WARNING(f'Grupo "{group_name}" já existe.')) 