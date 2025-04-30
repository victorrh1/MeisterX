from django.db import models
from django.conf import settings
from django.utils import timezone

class CategoriaPlano(models.Model):
    """Categorias para planos de produtos"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Categoria de Plano"
        verbose_name_plural = "Categorias de Planos"


class Produto(models.Model):
    """Modelo de produto/serviço oferecido pelo sistema"""
    TIPO_CHOICES = (
        ('assinatura', 'Assinatura Mensal'),
        ('licenca', 'Licença Anual'),
        ('servico', 'Serviço Único'),
    )
    
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('suspenso', 'Suspenso'),
        ('cancelado', 'Cancelado'),
    )
    
    nome = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descricao = models.TextField()
    descricao_curta = models.CharField(max_length=255, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='assinatura')
    categoria = models.ForeignKey(CategoriaPlano, on_delete=models.SET_NULL, null=True, blank=True)
    duracao_dias = models.PositiveIntegerField(default=30, help_text="Duração em dias da assinatura ou licença")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    destaque = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    
    # Campos para recursos/features do produto
    usuarios_permitidos = models.PositiveIntegerField(default=1, help_text="Quantidade de usuários permitidos")
    armazenamento_gb = models.PositiveIntegerField(default=5, help_text="Espaço de armazenamento em GB")
    permite_exportacao = models.BooleanField(default=False)
    permite_api = models.BooleanField(default=False)
    suporte_24h = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nome
    
    def get_preco_formatado(self):
        return f"R$ {self.preco:.2f}".replace('.', ',')
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']


class AssinaturaProduto(models.Model):
    """Modelo que registra as assinaturas de clientes a produtos"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assinaturas')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='assinaturas')
    data_inicio = models.DateTimeField(default=timezone.now)
    data_expiracao = models.DateTimeField()
    renovacao_automatica = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=Produto.STATUS_CHOICES, default='ativo')
    notas = models.TextField(blank=True, null=True)
    ultimo_acesso = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.produto.nome}"
    
    def esta_ativo(self):
        """Verifica se a assinatura está ativa e dentro do prazo"""
        return self.status == 'ativo' and self.data_expiracao > timezone.now()
    
    def dias_restantes(self):
        """Retorna o número de dias restantes na assinatura"""
        if not self.esta_ativo():
            return 0
        delta = self.data_expiracao - timezone.now()
        return max(0, delta.days)
    
    def registrar_acesso(self):
        """Registra um acesso do usuário ao produto"""
        self.ultimo_acesso = timezone.now()
        self.save(update_fields=['ultimo_acesso'])
    
    def renovar(self, dias=None):
        """Renova a assinatura pelo período padrão ou número de dias especificado"""
        if dias is None:
            dias = self.produto.duracao_dias
        
        # Se expirada, recomeça a partir de hoje
        if self.data_expiracao < timezone.now():
            self.data_inicio = timezone.now()
            self.data_expiracao = timezone.now() + timezone.timedelta(days=dias)
        else:
            # Se ainda válida, adiciona os dias
            self.data_expiracao += timezone.timedelta(days=dias)
        
        self.status = 'ativo'
        self.save(update_fields=['data_inicio', 'data_expiracao', 'status'])
    
    def cancelar(self):
        """Cancela a assinatura"""
        self.status = 'cancelado'
        self.renovacao_automatica = False
        self.save(update_fields=['status', 'renovacao_automatica'])
    
    def get_percentual_tempo_restante(self):
        """Calcula o percentual de tempo restante para a assinatura expirar"""
        if not self.esta_ativo():
            return 0
        
        # Calcula o tempo total da assinatura em dias
        tempo_total = (self.data_expiracao - self.data_inicio).days
        # Se por algum motivo o tempo total for zero, evita divisão por zero
        if tempo_total <= 0:
            return 0
            
        # Calcula o tempo restante em dias
        tempo_restante = (self.data_expiracao - timezone.now()).days
        
        # Calcula o percentual
        percentual = (tempo_restante / tempo_total) * 100
        
        # Limita o valor entre 0 e 100
        return max(0, min(100, percentual))
    
    class Meta:
        verbose_name = "Assinatura de Produto"
        verbose_name_plural = "Assinaturas de Produtos"
        unique_together = ('usuario', 'produto')


class HistoricoUso(models.Model):
    """Registro de uso dos produtos pelos clientes"""
    assinatura = models.ForeignKey(AssinaturaProduto, on_delete=models.CASCADE, related_name='historico_uso')
    data_acesso = models.DateTimeField(auto_now_add=True)
    recurso_acessado = models.CharField(max_length=255)
    duracao_segundos = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Acesso de {self.assinatura.usuario.username} a {self.recurso_acessado}"
    
    class Meta:
        verbose_name = "Histórico de Uso"
        verbose_name_plural = "Históricos de Uso"
        ordering = ['-data_acesso']
