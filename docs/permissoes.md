# Sistema de Permissões - Gerencial SaaS

## Visão Geral

O Gerencial SaaS implementa um sistema de controle de acesso baseado em grupos que garante que cada tipo de usuário (Administrador, Equipe, Cliente) tenha acesso apenas às funcionalidades relevantes para seu papel.

## Grupos de Usuários

### Admin
- Acesso completo ao sistema
- Pode gerenciar usuários, produtos, clientes e configurações
- Acesso a relatórios administrativos e estatísticas
- Dashboard com visão geral de todo o sistema

### Equipe
- Acesso ao painel da equipe
- Gerenciamento de clientes e produtos
- Acesso a relatórios operacionais
- Não possui acesso às configurações administrativas do sistema

### Cliente
- Acesso limitado ao painel do cliente
- Visualização apenas dos seus próprios dados
- Não possui acesso ao gerenciamento de usuários ou configurações
- Interface simplificada e focada nas necessidades do cliente

## Implementação Técnica

O sistema de permissões é implementado em três camadas:

### 1. Middlewares

#### GrupoMiddleware
- Controla o acesso às URLs com base no grupo do usuário
- Redireciona usuários que tentam acessar páginas não autorizadas
- Exibe mensagens informativas ao redirecionar

Localizado em: `apps/usuarios/middleware.py`

### 2. Decoradores

O sistema usa decoradores para proteger views específicas:

- `@admin_required`: Limita acesso apenas a administradores
- `@equipe_required`: Limita acesso a membros da equipe e administradores
- `@cliente_required`: Limita acesso a clientes

Localizado em: `apps/usuarios/decorators.py`

### 3. Permissões no Django Admin

O sistema também utiliza o sistema de permissões nativo do Django:

- Cada grupo tem permissões específicas nos modelos do sistema
- Controle granular de quais ações (visualizar, adicionar, editar, excluir) cada grupo pode realizar

## URLs Protegidas

### URLs de Admin
- `/dashboard/`
- `/admin/`
- `/usuarios/`
- `/relatorios/admin/`

### URLs de Equipe
- `/dashboard/equipe/`
- `/painel_equipe/`
- `/clientes/`
- `/produtos/`
- `/relatorios/equipe/`

### URLs de Cliente
- `/dashboard/cliente/`
- `/painel_cliente/`
- `/meus-dados/`
- `/meus-produtos/`

## URLs Públicas (Acessíveis a Todos Usuários Autenticados)
- `/perfil/`
- `/alterar-senha/`
- `/login/`
- `/logout/`
- `/static/`
- `/media/`

## Como Adicionar Novas Permissões

Para adicionar novas permissões a um grupo:

1. Acesse o Django Admin
2. Navegue até "Groups"
3. Selecione o grupo desejado
4. Adicione as permissões necessárias

Para proteger uma nova view:

```python
from apps.usuarios.decorators import admin_required, equipe_required, cliente_required

@login_required
@equipe_required
def minha_view(request):
    # Código da view aqui
    return render(request, 'template.html')
```

Para adicionar novas URLs protegidas, edite o middleware `GrupoMiddleware` em `apps/usuarios/middleware.py` e adicione os caminhos às listas apropriadas. 