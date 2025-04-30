from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def audit_log(acao, descricao=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Registra o log
            request._audit_log = {
                'acao': acao,
                'descricao': descricao or ''
            }
            
            return response
        return _wrapped_view
    return decorator

def user_has_permission(permission_name):
    """
    Decorador para verificar se o usuário tem determinada permissão
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Você não tem permissão para acessar essa página.")
                return redirect('dashboard')
        return _wrapped_view
    return decorator 