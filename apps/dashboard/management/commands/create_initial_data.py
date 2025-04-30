from django.core.management.base import BaseCommand
from apps.dashboard.models import CategoriaPlano

class Command(BaseCommand):
    help = 'Cria dados iniciais para o sistema, como categorias de planos'

    def handle(self, *args, **options):
        self.stdout.write('Criando categorias de planos...')
        
        # Lista de categorias a serem criadas
        categorias = [
            {'nome': 'Básico', 'descricao': 'Planos básicos para iniciantes'},
            {'nome': 'Intermediário', 'descricao': 'Planos com recursos adicionais'},
            {'nome': 'Premium', 'descricao': 'Planos completos com todos os recursos'},
            {'nome': 'Empresarial', 'descricao': 'Planos específicos para empresas'},
            {'nome': 'Personalizado', 'descricao': 'Planos com configurações customizadas'}
        ]
        
        # Criar cada categoria, se ainda não existir
        categorias_criadas = 0
        for cat_data in categorias:
            categoria, created = CategoriaPlano.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={'descricao': cat_data['descricao'], 'ativo': True}
            )
            
            if created:
                categorias_criadas += 1
                self.stdout.write(self.style.SUCCESS(f'Categoria "{cat_data["nome"]}" criada com sucesso!'))
            else:
                self.stdout.write(f'Categoria "{cat_data["nome"]}" já existe, pulando...')
        
        # Exibir resumo
        self.stdout.write(self.style.SUCCESS(f'{categorias_criadas} novas categorias foram criadas.'))
        self.stdout.write(f'Total de categorias no sistema: {CategoriaPlano.objects.count()}') 