from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Adiciona um usuário ao grupo Admin'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username do usuário')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = Usuario.objects.get(username=username)
            admin_group = Group.objects.get(name='Admin')
            user.groups.add(admin_group)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuário {username} adicionado ao grupo Admin com sucesso!'))
        except Usuario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuário {username} não encontrado.')) 