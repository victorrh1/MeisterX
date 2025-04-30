from django.db import models # type: ignore
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Create your models here.
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    quantidade_estoque = models.IntegerField(default=0)

    def __str__(self):
        return self.nome

class AuditLog(models.Model):
    ACOES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('LOGIN_FALHA', 'Falha no Login'),
        ('CRIAR', 'Criação de Registro'),
        ('EDITAR', 'Edição de Registro'),
        ('DELETAR', 'Deleção de Registro'),
        ('2FA', 'Autenticação 2FA'),
        ('SENHA', 'Alteração de Senha'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuário'
    )
    acao = models.CharField(
        max_length=20,
        choices=ACOES,
        verbose_name='Ação'
    )
    descricao = models.TextField(
        verbose_name='Descrição'
    )
    ip = models.GenericIPAddressField(
        verbose_name='Endereço IP'
    )
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-data_hora']

    def __str__(self):
        return f'{self.get_acao_display()} - {self.usuario} - {self.data_hora}'

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificacoes'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Se é uma nova notificação e precisa enviar email
        enviar_email = kwargs.pop('enviar_email', False) if 'enviar_email' in kwargs else False
        if not self.pk and enviar_email:
            self.enviar_notificacao_email()
        super().save(*args, **kwargs)

    def enviar_notificacao_email(self):
        """Envia a notificação por email usando um template HTML"""
        context = {
            'titulo': self.title,
            'mensagem': self.message,
            'usuario': self.user,
            'tipo': 'INFO'  # Valor padrão para compatibilidade com o template
        }
        
        html_message = render_to_string('emails/notificacao.html', context)
        
        send_mail(
            subject=self.title,
            message=self.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
            html_message=html_message
        )

    @classmethod
    def criar_notificacao(cls, usuario, mensagem, titulo=None, enviar_email=False):
        """Método de classe para facilitar a criação de notificações"""
        if not titulo:
            titulo = 'Nova notificação'
            
        notificacao = cls.objects.create(
            user=usuario,
            message=mensagem,
            title=titulo
        )
        
        if enviar_email:
            notificacao.enviar_notificacao_email()
            
        return notificacao