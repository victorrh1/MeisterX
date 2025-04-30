# Gerencial SaaS - Documentação

## Sobre o Projeto

O Gerencial SaaS é uma plataforma de gestão completa para empresas, oferecendo recursos de controle de vendas, produtos, clientes e usuários. O sistema foi desenvolvido usando Django como framework principal e segue uma arquitetura modular que facilita a manutenção e expansão.

## Índice da Documentação

1. [Introdução e Visão Geral](01-introducao.md)
2. [Instalação e Configuração](02-instalacao.md)
3. [Estrutura do Projeto](03-estrutura.md)
4. [Arquitetura do Sistema](04-arquitetura.md)
5. [Módulos do Sistema](modulos/README.md)
   - [Core](modulos/01-core.md)
   - [Usuários](modulos/02-usuarios.md)
   - [Dashboard](modulos/03-dashboard.md)
   - [Clientes](modulos/04-clientes.md)
   - [Produtos](modulos/05-produtos.md)
   - [Vendas](modulos/06-vendas.md)
6. [Banco de Dados](05-banco-dados.md)
7. [Templates e Interface](06-templates.md)
8. [Permissões e Segurança](07-permissoes.md)
9. [Middlewares](08-middlewares.md)
10. [Fluxos de Navegação](09-fluxos.md)
11. [Manutenção e Troubleshooting](10-manutencao.md)

## Visão Geral do Sistema

O Gerencial SaaS é um sistema de gestão empresarial com as seguintes características principais:

- **Multi-tenant**: Suporta múltiplas empresas utilizando a mesma instância do sistema
- **Controle de Acesso Baseado em Grupos**: Três níveis principais de acesso (Admin, Equipe, Cliente)
- **Módulos Independentes**: Cada funcionalidade está organizada em apps Django separados
- **Interface Responsiva**: Design moderno e adaptável usando Bootstrap e componentes personalizados
- **Dashboard Personalizado**: Cada tipo de usuário tem uma visão personalizada conforme suas permissões

### Principais Funcionalidades

- Gestão de usuários e controle de acesso
- Cadastro e gestão de clientes
- Cadastro e gestão de produtos
- Controle completo de vendas
- Dashboard com estatísticas e indicadores
- Sistema de notificações integrado

## Como Usar Esta Documentação

Esta documentação está organizada em arquivos Markdown separados para facilitar a navegação. Recomendamos começar pela [Introdução e Visão Geral](01-introducao.md) e seguir a ordem sugerida no índice para uma compreensão completa do sistema.

Para desenvolvedores iniciantes, sugerimos focar inicialmente nos módulos específicos que irão trabalhar, enquanto desenvolvedores experientes podem se beneficiar da visão da arquitetura geral e fluxos do sistema.

## Convenções

Em toda a documentação, utilizamos as seguintes convenções:

- `código em linha` para nomes de arquivos, classes, métodos ou comandos
- **Negrito** para termos importantes
- *Itálico* para ênfase
- > Blocos de citação para notas importantes ou avisos

## Licença

Este projeto é proprietário e seu uso, modificação ou distribuição está sujeito aos termos acordados com o proprietário do sistema. 