from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def grupo_requerido(grupos_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not isinstance(grupos_permitidos, (list, tuple)):
                grupos = [grupos_permitidos]
            else:
                grupos = grupos_permitidos
            
            # Verifica se o usuário pertence a algum dos grupos permitidos
            if not any(request.user.groups.filter(name=grupo).exists() for grupo in grupos):
                messages.error(request, 'Você não tem permissão para acessar esta página.')
                return redirect('dashboard')
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return grupo_requerido('Admin')(view_func)

def equipe_required(view_func):
    return grupo_requerido(['Admin', 'Equipe'])(view_func)

def cliente_required(view_func):
    return grupo_requerido('Cliente')(view_func) 