from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class Produto(models.Model):
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True, null=True)
    preco = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    estoque = models.IntegerField('Estoque', default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-data_criacao']

# Novo modelo para produtos cadastrados pelos clientes do sistema
class ProdutoEmpresa(models.Model):
    """
    Modelo que representa os produtos cadastrados por um usuário cliente do sistema.
    Implementa conceito de multitenancy para separar dados entre usuários.
    """
    usuario_proprietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, 
                                        related_name='produtos_empresa',
                                        verbose_name="Proprietário")
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True, null=True)
    preco = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    estoque = models.IntegerField('Estoque', default=0)
    imagem = models.ImageField('Imagem', upload_to='produtos/', blank=True, null=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    ativo = models.BooleanField('Ativo', default=True)

    def __str__(self):
        return self.nome
    
    def get_preco_formatado(self):
        """Retorna o preço formatado como moeda brasileira"""
        return f"R$ {self.preco:.2f}".replace('.', ',')
    
    class Meta:
        verbose_name = "Produto da Empresa"
        verbose_name_plural = "Produtos da Empresa"
        ordering = ['nome'] 