from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.lista, name='produto_lista'),
    path('novo/', views.novo, name='produto_novo'),
    path('editar/<int:id>/', views.editar, name='produto_editar'),
    
    # URLs para o módulo de produtos do cliente
    path('meus-produtos/', views.produto_empresa_lista, name='produto_empresa_lista'),
    path('meus-produtos/novo/', views.produto_empresa_novo, name='produto_empresa_novo'),
    path('meus-produtos/editar/<int:id>/', views.produto_empresa_editar, name='produto_empresa_editar'),
    path('meus-produtos/excluir/<int:id>/', views.produto_empresa_excluir, name='produto_empresa_excluir'),
] 