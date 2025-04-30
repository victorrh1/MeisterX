from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    # Criar grupos se não existirem
    groups = ['Admin', 'Equipe', 'Cliente']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)

def delete_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Admin', 'Equipe', 'Cliente']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, delete_groups),
    ] 