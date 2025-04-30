from django.shortcuts import redirect
from django.urls import resolve, reverse, NoReverseMatch
from django.conf import settings

class RedirectToDashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"[DashboardMiddleware] Iniciando processamento para: {request.path_info}")
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Se não estiver autenticado, não faz nada
        if not request.user.is_authenticated:
            print(f"[DashboardMiddleware] Usuário não autenticado, passando adiante")
            return None

        print(f"[DashboardMiddleware] Usuário autenticado: {request.user.username}")
        print(f"[DashboardMiddleware] Grupos do usuário: {[g.name for g in request.user.groups.all()]}")

        # Verifica apenas a raiz e redireciona
        current_url = request.path_info
        print(f"[DashboardMiddleware] URL atual: {current_url}")
        
        if current_url in ['/', '/home/', '/index/']:
            print("[DashboardMiddleware] URL raiz detectada, verificando grupo")
            try:
                if request.user.groups.filter(name='Cliente').exists():
                    print("[DashboardMiddleware] Redirecionando cliente para dashboard")
                    return redirect('cliente_dashboard')
                elif request.user.groups.filter(name='Equipe').exists():
                    print("[DashboardMiddleware] Redirecionando equipe para dashboard")
                    return redirect('equipe_dashboard')
                elif request.user.groups.filter(name='Admin').exists():
                    print("[DashboardMiddleware] Redirecionando admin para dashboard")
                    return redirect('admin_dashboard')
            except Exception as e:
                print(f"[DashboardMiddleware] Erro ao redirecionar: {e}")
                return None

        print("[DashboardMiddleware] Nenhuma ação necessária")
        return None 