@echo off
REM Script de backup automático para PostgreSQL 
REM Para ser usado com o Agendador de Tarefas do Windows

cd /d "%~dp0"
echo Iniciando backup do PostgreSQL às %date% %time%
echo ------------------------------------------------

REM Ativar o ambiente virtual (ajuste o caminho se necessário)
call venv\Scripts\activate.bat

REM Executar o script de backup com notificação WhatsApp
python backup_postgres.py --auto --whatsapp

echo ------------------------------------------------
echo Backup concluído às %date% %time%
echo Log salvo em backups\backup_log_%date:~-4,4%%date:~-7,2%%date:~-10,2%.txt

REM Pausar somente se for executado manualmente
if not defined SCHEDULED_TASK pause 