from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

def create_groups(apps, schema_editor):
    # Criando grupos
    admin_group = Group.objects.create(name='Admin')
    cliente_group = Group.objects.create(name='Cliente')
    equipe_group = Group.objects.create(name='Equipe')
    
    # Obtendo o modelo de usuário
    Usuario = get_user_model()
    
    # Obtendo content types
    usuario_ct = ContentType.objects.get_for_model(Usuario)
    
    # Criando permissões específicas
    view_dashboard = Permission.objects.create(
        codename='view_dashboard',
        name='Can view dashboard',
        content_type=usuario_ct,
    )
    manage_users = Permission.objects.create(
        codename='manage_users',
        name='Can manage users',
        content_type=usuario_ct,
    )
    view_reports = Permission.objects.create(
        codename='view_reports',
        name='Can view reports',
        content_type=usuario_ct,
    )
    
    # Atribuindo permissões aos grupos
    admin_group.permissions.add(
        *Permission.objects.all()  # Todas as permissões para admin
    )
    
    equipe_group.permissions.add(
        view_dashboard,
        view_reports
    )
    
    cliente_group.permissions.add(
        view_dashboard
    )

def remove_groups(apps, schema_editor):
    Group.objects.filter(name__in=['Admin', 'Cliente', 'Equipe']).delete()
    Permission.objects.filter(codename__in=['view_dashboard', 'manage_users', 'view_reports']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ] 