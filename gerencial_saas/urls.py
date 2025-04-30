"""
URL configuration for gerencial_saas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from apps.usuarios.views import pos_login_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    # Redireciona a raiz para o dashboard apropriado se autenticado, senão para login
    path('', login_required(pos_login_redirect, login_url='/usuarios/login/'), name='index'),
    path('dashboard/', include('apps.dashboard.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('produtos/', include('apps.produtos.urls')),
    path('vendas/', include('apps.vendas.urls')),
    path('perfil/', RedirectView.as_view(url='/usuarios/perfil/'), name='perfil_redirect'),
]
