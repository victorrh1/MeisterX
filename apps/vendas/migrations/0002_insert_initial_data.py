from django.db import migrations

def inserir_dados_iniciais(apps, schema_editor):
    FormaPagamento = apps.get_model('vendas', 'FormaPagamento')
    MetodoEnvio = apps.get_model('vendas', 'MetodoEnvio')
    
    # Criar formas de pagamento
    formas_pagamento = [
        {
            'nome': 'Cartão de Crédito',
            'descricao': 'Pagamento via cartão de crédito',
            'ativo': True
        },
        {
            'nome': 'Pix',
            'descricao': 'Pagamento via Pix',
            'ativo': True
        },
        {
            'nome': 'Boleto Bancário',
            'descricao': 'Pagamento via boleto bancário',
            'ativo': True
        }
    ]
    
    for forma in formas_pagamento:
        FormaPagamento.objects.create(**forma)
    
    # Criar métodos de envio
    metodos_envio = [
        {
            'nome': 'Correios - PAC',
            'descricao': 'Entrega via Correios - PAC',
            'taxa_fixa': 15.00,
            'ativo': True
        },
        {
            'nome': 'Correios - SEDEX',
            'descricao': 'Entrega via Correios - SEDEX',
            'taxa_fixa': 25.00,
            'ativo': True
        },
        {
            'nome': 'Entrega Expressa',
            'descricao': 'Entrega expressa em até 24h',
            'taxa_fixa': 35.00,
            'ativo': True
        }
    ]
    
    for metodo in metodos_envio:
        MetodoEnvio.objects.create(**metodo)

def reverter_dados_iniciais(apps, schema_editor):
    FormaPagamento = apps.get_model('vendas', 'FormaPagamento')
    MetodoEnvio = apps.get_model('vendas', 'MetodoEnvio')
    
    FormaPagamento.objects.all().delete()
    MetodoEnvio.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('vendas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(inserir_dados_iniciais, reverter_dados_iniciais),
    ] 