# Arquitetura do Sistema

Este documento descreve a arquitetura do Gerencial SaaS, incluindo seus componentes principais, o fluxo de dados e as interações entre diferentes partes do sistema.

## Visão Arquitetural

O Gerencial SaaS segue uma arquitetura em camadas baseada no padrão Model-View-Template (MVT) do Django, com extensões para segurança e personalização por perfil de usuário.

```
+-------------------------------------------+
|                                           |
|              Navegador Web                |
|                                           |
+-------------------------------------------+
                   ▲  |
                   |  | HTTP/HTTPS
                   |  ▼
+-------------------------------------------+
|            Servidor Web (IIS)             |
+-------------------------------------------+
                   ▲  |
                   |  | WSGI
                   |  ▼
+-------------------------------------------+
|                                           |
|  +--------+  +------------+  +---------+  |
|  |        |  |            |  |         |  |
|  | URLs   |->| Middlewares|->| Views   |  |
|  |        |  |            |  |         |  |
|  +--------+  +------------+  +---------+  |
|                |      ▲          |  ▲     |
|                ▼      |          ▼  |     |
|           +------------+       +--------+ |
|           |            |       |        | |
|           | Context    |<----->| Models | |
|           | Processors |       |        | |
|           |            |       +--------+ |
|           +------------+          |  ▲    |
|                |                  ▼  |    |
|                ▼               +--------+ |
|           +------------+       |        | |
|           |            |       | Banco  | |
|           | Templates  |<----->| de     | |
|           |            |       | Dados  | |
|           +------------+       |        | |
|                                +--------+ |
|                                           |
+-------------------------------------------+
```

## Componentes Principais

### 1. Roteamento de URLs

O sistema de roteamento do Django mapeia URLs para views específicas:

- **URLs Raiz**: Definidas em `gerencial_saas/urls.py`, direcionam para as apps específicas
- **URLs por App**: Cada app tem seu próprio arquivo `urls.py` com rotas específicas daquele módulo
- **Padrão de Nomenclatura**: As rotas geralmente seguem o padrão `nome_do_recurso/ação/`

### 2. Middlewares

Os middlewares processam cada requisição antes de chegar às views e depois de gerada a resposta:

- **GrupoMiddleware**: Controla acesso baseado em grupos de usuário (`apps/usuarios/middleware.py`)
- **RedirectToDashboardMiddleware**: Direciona usuários ao dashboard correto (`apps/dashboard/middleware.py`)
- **DebugMiddleware**: Ajuda na depuração em ambiente de desenvolvimento (`apps/core/middlewares.py`)
- **AuditLogMiddleware**: Registra ações importantes para auditoria (`apps/core/middleware.py`)
- **LoginRateLimitMiddleware**: Protege contra tentativas excessivas de login (`apps/usuarios/middleware.py`)

### 3. Views (Controladores)

As views processam requisições, interagem com o banco de dados e renderizam templates:

- **Views Baseadas em Função**: A maioria das views são funções decoradas com `@login_required`
- **Decoradores de Permissão**: Controlam acesso fino usando `@admin_required`, `@equipe_required`, etc.
- **Separação por Módulo**: Cada app tem suas próprias views em `views.py`

### 4. Models (Modelos de Dados)

Os models definem a estrutura do banco de dados e a lógica de negócios:

- **Model de Usuário Personalizado**: Estende o modelo base do Django (`apps/usuarios/models.py`)
- **Modelos por Domínio**: Cada app define seus próprios models relacionados à sua funcionalidade
- **Relacionamentos Lógicos**: Os models se conectam através de chaves estrangeiras para formar o grafo de dados

### 5. Templates

Os templates definem a interface de usuário:

- **Template Base**: `templates/base.html` define a estrutura comum a todas as páginas
- **Herança**: Todos os templates específicos herdam do template base
- **Partials**: Componentes reutilizáveis são definidos em `templates/partials/`
- **Organização por App**: Cada app tem seus próprios templates em diretórios dedicados

### 6. Context Processors

Os context processors adicionam dados a todos os templates:

- **Notificações**: Adiciona notificações não lidas a todos os templates
- **Informações do Usuário**: Adiciona dados do perfil do usuário atual
- **Menus Dinâmicos**: Constrói o menu lateral baseado no grupo do usuário

## Fluxo de Dados

### Fluxo de Requisição/Resposta

```
+------------------------------------+
| 1. Usuário acessa URL              |
+------------------------------------+
                 |
                 ▼
+------------------------------------+
| 2. URLs mapeiam requisição à view  |
+------------------------------------+
                 |
                 ▼
+------------------------------------+
| 3. Middlewares processam requisição|
|    - Verificação de autenticação   |
|    - Controle de acesso por grupo  |
|    - Redirecionamentos condicionais|
+------------------------------------+
                 |
                 ▼
+------------------------------------+
| 4. View processa a requisição      |
|    - Decoradores validam permissões|
|    - Lógica de negócio é aplicada  |
|    - Interação com models/BD       |
+------------------------------------+
                 |
                 ▼
+------------------------------------+
| 5. Template é renderizado          |
|    - Context processors executados |
|    - Dados passados para template  |
|    - HTML é gerado                 |
+------------------------------------+
                 |
                 ▼
+------------------------------------+
| 6. Middlewares processam resposta  |
|    - Logs de auditoria             |
|    - Transformações finais         |
+------------------------------------+
                 |
                 ▼
+------------------------------------+
| 7. Resposta enviada ao navegador   |
+------------------------------------+
```

### Fluxo de Autenticação

```
+-------------------------+    +-------------------------+    +-------------------------+
| Login                   |    | Verificação de Grupo    |    | Redirecionamento        |
|                         |    |                         |    |                         |
| 1. Usuário insere       |    | 1. GrupoMiddleware     |    | 1. RedirectToMiddleware |
|    credenciais          | -> |    verifica grupos     | -> |    determina dashboard  |
| 2. View de login        |    |    do usuário          |    |    apropriado           |
|    autentica usuário    |    | 2. Define permissões   |    | 2. Usuário é levado ao  |
| 3. Sessão é criada      |    |    baseadas no grupo   |    |    seu dashboard        |
+-------------------------+    +-------------------------+    +-------------------------+
```

### Fluxo de Dados do Dashboard

```
+-------------------------+
| Usuário acessa dashboard|
+-------------------------+
            |
            ▼
+-------------------------+
| Views identificam grupo |
| do usuário e preparam   |
| dados relevantes        |
+-------------------------+
            |
            ▼
+---------------------------+
| Dados consultados:        |
| - Estatísticas de vendas  |
| - Produtos populares      |
| - Clientes ativos         |
| - Notificações            |
+---------------------------+
            |
            ▼
+---------------------------+
| Context processors        |
| adicionam dados globais   |
+---------------------------+
            |
            ▼
+---------------------------+
| Template renderiza        |
| interface personalizada   |
| com cards específicos     |
+---------------------------+
```

## Padrões Arquiteturais

### 1. Camadas de Segurança

A segurança é implementada em múltiplas camadas:

1. **Autenticação**: Sistema de login com Django Authentication
2. **Grupos**: Controle de acesso baseado em grupos (Admin, Equipe, Cliente)
3. **Middlewares**: Filtram requisições baseadas no grupo do usuário
4. **Decoradores**: Refinam permissões em views específicas
5. **Templates Condicionais**: Mostram/escondem elementos baseados no grupo

### 2. Multi-tenant

O sistema suporta múltiplos clientes (tenants) em uma única instância:

1. **Filtro por Proprietário**: Models incluem campos como `usuario_proprietario`
2. **Queries Filtradas**: Views automaticamente limitam dados ao usuário atual
3. **Isolamento Lógico**: Cada cliente vê apenas seus dados

### 3. Dashboard Personalizado

A experiência do usuário é personalizada por grupo:

1. **Dashboard Específico**: Cada grupo tem uma view dedicada de dashboard
2. **RedirectMiddleware**: Direciona usuários para seu dashboard correspondente
3. **Cards Dinâmicos**: O conteúdo visualizado é adaptado ao perfil do usuário

## Comunicação entre Módulos

Os módulos do sistema se comunicam principalmente através de:

1. **Banco de Dados**: Models de diferentes apps se relacionam via ForeignKeys
2. **Imports Diretos**: Um app pode importar e usar componentes de outro app
3. **Sinais do Django**: Para comunicação assíncrona entre componentes

## Escalabilidade e Performance

O design permite escalabilidade através de:

1. **Separação por App**: Cada funcionalidade em um app independente
2. **Módulos Desacoplados**: Baixo acoplamento entre componentes
3. **Cache Configurável**: Suporte a cache em múltiplos níveis
4. **Banco de Dados Flexível**: Funciona com SQLite ou PostgreSQL (dev) e (prod)

## Integrações Potenciais

A arquitetura permite integração com:

1. **APIs Externas**: Pontos de extensão para serviços de terceiros
2. **Gateways de Pagamento**: Integração com processadores de pagamento
3. **Sistemas de Email**: Para comunicação com clientes
4. **Outros Sistemas**: Via API ou importação/exportação de dados

Continue para a próxima seção: [Módulos do Sistema](modulos/README.md) 