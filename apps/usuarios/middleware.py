from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import resolve, reverse, NoReverseMatch
import time
from django.urls import resolve, Resolver404
from django.conf import settings
from django.contrib.auth.models import Group
from re import compile
from .models import PerfilUsuario

class LoginRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/login/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            if self.is_ip_blocked(ip):
                # Verifica se o sistema de mensagens está disponível
                try:
                    messages.error(request, 'Muitas tentativas de login. Tente novamente em alguns minutos.')
                except:
                    pass  # Ignora erro se o sistema de mensagens não estiver disponível
                return render(request, 'registration/login.html')
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_ip_blocked(self, ip):
        # Checa se o IP está bloqueado
        block_key = f'login_block_{ip}'
        return cache.get(block_key, False)


class GrupoMiddleware:
    """
    Middleware que controla o acesso às páginas com base nos grupos de usuários.
    Garante que cada grupo (Admin, Cliente, Equipe) veja apenas o que está autorizado.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs públicas que não precisam de autenticação
        self.PUBLIC_URLS = [
            r'^/admin/',
            r'^/static/',
            r'^/media/',
            r'^/usuarios/login/$',
            r'^/usuarios/logout/$',
            r'^/usuarios/register/$',
            r'^/usuarios/recuperar-senha/',
            r'^/$'
        ]
        
        # URLs de acesso pendente
        self.PENDING_URLS = [
            r'^/dashboard/pendente/$',
            r'^/usuarios/perfil-usuario/$',
            r'^/usuarios/contato/$',
            r'^/usuarios/logout/$'
        ]
        
        # Compilar expressões regulares
        self.public_patterns = [compile(url) for url in self.PUBLIC_URLS]
        self.pending_patterns = [compile(url) for url in self.PENDING_URLS]

    def __call__(self, request):
        path = request.path_info.lstrip('/')
        
        # Verificar se a URL é pública
        print(f"[GrupoMiddleware] Iniciando processamento para: {request.path}")
        
        # Se o usuário estiver autenticado
        if request.user.is_authenticated:
            print(f"[GrupoMiddleware] Usuário autenticado: {request.user.username}")
            
            # Obter grupos do usuário
            grupos = [g.name for g in request.user.groups.all()]
            print(f"[GrupoMiddleware] Grupos do usuário: {grupos}")
            
            # Verificar se o usuário está pendente de aprovação
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.pending_approval:
                    print(f"[GrupoMiddleware] Usuário pendente de aprovação")
                    
                    # Verificar se a URL é permitida para usuários pendentes
                    url_pendente = False
                    for pattern in self.pending_patterns:
                        if pattern.match(request.path):
                            url_pendente = True
                            break
                    
                    # Se não for URL permitida para pendentes e não for pública, redireciona
                    if not url_pendente:
                        url_publica = False
                        for pattern in self.public_patterns:
                            if pattern.match(request.path):
                                url_publica = True
                                break
                        
                        if not url_publica:
                            print(f"[GrupoMiddleware] Redirecionando para dashboard pendente")
                            messages.warning(request, "Seu acesso está pendente de aprovação pelo administrador.")
                            return redirect('dashboard_pendente')
            except PerfilUsuario.DoesNotExist:
                # Se não tem perfil, não faz nada
                pass
            
            print(f"[GrupoMiddleware] Caminho atual: {request.path}")
            
            # Verificar URLs públicas
            for pattern in self.public_patterns:
                if pattern.match(request.path):
                    print(f"[GrupoMiddleware] URL pública encontrada: {request.path}")
                    return self.get_response(request)
            
            # Verificar acesso baseado nos grupos do usuário
            admin_access = 'Admin' in grupos
            equipe_access = 'Equipe' in grupos
            cliente_access = 'Cliente' in grupos
                
            # Verificar URLs específicas para cada grupo
            if request.path.startswith('/dashboard/admin/') and not admin_access:
                print(f"[GrupoMiddleware] 403: URL de Admin, mas usuário não é Admin")
                messages.error(request, "Você não tem permissão para acessar esta área.")
                return redirect('dashboard')
                
            if request.path.startswith('/dashboard/equipe/') and not (admin_access or equipe_access):
                print(f"[GrupoMiddleware] 403: URL de Equipe, mas usuário não é Admin nem Equipe")
                messages.error(request, "Você não tem permissão para acessar esta área.")
                return redirect('dashboard')
                
            if request.path.startswith('/dashboard/cliente/') and not (admin_access or equipe_access or cliente_access):
                print(f"[GrupoMiddleware] 403: URL de Cliente, mas usuário não tem acesso")
                messages.error(request, "Você não tem permissão para acessar esta área.")
                return redirect('dashboard')
        
        return self.get_response(request) 