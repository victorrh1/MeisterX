# Migração para PostgreSQL - Gerencial SaaS

Este documento contém informações sobre a migração do SQLite para o PostgreSQL e como usar as ferramentas de backup e restauração.

## Migração do SQLite para PostgreSQL

A migração do banco de dados SQLite para PostgreSQL já foi realizada com sucesso. Todas as tabelas e dados foram transferidos para o PostgreSQL.

### Pré-requisitos

- PostgreSQL instalado e configurado (versão 12 ou superior)
- Cliente PostgreSQL (psql, pg_dump, pg_restore)
- Python 3.8+
- Pacote `psycopg2-binary` (driver PostgreSQL para Python)

## Ferramentas de Backup e Restauração

O projeto inclui scripts para gerenciar backups e restaurações do banco de dados:

### 1. backup_postgres.py

Script para criar backups do PostgreSQL e remover o arquivo SQLite com segurança.

```bash
# Backup completo com interação do usuário
python backup_postgres.py

# Backup automático (sem interação)
python backup_postgres.py --auto

# Backup sem remover o SQLite
python backup_postgres.py --no-remove-sqlite
```

O script realiza as seguintes operações:
- Cria uma pasta `backups/` se não existir
- Faz backup do banco PostgreSQL usando pg_dump
- Exporta os dados em formato JSON usando o comando dumpdata do Django
- Opcionalmente faz backup e remove o arquivo SQLite (se ainda existir)

### 2. backup_postgres_agendado.bat

Script batch para Windows que pode ser usado com o Agendador de Tarefas para backups automáticos.

Para configurar:
1. Abra o Agendador de Tarefas do Windows
2. Crie uma nova tarefa
3. Configure para executar o script `backup_postgres_agendado.bat`
4. Defina a frequência (diária, semanal, etc.)

### 3. restaurar_backup.py

Script para restaurar um backup existente.

```bash
python restaurar_backup.py
```

O script mostrará uma lista de backups disponíveis e permitirá escolher qual restaurar.

## Verificações e Manutenção

### Verificar Migrações Pendentes

Para verificar se existem migrações pendentes:

```bash
python manage.py showmigrations
```

### Aplicar Migrações Pendentes

Se houver migrações pendentes, aplique-as com:

```bash
python manage.py migrate
```

### Monitoramento de Tamanho do Banco

Para monitorar o tamanho do banco PostgreSQL:

```bash
psql -U postgres -d postgres -c "SELECT pg_size_pretty(pg_database_size('gerencial_saas')) AS tamanho;"
```

## Solução de Problemas

### Erro de Conexão com PostgreSQL

Se você encontrar erros de conexão:

1. Verifique se o serviço PostgreSQL está em execução
2. Confirme que as credenciais em `settings.py` estão corretas
3. Verifique se consegue se conectar com o comando:
   ```
   psql -U postgres -h localhost -p 5432
   ```

### Restauração Falha

Se a restauração falhar:

1. Verifique se o arquivo de backup está íntegro
2. Tente restaurar manualmente com:
   ```
   pg_restore -U postgres -d gerencial_saas -h localhost backup_file.sql
   ```

## Boas Práticas

1. **Backups regulares**: Configure backups automáticos diários ou semanais
2. **Armazenamento externo**: Copie periodicamente os backups para um dispositivo ou serviço externo
3. **Teste de restauração**: Teste a restauração de backups regularmente
4. **Documentação**: Mantenha este documento atualizado conforme as necessidades do projeto evoluem 