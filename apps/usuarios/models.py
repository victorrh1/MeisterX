from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class Usuario(AbstractUser):
    # Campos extras que quiser adicionar (opcional)
    nome_completo = models.CharField(max_length=150, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True)
    two_factor_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    @property
    def grupo(self):
        """Retorna o nome do grupo principal do usuário"""
        grupos = ['Admin', 'Equipe', 'Cliente']
        for grupo in grupos:
            if self.groups.filter(name=grupo).exists():
                return grupo
        return None

    @property
    def badge_color(self):
        """Retorna a cor do badge baseado no grupo"""
        cores = {
            'Admin': 'red',
            'Equipe': 'blue',
            'Cliente': 'green'
        }
        return cores.get(self.grupo, 'gray')

    def is_admin(self):
        return self.groups.filter(name='Admin').exists()

    def is_equipe(self):
        return self.groups.filter(name='Equipe').exists()

    def is_cliente(self):
        return self.groups.filter(name='Cliente').exists()

    def get_dashboard_url(self):
        """Retorna a URL do dashboard apropriada para o tipo de usuário"""
        if self.is_admin():
            return '/dashboard/'
        elif self.is_equipe():
            return '/dashboard/equipe/'
        elif self.is_cliente():
            return '/dashboard/cliente/'
        return '/dashboard/'  # fallback

class TwoFactorCode(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_code(cls):
        """Gera um código OTP de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))

    class Meta:
        verbose_name = 'Código 2FA'
        verbose_name_plural = 'Códigos 2FA'

class PerfilUsuario(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    pending_approval = models.BooleanField(default=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    
    def approve(self):
        self.is_approved = True
        self.pending_approval = False
        self.approval_date = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
