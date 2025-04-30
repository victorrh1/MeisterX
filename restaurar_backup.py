#!/usr/bin/env python
"""
Script para restaurar um backup do PostgreSQL
"""
import os
import sys
import glob
import subprocess
import django
from django.conf import settings

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gerencial_saas.settings')
django.setup()

def listar_backups():
    """Lista todos os backups disponíveis"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    if not os.path.exists(backup_dir):
        print("Pasta de backups não encontrada.")
        return []
    
    # Procurar arquivos de backup PostgreSQL
    pg_backups = glob.glob(os.path.join(backup_dir, "postgres_backup_*.sql"))
    # Procurar arquivos de backup JSON
    json_backups = glob.glob(os.path.join(backup_dir, "dados_backup_*.json"))
    
    all_backups = pg_backups + json_backups
    all_backups.sort(reverse=True)  # Ordenar por data (mais recente primeiro)
    
    return all_backups

def mostrar_backups():
    """Mostra uma lista numerada de backups"""
    backups = listar_backups()
    
    if not backups:
        print("Nenhum backup encontrado.")
        return None
    
    print("\nBackups disponíveis:")
    print("--------------------")
    
    for i, backup in enumerate(backups, 1):
        filename = os.path.basename(backup)
        timestamp = filename.split('_')[2].split('.')[0]
        tipo = "PostgreSQL" if "postgres" in filename else "Dados JSON"
        tamanho = os.path.getsize(backup) / (1024*1024)
        
        print(f"{i}. [{tipo}] {filename} ({tamanho:.2f} MB)")
    
    return backups

def restaurar_postgres(backup_path):
    """Restaura um backup PostgreSQL"""
    if not os.path.exists(backup_path):
        print(f"Arquivo de backup não encontrado: {backup_path}")
        return False
    
    # Obter configurações do banco de dados
    db_settings = settings.DATABASES['default']
    dbname = db_settings['NAME']
    user = db_settings['USER']
    password = db_settings['PASSWORD']
    host = db_settings['HOST']
    port = db_settings['PORT']
    
    # Configurar variável de ambiente para a senha
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    # Verificar se o banco existe
    try:
        check_cmd = [
            'psql',
            f'--host={host}',
            f'--port={port}',
            f'--username={user}',
            '--dbname=postgres',
            '-c', f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'"
        ]
        
        result = subprocess.run(check_cmd, env=env, capture_output=True, text=True)
        if '1 row' not in result.stdout:
            # Banco não existe, vamos criar
            create_cmd = [
                'createdb',
                f'--host={host}',
                f'--port={port}',
                f'--username={user}',
                dbname
            ]
            subprocess.run(create_cmd, env=env, check=True)
            print(f"Banco de dados '{dbname}' criado.")
    except Exception as e:
        print(f"Erro ao verificar/criar banco de dados: {e}")
        return False
    
    # Restaurar o backup
    try:
        print(f"Restaurando backup para o banco '{dbname}'...")
        
        # Primeiro, limpa o banco (drop e recria)
        drop_cmd = [
            'psql',
            f'--host={host}',
            f'--port={port}',
            f'--username={user}',
            '--dbname=postgres',
            '-c', f"DROP DATABASE IF EXISTS {dbname}"
        ]
        
        create_cmd = [
            'psql',
            f'--host={host}',
            f'--port={port}',
            f'--username={user}',
            '--dbname=postgres',
            '-c', f"CREATE DATABASE {dbname}"
        ]
        
        print("Recriando banco de dados...")
        subprocess.run(drop_cmd, env=env, check=True)
        subprocess.run(create_cmd, env=env, check=True)
        
        # Agora restaura com pg_restore
        restore_cmd = [
            'pg_restore',
            f'--host={host}',
            f'--port={port}',
            f'--username={user}',
            '--no-owner',
            '--no-privileges',
            '--dbname=' + dbname,
            backup_path
        ]
        
        print("Executando restauração...")
        result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
        
        # Alguns erros são esperados, então não usamos check=True
        print(f"Restauração concluída. {result.returncode}")
        
        return True
    except Exception as e:
        print(f"Erro durante a restauração: {e}")
        return False

def restaurar_dados_json(backup_path):
    """Restaura um backup de dados JSON"""
    if not os.path.exists(backup_path):
        print(f"Arquivo de backup não encontrado: {backup_path}")
        return False
    
    try:
        print("Carregando dados do backup JSON...")
        
        # Usar loaddata para carregar os dados
        from django.core.management import call_command
        call_command('loaddata', backup_path)
        
        print("Dados restaurados com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao restaurar dados JSON: {e}")
        return False

def main():
    """Função principal"""
    print("=== Restauração de Backup ===")
    
    backups = mostrar_backups()
    if not backups:
        return
    
    try:
        escolha = int(input("\nSelecione o número do backup a restaurar (0 para cancelar): "))
        
        if escolha == 0:
            print("Operação cancelada pelo usuário.")
            return
        
        if escolha < 1 or escolha > len(backups):
            print("Número inválido.")
            return
        
        backup_path = backups[escolha - 1]
        filename = os.path.basename(backup_path)
        
        print(f"\nVocê selecionou: {filename}")
        confirmacao = input("ATENÇÃO: A restauração irá substituir todos os dados atuais. Continuar? (s/n): ")
        
        if confirmacao.lower() != 's':
            print("Operação cancelada pelo usuário.")
            return
        
        if "postgres_backup" in filename:
            sucesso = restaurar_postgres(backup_path)
        elif "dados_backup" in filename:
            sucesso = restaurar_dados_json(backup_path)
        else:
            print("Tipo de backup não reconhecido.")
            return
        
        if sucesso:
            print("\nRestauração concluída com sucesso!")
            print("\nImportante:")
            print("1. Verifique se todos os dados foram restaurados corretamente.")
            print("2. Reinicie o servidor Django para aplicar todas as mudanças.")
        else:
            print("\nRestauração falhou. Verifique os erros acima.")
    
    except ValueError:
        print("Entrada inválida. Por favor, insira um número.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main() 