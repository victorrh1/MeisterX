# Estrutura do Projeto

Este documento descreve a estrutura de diretórios e arquivos do Gerencial SaaS, explicando a organização do código e a função de cada componente principal.

## Visão Geral da Estrutura

O projeto segue uma estrutura modular baseada em apps Django, organizando o código em componentes funcionais separados.

```
gerencial_saas/
│
├── apps/                  # Aplicações principais do sistema
│   ├── core/              # Funcionalidades centrais e compartilhadas
│   ├── dashboard/         # Dashboard e visualizações principais
│   ├── usuarios/          # Gestão de usuários e autenticação
│   ├── clientes/          # Gestão de clientes
│   ├── produtos/          # Gestão de produtos
│   └── vendas/            # Gestão de vendas
│
├── docs/                  # Documentação do projeto
│
├── gerencial_saas/        # Configurações principais do projeto Django
│   ├── settings.py        # Configurações do Django
│   ├── urls.py            # Configuração de URLs principal
│   ├── wsgi.py            # Configuração WSGI para produção
│   └── asgi.py            # Configuração ASGI para produção
│
├── static/                # Arquivos estáticos (CSS, JS, imagens, etc.)
│   ├── css/
│   ├── js/
│   └── img/
│
├── staticfiles/           # Arquivos estáticos coletados para produção
│
├── templates/             # Templates HTML do projeto
│   ├── base.html          # Template base que outros herdam
│   ├── partials/          # Componentes reutilizáveis
│   ├── core/              # Templates do app core
│   ├── dashboard/         # Templates do app dashboard
│   ├── usuarios/          # Templates do app usuarios
│   ├── clientes/          # Templates do app clientes
│   ├── produtos/          # Templates do app produtos
│   └── vendas/            # Templates do app vendas
│
├── venv/                  # Ambiente virtual Python (não versionado)
│
├── .env                   # Variáveis de ambiente (não versionado)
├── .gitignore             # Arquivos ignorados pelo Git
├── db.sqlite3             # OBS: Antes era sqlite3, mas migrei para Postgresql
├── manage.py              # Script de gerenciamento do Django
└── requirements.txt       # Dependências do projeto
```

## Detalhamento dos Principais Diretórios

### Apps (`apps/`)

Cada app do Django é um módulo que contém um conjunto específico de funcionalidades:

#### Core (`apps/core/`)

```
core/
├── __init__.py
├── admin.py            # Configurações do admin Django
├── apps.py             # Configuração da aplicação
├── context_processors.py  # Processadores de contexto para templates
├── middleware.py       # Middleware para auditoria
├── middlewares.py      # Middlewares adicionais para debug
├── models.py           # Modelos de dados centrais
├── templatetags/       # Tags e filtros personalizados para templates
├── tests.py            # Testes automatizados
├── urls.py             # Configuração de URLs do app
└── views.py            # Views/Controladores do app
```

O app `core` contém funcionalidades compartilhadas utilizadas por outros apps, como notificações, logging, auditorias e componentes de UI reutilizáveis.

#### Dashboard (`apps/dashboard/`)

```
dashboard/
├── __init__.py
├── admin.py            # Configurações do admin Django
├── apps.py             # Configuração da aplicação
├── middleware.py       # Middleware para redirecionamento de dashboard
├── models.py           # Modelos de dados específicos do dashboard
├── tests.py            # Testes automatizados
├── urls.py             # Configuração de URLs do app
└── views.py            # Views/Controladores do dashboard
```

O app `dashboard` gerencia os diferentes painéis iniciais para cada tipo de usuário (Admin, Equipe, Cliente).

#### Usuários (`apps/usuarios/`)

```
usuarios/
├── __init__.py
├── admin.py            # Configurações do admin Django
├── apps.py             # Configuração da aplicação
├── auth_backends.py    # Backend de autenticação personalizado
├── decorators.py       # Decoradores para controle de acesso
├── forms.py            # Formulários para autenticação e perfil
├── middleware.py       # Middleware para controle de acesso e grupos
├── models.py           # Modelo de usuário personalizado
├── tests.py            # Testes automatizados
├── urls.py             # Configuração de URLs do app
└── views.py            # Views/Controladores para autenticação
```

O app `usuarios` gerencia autenticação, autorização, perfis de usuário e controles de acesso.

### Templates (`templates/`)

Os templates seguem uma estrutura organizada por app, com componentes comuns extraídos para o diretório `partials/`:

```
templates/
├── base.html           # Template base com estrutura HTML, cabeçalho e rodapé
├── index.html          # Página inicial/landing page
├── login.html          # Página de login principal
├── partials/           # Componentes reutilizáveis de UI
│   ├── cards_dinamicos.html  # Componente de cards para dashboard
│   ├── footer.html     # Rodapé compartilhado
│   ├── header.html     # Cabeçalho compartilhado
│   ├── menu.html       # Menu de navegação lateral
│   └── notifications.html  # Componente de notificações
│
├── usuarios/           # Templates específicos de usuários
├── dashboard/          # Templates específicos de dashboard
├── clientes/           # Templates específicos de clientes
├── produtos/           # Templates específicos de produtos
└── vendas/             # Templates específicos de vendas
```

### Configurações do Projeto (`gerencial_saas/`)

Este diretório contém as configurações centrais do Django:

```
gerencial_saas/
├── __init__.py
├── settings.py         # Configurações do Django (instalação de apps, BD, etc.)
├── urls.py             # Configuração de URLs raiz do projeto
├── wsgi.py             # Configuração WSGI para servidores web
└── asgi.py             # Configuração ASGI para servidores web modernos
```

## Arquivos Importantes na Raiz

- `manage.py`: Script principal para gerenciar o projeto Django
- `requirements.txt`: Lista de dependências do Python
- `.env`: Variáveis de ambiente (deve ser criado localmente, não versionado)
- `postgresql`: Banco de dados postgresql para desenvolvimento e produção

## Padrões e Convenções

O projeto segue alguns padrões e convenções importantes:

### Organização de Código

1. **Modularidade por Funcionalidade**: Cada app contém todas as funcionalidades relacionadas a um domínio específico
2. **Reutilização**: Componentes comuns são mantidos no app `core` ou em `templates/partials/`
3. **Responsabilidades Claras**: Cada arquivo tem uma responsabilidade específica (models, views, urls, etc.)

### Convenções de Nomenclatura

1. **URLs**: Geralmente usando nomes em português no formato `objeto_acao` (ex: `cliente_cadastro`, `venda_lista`)
2. **Templates**: Seguem o mesmo padrão das URLs, organizados por app
3. **Models**: Classes em CamelCase, nomes em inglês (convenção Django)
4. **Views**: Funções em snake_case, geralmente com nomes que refletem a URL correspondente

### Fluxo de Dados

1. **URL → View → Template**: O fluxo básico de uma requisição
2. **Middlewares**: Processam requisições antes de chegarem às views
3. **Context Processors**: Adicionam dados a todos os templates
4. **Decorators**: Controlam acesso às views específicas

## Como Navegar pelo Código

Para entender o sistema, recomendamos começar pelos seguintes arquivos:

1. `gerencial_saas/settings.py`: Para entender a configuração geral
2. `gerencial_saas/urls.py`: Para ver as rotas principais
3. `apps/dashboard/views.py`: Para entender os diferentes dashboards
4. `apps/usuarios/middleware.py`: Para compreender o controle de acesso
5. `templates/base.html`: Para ver a estrutura básica da UI

Continue para a próxima seção: [Arquitetura do Sistema](04-arquitetura.md) 