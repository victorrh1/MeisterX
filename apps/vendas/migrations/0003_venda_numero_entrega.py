# Generated by Django 5.2 on 2025-04-26 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0002_insert_initial_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='venda',
            name='numero_entrega',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Número'),
        ),
    ]
