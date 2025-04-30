from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cliente/', views.cliente_dashboard, name='cliente_dashboard'),
    path('equipe/', views.equipe_dashboard, name='equipe_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('painel-cliente/', views.painel_cliente, name='painel_cliente'),
    path('painel-equipe/', views.painel_equipe, name='painel_equipe'),
    path('exportar/<str:format>/', views.exportar_relatorio, name='exportar_relatorio'),
    path('cadastrar-produto/', views.cadastrar_produto_demo, name='cadastrar_produto_demo'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    path('pendente/', views.dashboard_pendente, name='dashboard_pendente'),
] 