from django.urls import path
from . import views
from django.http import HttpResponse
from django.shortcuts import redirect

def debug_view(request):
    user_info = "Não autenticado"
    groups_info = "Nenhum"
    
    if request.user.is_authenticated:
        user_info = f"{request.user.username} (ID: {request.user.id})"
        groups = request.user.groups.all()
        if groups:
            groups_info = ", ".join([g.name for g in groups])
        else:
            groups_info = "Usuário não pertence a nenhum grupo"
    
    return HttpResponse(f"""
    <html>
    <head>
        <title>Teste de acesso ao módulo de vendas</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .info {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            h2 {{ color: #4a4a4a; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
            button, .button {{ 
                background-color: #4CAF50; color: white; padding: 10px 15px; 
                border: none; border-radius: 4px; cursor: pointer; text-decoration: none; 
                display: inline-block; margin: 5px;
            }}
            .warning {{ background-color: #ff9800; }}
        </style>
    </head>
    <body>
        <h1>Teste de acesso ao módulo de vendas</h1>
        
        <div class="info">
            <h2>Informações do usuário:</h2>
            <p><strong>Usuário:</strong> {user_info}</p>
            <p><strong>Autenticado:</strong> {request.user.is_authenticated}</p>
            <p><strong>Grupos:</strong> {groups_info}</p>
        </div>
        
        <div class="info">
            <h2>Links para teste:</h2>
            <p><a href="/vendas/" class="button">Ir para a lista de vendas</a></p>
            <p><a href="/vendas/dashboard/" class="button">Ir para o dashboard de vendas</a></p>
            <p><a href="/vendas/nova/" class="button">Criar nova venda</a></p>
        </div>
        
        <div class="info">
            <h2>Diagnóstico:</h2>
            <p>Se você está vendo esta página, o acesso à URL base do módulo de vendas está funcionando.</p>
            <p>Se você conseguir acessar os links acima, todas as views estão funcionando corretamente.</p>
            <p>Se algum erro ocorrer, verifique a mensagem e o status HTTP retornado.</p>
        </div>
    </body>
    </html>
    """)

urlpatterns = [
    # Página de debug
    path('debug/', debug_view, name='venda_debug'),
    
    # Dashboard de vendas
    path('dashboard/', views.venda_dashboard, name='venda_dashboard'),
    
    # Listar, criar, detalhar vendas
    path('', views.venda_lista, name='venda_lista'),  # Usando a view principal sem @cliente_required
    path('nova/', views.venda_nova, name='venda_nova'),
    path('<int:id>/detalhe/', views.venda_detalhe, name='venda_detalhe'),
    path('<int:id>/editar/', views.venda_editar, name='venda_editar'),
    path('<int:id>/finalizar/', views.venda_finalizar, name='venda_finalizar'),
    path('<int:id>/cancelar/', views.venda_cancelar, name='venda_cancelar'),
    
    # Gerenciar itens da venda
    path('<int:venda_id>/remover-item/<int:item_id>/', views.venda_item_remover, name='venda_item_remover'),
    
    # Gerenciar status da venda
    path('<int:id>/confirmar-pagamento/', views.venda_confirmar_pagamento, name='venda_confirmar_pagamento'),
    path('<int:id>/marcar-enviado/', views.venda_marcar_enviado, name='venda_marcar_enviado'),
    path('<int:id>/marcar-entregue/', views.venda_marcar_entregue, name='venda_marcar_entregue'),
    path('<int:id>/pdf/', views.venda_pdf, name='venda_pdf'),
    
    # API de clientes para vendas
    path('cliente/<int:cliente_id>/dados/', views.obter_dados_cliente, name='obter_dados_cliente'),
    path('cliente/atualizar-enderecos/', views.atualizar_enderecos_cliente, name='atualizar_enderecos_cliente'),
] 