# Fluxo: Upload NFC-e

## Via QR Code

1. O usuário escaneia o QR Code 
2. O sistema extrair o HTML da pagina e salva no armazenamento
2.1. Faz upload para o armazenamento
2.2. Registra no banco de dados

## Trigger no armazenamento

1. Um novo arquivo é adicionado ao armazenamento
2. O sistema transforma o html em um JSON estruturado
3. O sistema registra o JSON no banco de dados


# Regras
Arquivo só deve ser acessado pelo usuário que o enviou
