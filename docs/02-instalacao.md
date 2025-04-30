# Instalação e Configuração

Este guia descreve como instalar e configurar o Gerencial SaaS em um ambiente Windows 11 Pro, tanto para desenvolvimento quanto para produção.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.10+ (recomendado 3.13.2)
- Git
- Visual Studio Code (ou outro editor de sua preferência)
- Conexão com a internet para baixar dependências

## Instalação para Desenvolvimento

### 1. Clonar o Repositório

```bash
# Abra o PowerShell como administrador e execute:
cd C:\Projetos  # ou outro diretório de sua preferência
git clone https://github.com/seu-usuario/gerencial_saas.git
cd gerencial_saas
```

### 2. Criar e Ativar Ambiente Virtual

```bash
# No diretório do projeto
python -m venv venv
.\venv\Scripts\Activate.ps1  # Para PowerShell
# ou
.\venv\Scripts\activate.bat  # Para Prompt de Comando
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=seu-servidor-smtp
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@dominio.com
EMAIL_HOST_PASSWORD=sua-senha-email
```

### 5. Aplicar Migrações do Banco de Dados

```bash
python manage.py migrate
```

### 6. Carregar Dados Iniciais (Fixtures)

```bash
python manage.py loaddata apps/vendas/fixtures/initial_data.json
# Carregar outras fixtures conforme necessário
```

### 7. Criar Superusuário Administrativo

```bash
python manage.py createsuperuser
```

### 8. Iniciar o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Após estes passos, o sistema estará disponível em `http://127.0.0.1:8000/`.

## Configuração de Produção

Para ambientes de produção, são necessárias algumas configurações adicionais para garantir segurança e desempenho.

### 1. Configurações de Segurança

Edite o arquivo `gerencial_saas/settings.py` e atualize:

```python
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']
```

### 2. Configuração do Banco de Dados PostgreSQL

Instale o PostgreSQL e atualize o arquivo `.env`:

```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/gerencial_saas
```

### 3. Configuração de Arquivos Estáticos

```bash
python manage.py collectstatic
```

### 4. Configuração do Servidor Web (IIS no Windows)

#### Instalar módulos necessários:

```bash
pip install wfastcgi
wfastcgi-enable
```

#### Configuração no IIS:

1. Instale o IIS com CGI
2. Crie um novo site no IIS apontando para o diretório do projeto
3. Configure o manipulador FastCGI
4. Configure o arquivo web.config

Exemplo de `web.config`:

```xml
<configuration>
  <system.webServer>
    <handlers>
      <add name="Python FastCGI" 
           path="*" 
           verb="*" 
           modules="FastCgiModule" 
           scriptProcessor="C:\Projetos\gerencial_saas\venv\Scripts\python.exe|C:\Projetos\gerencial_saas\venv\Lib\site-packages\wfastcgi.py" 
           resourceType="Unspecified" 
           requireAccess="Script" />
    </handlers>
    <fastCgi>
      <application fullPath="C:\Projetos\gerencial_saas\venv\Scripts\python.exe" arguments="C:\Projetos\gerencial_saas\venv\Lib\site-packages\wfastcgi.py" />
    </fastCgi>
  </system.webServer>
  
  <appSettings>
    <add key="WSGI_HANDLER" value="django.core.wsgi.get_wsgi_application()" />
    <add key="PYTHONPATH" value="C:\Projetos\gerencial_saas" />
    <add key="DJANGO_SETTINGS_MODULE" value="gerencial_saas.settings" />
  </appSettings>
</configuration>
```

## Solução de Problemas Comuns

### Erro ao Migrar Banco de Dados

Se encontrar erros durante as migrações:

```bash
# Verificar migrações pendentes
python manage.py showmigrations

# Resolver problemas específicos de uma app
python manage.py migrate app_name zero  # Reset a app
python manage.py migrate app_name  # Aplicar migrações novamente
```

### Erro "no such table"

Se encontrar erro indicando que uma tabela não existe:

```bash
# Verificar integridade do banco de dados
python manage.py dbshell
.tables  # No SQLite

# Recriar fixtures para a tabela específica
python manage.py dumpdata app_name.model_name --indent 2 > fixture_name.json
```

### Problemas com Permissões

```bash
# Verificar permissões do usuário
python manage.py shell
from django.contrib.auth.models import Group
print(Group.objects.all())

# Adicionar um usuário ao grupo Admin
python manage.py shell
from django.contrib.auth.models import Group, User
user = User.objects.get(username='seu_usuario')
admin_group = Group.objects.get(name='Admin')
user.groups.add(admin_group)
user.save()
```

## Atualização do Sistema

Para atualizar o sistema para uma nova versão:

```bash
# Atualizar código-fonte
git pull

# Atualizar dependências
pip install -r requirements.txt

# Aplicar novas migrações
python manage.py migrate

# Coletar arquivos estáticos (em produção)
python manage.py collectstatic --noinput

# Reiniciar o servidor
```

Continue para a próxima seção: [Estrutura do Projeto](03-estrutura.md) 