from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()

# Create your models here.

class Cliente(models.Model):
    nome = models.CharField('Nome', max_length=200)
    email = models.EmailField('Email', max_length=255)
    telefone = models.CharField('Telefone', max_length=20)
    endereco = models.TextField('Endereço', blank=True, null=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-data_cadastro']

class Endereco(models.Model):
    """
    Modelo que representa um endereço completo para um cliente.
    """
    TIPO_CHOICES = [
        ('principal', 'Principal'),
        ('cobranca', 'Cobrança'),
        ('entrega', 'Entrega'),
        ('outro', 'Outro'),
    ]
    
    cliente = models.ForeignKey('ClienteEmpresa', on_delete=models.CASCADE, 
                              related_name='enderecos',
                              verbose_name="Cliente")
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='principal')
    nome = models.CharField('Nome do Endereço', max_length=100, blank=True, null=True)
    cep = models.CharField('CEP', max_length=10, blank=True, null=True)
    logradouro = models.CharField('Logradouro', max_length=255)
    numero = models.CharField('Número', max_length=20)
    complemento = models.CharField('Complemento', max_length=100, blank=True, null=True)
    bairro = models.CharField('Bairro', max_length=100)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2)
    ativo = models.BooleanField('Ativo', default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome or self.tipo} - {self.cliente.nome}"
    
    @property
    def endereco_completo(self):
        """Retorna o endereço completo formatado"""
        partes = [
            self.logradouro,
            f"Nº {self.numero}",
            self.complemento,
            self.bairro,
            f"{self.cidade} - {self.estado}",
            f"CEP: {self.cep}" if self.cep else ""
        ]
        # Filtra partes vazias e junta com vírgulas
        return ", ".join([p for p in partes if p])
    
    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        ordering = ['tipo', '-data_cadastro']

class ClienteEmpresa(models.Model):
    """
    Modelo que representa os clientes cadastrados por um usuário cliente do sistema.
    Implementa conceito de multitenancy para separar dados entre usuários.
    """
    usuario_proprietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, 
                                        related_name='clientes_empresa',
                                        verbose_name="Proprietário")
    nome = models.CharField('Nome', max_length=200)
    email = models.EmailField('Email', max_length=255)
    telefone = models.CharField('Telefone', max_length=20)
    telefone_secundario = models.CharField('Telefone Secundário', max_length=20, blank=True, null=True)
    empresa = models.CharField('Empresa', max_length=200, blank=True, null=True)
    endereco_principal = models.TextField('Endereço Principal', max_length=500, blank=True, null=True)
    endereco_cidade = models.CharField('Cidade', max_length=100, blank=True, null=True)
    endereco_estado = models.CharField('Estado', max_length=2, blank=True, null=True)
    endereco_cep = models.CharField('CEP', max_length=10, blank=True, null=True)
    endereco_secundario = models.TextField('Endereço Secundário', max_length=500, blank=True, null=True)
    endereco_adicional = models.TextField('Endereço Adicional', max_length=500, blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True, null=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    ativo = models.BooleanField('Ativo', default=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Cliente da Empresa"
        verbose_name_plural = "Clientes da Empresa"
        ordering = ['-data_cadastro']