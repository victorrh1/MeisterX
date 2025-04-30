import logging
import traceback
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

logger = logging.getLogger(__name__)

class DebugMiddleware:
    """
    Middleware para ajudar na depuração de problemas de requisições e renderização de templates
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            
            # Verificar se a resposta é um redirecionamento para uma mesma URL (evitar loops)
            if response.status_code == 302:
                redirect_url = response.url
                current_url = request.path
                
                # Se está redirecionando para a mesma URL, isso pode indicar um problema
                if redirect_url == current_url:
                    logger.warning(f"Loop de redirecionamento detectado: {current_url} -> {redirect_url}")
                    # Quebrar o loop redirecionando para a página inicial
                    return redirect('index')
            
            return response
        except Exception as e:
            # Registrar a exceção completa
            logger.error(f"Erro não tratado na requisição: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Em desenvolvimento, mostra detalhes do erro
            if settings.DEBUG:
                return HttpResponse(
                    f"<h1>Erro na renderização da página</h1>"
                    f"<p>URL: {request.path}</p>"
                    f"<p>Erro: {str(e)}</p>"
                    f"<pre>{traceback.format_exc()}</pre>"
                )
            
            # Em produção, redireciona para uma página de erro genérica
            return redirect('dashboard')

class LoginRequiredMiddleware:
    """
    Middleware para redirecionar usuários não autenticados para a página de login,
    exceto para as URLs permitidas sem autenticação.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Caminhos que não exigem autenticação
        allowed_paths = [
            '/usuarios/login/',
            '/usuarios/logout/',
            '/usuarios/recuperar-senha/',
            '/admin/login/',
            '/static/',
            '/media/',
        ]
        
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            # Verificar se o caminho atual é permitido sem autenticação
            is_allowed = False
            for path in allowed_paths:
                if request.path.startswith(path):
                    is_allowed = True
                    break
            
            # Se não estiver em um caminho permitido, redirecionar para o login
            if not is_allowed:
                return redirect('login')
        
        response = self.get_response(request)
        return response 