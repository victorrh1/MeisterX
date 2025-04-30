import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gerencial_saas.settings')
django.setup()

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

Usuario = get_user_model()

def add_user_to_admin(username):
    try:
        user = Usuario.objects.get(username=username)
        admin_group, created = Group.objects.get_or_create(name='Admin')
        user.groups.add(admin_group)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f'Usuário {username} adicionado ao grupo Admin com sucesso!')
    except Usuario.DoesNotExist:
        print(f'Usuário {username} não encontrado.')

if __name__ == '__main__':
    username = input('Digite o username do usuário: ')
    add_user_to_admin(username) 