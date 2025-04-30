from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.produtos.models import ProdutoEmpresa
from apps.clientes.models import ClienteEmpresa

Usuario = get_user_model()

class MetodoEnvio(models.Model):
    """Métodos de envio disponíveis para as vendas"""
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True, null=True)
    taxa_fixa = models.DecimalField('Taxa Fixa', max_digits=10, decimal_places=2, default=0)
    ativo = models.BooleanField('Ativo', default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Método de Envio'
        verbose_name_plural = 'Métodos de Envio'
        ordering = ['nome']


class FormaPagamento(models.Model):
    """Formas de pagamento disponíveis para as vendas"""
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True, null=True)
    ativo = models.BooleanField('Ativo', default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Forma de Pagamento'
        verbose_name_plural = 'Formas de Pagamento'
        ordering = ['nome']


class StatusVenda(models.TextChoices):
    """Status possíveis para uma venda"""
    RASCUNHO = 'rascunho', 'Rascunho'
    PENDENTE = 'pendente', 'Pagamento Pendente'
    PAGO = 'pago', 'Pago'
    ENVIADO = 'enviado', 'Enviado'
    ENTREGUE = 'entregue', 'Entregue'
    CANCELADO = 'cancelado', 'Cancelado'


class Venda(models.Model):
    """
    Modelo principal de venda que registra uma transação de produtos
    """
    # Campos gerais
    usuario_vendedor = models.ForeignKey(Usuario, on_delete=models.PROTECT, 
                                        related_name='vendas_realizadas',
                                        verbose_name="Vendedor")
    
    # Cliente (pode ser um cliente cadastrado ou dados avulsos)
    cliente_cadastrado = models.ForeignKey(ClienteEmpresa, on_delete=models.PROTECT, 
                                        related_name='compras',
                                        verbose_name="Cliente Cadastrado",
                                        blank=True, null=True)
    cliente_nome = models.CharField('Nome do Cliente', max_length=200, blank=True, null=True)
    cliente_email = models.EmailField('Email do Cliente', max_length=255, blank=True, null=True)
    cliente_telefone = models.CharField('Telefone do Cliente', max_length=20, blank=True, null=True)
    
    # Dados de pagamento e entrega
    data_venda = models.DateTimeField('Data da Venda', auto_now_add=True)
    data_modificacao = models.DateTimeField('Última Modificação', auto_now=True)
    status = models.CharField('Status', max_length=20, choices=StatusVenda.choices, default=StatusVenda.RASCUNHO)
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT, 
                                        related_name='vendas',
                                        verbose_name="Forma de Pagamento")
    metodo_envio = models.ForeignKey(MetodoEnvio, on_delete=models.PROTECT, 
                                    related_name='vendas',
                                    verbose_name="Método de Envio")
    
    # Endereço de entrega
    endereco_entrega = models.TextField('Endereço de Entrega', blank=True, null=True)
    numero_entrega = models.CharField('Número', max_length=20, blank=True, null=True)
    cidade_entrega = models.CharField('Cidade', max_length=100, blank=True, null=True)
    estado_entrega = models.CharField('Estado', max_length=2, blank=True, null=True)
    cep_entrega = models.CharField('CEP', max_length=10, blank=True, null=True)
    
    # Valores
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2, default=0)
    desconto_percentual = models.DecimalField('Desconto (%)', max_digits=5, decimal_places=2, default=0,
                                             validators=[MinValueValidator(0), MaxValueValidator(100)])
    desconto_valor = models.DecimalField('Valor do Desconto', max_digits=10, decimal_places=2, default=0)
    valor_frete = models.DecimalField('Valor do Frete', max_digits=10, decimal_places=2, default=0)
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2, default=0)
    
    # Observações
    observacoes = models.TextField('Observações', blank=True, null=True)
    codigo_rastreamento = models.CharField('Código de Rastreamento', max_length=50, blank=True, null=True)
    
    def __str__(self):
        cliente = self.cliente_cadastrado.nome if self.cliente_cadastrado else self.cliente_nome
        return f"Venda #{self.id} - {cliente} ({self.get_status_display()})"
    
    def calcular_subtotal(self):
        """Calcula o subtotal baseado nos itens"""
        return sum(item.valor_total for item in self.itens.all())
    
    def calcular_desconto(self):
        """Calcula o valor do desconto baseado no percentual"""
        if self.desconto_percentual > 0:
            return (self.subtotal * Decimal(self.desconto_percentual / 100)).quantize(Decimal('0.01'))
        return self.desconto_valor
    
    def calcular_total(self):
        """Calcula o valor total da venda"""
        return self.subtotal - self.desconto_valor + self.valor_frete
    
    def atualizar_valores(self):
        """Atualiza os valores calculados"""
        self.subtotal = self.calcular_subtotal()
        self.desconto_valor = self.calcular_desconto()
        self.valor_total = self.calcular_total()
        self.save()
    
    def cancelar(self):
        """Cancela a venda e estorna os produtos para o estoque"""
        if self.status not in [StatusVenda.CANCELADO, StatusVenda.ENTREGUE]:
            # Estornar itens para o estoque
            for item in self.itens.all():
                produto = item.produto
                produto.estoque += item.quantidade
                produto.save()
            
            self.status = StatusVenda.CANCELADO
            self.save()
            return True
        return False
    
    def finalizar(self):
        """Finaliza a venda e muda o status para pago"""
        if self.status == StatusVenda.RASCUNHO or self.status == StatusVenda.PENDENTE:
            self.status = StatusVenda.PAGO
            self.save()
            return True
        return False
    
    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_venda']
        
        
class ItemVenda(models.Model):
    """
    Item de uma venda, representando um produto vendido
    """
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, 
                             related_name='itens',
                             verbose_name="Venda")
    produto = models.ForeignKey(ProdutoEmpresa, on_delete=models.PROTECT, 
                               related_name='vendas',
                               verbose_name="Produto")
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    valor_unitario = models.DecimalField('Valor Unitário', max_digits=10, decimal_places=2)
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
    
    def save(self, *args, **kwargs):
        # Calcula o valor total do item
        self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)
        
        # Atualiza os valores da venda
        self.venda.atualizar_valores()
    
    class Meta:
        verbose_name = 'Item da Venda'
        verbose_name_plural = 'Itens da Venda'
        ordering = ['produto__nome'] 