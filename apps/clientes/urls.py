from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista, name='clientes_lista'),
    path('novo/', views.novo, name='cliente_novo'),
    path('<int:id>/', views.detalhe, name='cliente_detalhe'),
    path('<int:id>/editar/', views.editar, name='cliente_editar'),
    path('<int:id>/deletar/', views.deletar, name='cliente_deletar'),
    
    # URLs para clientes da empresa
    path('meus-clientes/', views.cliente_empresa_lista, name='cliente_empresa_lista'),
    path('meus-clientes/novo/', views.cliente_empresa_novo, name='cliente_empresa_novo'),
    path('meus-clientes/<int:id>/', views.cliente_empresa_detalhe, name='cliente_empresa_detalhe'),
    path('meus-clientes/<int:id>/editar/', views.cliente_empresa_editar, name='cliente_empresa_editar'),
    path('meus-clientes/<int:id>/excluir/', views.cliente_empresa_excluir, name='cliente_empresa_excluir'),
    
    # API de endereços
    path('meus-clientes/<int:cliente_id>/enderecos/', views.gerenciar_enderecos, name='gerenciar_enderecos'),
    
    # Cadastro rápido
    path('cadastro-rapido/', views.cliente_cadastrar_rapido, name='cliente_cadastrar_rapido'),
    
    # URLs de endereços
    path('cliente/<int:cliente_id>/endereco/adicionar/', views.adicionar_endereco, name='adicionar_endereco'),
    path('endereco/<int:endereco_id>/editar/', views.editar_endereco, name='editar_endereco'),
    path('endereco/<int:endereco_id>/remover/', views.remover_endereco, name='remover_endereco'),
] 