# Configuração de Notificações de Backup via WhatsApp

Este guia explica como configurar o sistema para enviar notificações automáticas pelo WhatsApp quando um backup for concluído.

## Requisitos

1. Conta no Twilio (https://www.twilio.com/)
2. Um número de WhatsApp verificado para receber as mensagens
3. Biblioteca Twilio instalada no sistema (`pip install twilio`)

## Passos para Configuração

### 1. Criar uma conta no Twilio

- Acesse [Twilio.com](https://www.twilio.com/) e crie uma conta gratuita
- Após criar a conta, você terá acesso a um período de avaliação que permite enviar mensagens de teste

### 2. Configurar o Sandbox do WhatsApp do Twilio

- No painel do Twilio, navegue até "Messaging" > "Try it out" > "Send a WhatsApp message"
- Siga as instruções para conectar seu WhatsApp ao sandbox do Twilio
  - Você precisará enviar uma mensagem com um código para o número do Twilio
  - Este processo associa seu número de WhatsApp à conta do Twilio

### 3. Obter as credenciais da API

No painel do Twilio, anote:
- Account SID
- Auth Token 
- O número do WhatsApp do Twilio (formato: +14155238886)

### 4. Configurar o script de backup

Edite o arquivo `backup_postgres.py` e altere as seguintes linhas:

```python
# Configuração do Twilio para WhatsApp
TWILIO_ENABLED = True  # Altere de False para True
TWILIO_ACCOUNT_SID = "sua_account_sid"  # Cole o Account SID aqui
TWILIO_AUTH_TOKEN = "seu_auth_token"  # Cole o Auth Token aqui
TWILIO_FROM_WHATSAPP = "whatsapp:+14155238886"  # Verifique se este é o número fornecido pelo Twilio
TWILIO_TO_WHATSAPP = "whatsapp:+5511999999999"  # Substitua pelo seu número de WhatsApp (com código do país)
```

### 5. Teste a configuração

Execute o seguinte comando para testar se a notificação está funcionando:

```
python backup_postgres.py --no-remove-sqlite --whatsapp
```

Se tudo estiver configurado corretamente, você receberá uma mensagem no WhatsApp informando sobre o backup.

### 6. Ativar notificações para backups agendados

O arquivo `backup_postgres_agendado.bat` já está configurado para enviar notificações via WhatsApp. Você não precisa fazer alterações adicionais nele.

## Notas importantes

1. O número do Twilio pode mudar, verifique sempre no painel do Twilio
2. Enquanto estiver no modo Sandbox do Twilio, você precisará renovar seu acesso a cada 72 horas
3. Para uso em produção, considere obter um plano pago do Twilio para evitar restrições
4. O Twilio cobra por mensagem enviada, verifique a tabela de preços atual
5. Você pode personalizar o formato da mensagem no arquivo `backup_postgres.py`

## Resolução de problemas

Se você encontrar erros ao enviar mensagens:

1. Verifique se o TWILIO_ENABLED está definido como True
2. Confirme se suas credenciais estão corretas
3. Certifique-se que seu número de WhatsApp está devidamente conectado ao Sandbox
4. Verifique se a biblioteca Twilio está instalada (`pip install twilio`)
5. Consulte os logs em caso de erros específicos

Para mais informações, consulte a [documentação do Twilio para WhatsApp](https://www.twilio.com/docs/whatsapp/api). 