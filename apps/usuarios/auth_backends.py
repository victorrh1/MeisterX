from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .views import send_two_factor_code

User = get_user_model()

class RateLimitedAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not request or not username or not password:
            return None

        # Obtém o IP do cliente
        ip = self.get_client_ip(request)
        
        # Checa se o IP está bloqueado
        if self.is_ip_blocked(ip):
            return None

        # Tenta autenticar o usuário
        user = super().authenticate(request, username=username, password=password, **kwargs)
        
        if user is None:
            # Incrementa o contador de tentativas falhas
            self.increment_failed_attempts(ip)
        else:
            # Limpa as tentativas falhas em caso de sucesso
            self.clear_failed_attempts(ip)
            
            # Se o usuário tem 2FA ativado, envia o código
            if user.two_factor_enabled:
                # Envia o código por email
                send_two_factor_code(user)
                
                # Configura a sessão para exigir verificação
                if request and hasattr(request, 'session'):
                    request.session['requires_2fa'] = True
                    request.session['user_id_2fa'] = user.id
                    
                # Retorna None para não completar o login ainda
                return None
        
        return user

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_ip_blocked(self, ip):
        block_key = f'login_block_{ip}'
        return cache.get(block_key, False)

    def increment_failed_attempts(self, ip):
        attempts_key = f'login_attempts_{ip}'
        block_key = f'login_block_{ip}'
        
        # Incrementa o contador de tentativas
        attempts = cache.get(attempts_key, 0) + 1
        
        if attempts >= 5:
            # Bloqueia o IP por 10 minutos
            cache.set(block_key, True, 600)  # 600 segundos = 10 minutos
            # Limpa o contador de tentativas
            cache.delete(attempts_key)
        else:
            # Atualiza o contador de tentativas (expira em 10 minutos)
            cache.set(attempts_key, attempts, 600)

    def clear_failed_attempts(self, ip):
        attempts_key = f'login_attempts_{ip}'
        block_key = f'login_block_{ip}'
        
        # Remove as chaves do cache
        cache.delete(attempts_key)
        cache.delete(block_key) 