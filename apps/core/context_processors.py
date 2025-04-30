def notifications(request):
    """
    Adiciona o contador de notificações não lidas ao contexto
    """
    notificacoes_nao_lidas = 0
    if request.user.is_authenticated:
        notificacoes_nao_lidas = request.user.notificacoes.filter(lida=False).count()
    
    return {
        'notificacoes_nao_lidas': notificacoes_nao_lidas
    }

def dashboard_cards(request):
    """
    Gerencia os cards exibidos no dashboard para diferentes grupos de usuários
    """
    cards = []
    
    if not request.user.is_authenticated:
        return {'dashboard_cards': cards}
    
    # Identifica o grupo do usuário
    user_group = None
    if request.user.groups.filter(name='Admin').exists():
        user_group = 'Admin'
    elif request.user.groups.filter(name='Equipe').exists():
        user_group = 'Equipe'
    elif request.user.groups.filter(name='Cliente').exists():
        user_group = 'Cliente'
    
    # Cards para Admin
    if user_group == 'Admin':
        cards = [
            {
                'id': 'admin_users',
                'title': 'Usuários',
                'icon': 'fa-users',
                'color': 'primary',
                'description': 'Gerenciar usuários do sistema',
                'url': '/admin/auth/user/'
            },
            {
                'id': 'admin_groups',
                'title': 'Grupos',
                'icon': 'fa-user-shield',
                'color': 'success',
                'description': 'Gerenciar grupos e permissões',
                'url': '/admin/auth/group/'
            },
            {
                'id': 'admin_products',
                'title': 'Produtos',
                'icon': 'fa-box',
                'color': 'info',
                'description': 'Gerenciar catálogo de produtos',
                'url': '/produtos/lista/'
            }
        ]
    
    # Cards para Equipe
    elif user_group == 'Equipe':
        cards = [
            {
                'id': 'team_clients',
                'title': 'Clientes',
                'icon': 'fa-users',
                'color': 'primary',
                'description': 'Gerenciar clientes',
                'url': '/clientes/lista/'
            },
            {
                'id': 'team_sales',
                'title': 'Vendas',
                'icon': 'fa-shopping-cart',
                'color': 'success',
                'description': 'Registro e acompanhamento de vendas',
                'url': '/vendas/'
            },
            {
                'id': 'team_reports',
                'title': 'Relatórios',
                'icon': 'fa-chart-bar',
                'color': 'info',
                'description': 'Visualizar relatórios de desempenho',
                'url': '#'
            }
        ]
    
    # Cards para Cliente
    elif user_group == 'Cliente':
        cards = [
            {
                'id': 'client_purchases',
                'title': 'Minhas Compras',
                'icon': 'fa-shopping-bag',
                'color': 'primary',
                'description': 'Visualizar suas compras de materiais',
                'url': '/usuarios/minhas-compras/'
            },
            {
                'id': 'client_myclients',
                'title': 'Meus Clientes',
                'icon': 'fa-users',
                'color': 'warning',
                'description': 'Gerencie seus clientes',
                'url': '/clientes/meus-clientes/'
            },
            {
                'id': 'client_sales',
                'title': 'Vendas',
                'icon': 'fa-shopping-cart',
                'color': 'success',
                'description': 'Registro e acompanhamento de vendas',
                'url': '/vendas/'
            },
            {
                'id': 'client_myproducts',
                'title': 'Meus Produtos',
                'icon': 'fa-boxes',
                'color': 'danger',
                'description': 'Gerencie seu catálogo',
                'url': '/produtos/meus-produtos/'
            },
            #
            #{
                #'id': 'client_profile',
                #'title': 'Meus Dados',
                #'icon': 'fa-user',
                #'color': 'info',
                #'description': 'Seus dados cadastrais',
                #'url': '/usuarios/meus-dados/'
            #},
            {
                'id': 'client_account',
                'title': 'Meu Perfil',
                'icon': 'fa-id-card',
                'color': 'info',
                'description': 'Configurações da sua conta',
                'url': '/usuarios/perfil-usuario/'
            }
        ]
    
    return {'dashboard_cards': cards} 