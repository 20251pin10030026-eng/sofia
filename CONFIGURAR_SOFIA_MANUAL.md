# Configuração Manual da Sofia na VM Azure

A configuração automática via Azure CLI está apresentando problemas. Siga os passos abaixo para configurar manualmente via SSH.

## 1. Conectar via SSH

```bash
ssh sofiaadmin@52.226.167.30
```

Digite a senha quando solicitado (a senha que você criou ao executar o deploy).

## 2. Verificar se a Sofia está instalada

```bash
cd /home/sofiaadmin/sofia
ls -la
```

Você deve ver os diretórios: `sofia/`, `venv/`, etc.

## 3. Configurar Variáveis de Ambiente

Crie o arquivo `.env` dentro do diretório `sofia/`:

```bash
cd /home/sofiaadmin/sofia/sofia
cat > .env << 'EOF'
SOFIA_USE_CLOUD=true
GITHUB_TOKEN=ghp_REDACTED
GITHUB_MODEL=gpt-4o
EOF
```

## 4. Testar a Configuração

```bash
cd /home/sofiaadmin/sofia/sofia
export SOFIA_USE_CLOUD=true
export GITHUB_TOKEN=ghp_REDACTED
export GITHUB_MODEL=gpt-4o
../venv/bin/python -c "from cerebro import Cerebro; c = Cerebro(); print(c.gerar_resposta('Ola, voce funciona?', 'test'))"
```

Se retornar uma resposta (não um erro de Ollama), está funcionando!

## 5. Criar Serviço Systemd

```bash
sudo tee /etc/systemd/system/sofia.service << 'EOF'
[Unit]
Description=Sofia - Assistente Virtual
After=network.target

[Service]
Type=simple
User=sofiaadmin
WorkingDirectory=/home/sofiaadmin/sofia/sofia
Environment="SOFIA_USE_CLOUD=true"
Environment="GITHUB_TOKEN=ghp_REDACTED"
Environment="GITHUB_MODEL=gpt-4o"
ExecStart=/home/sofiaadmin/sofia/venv/bin/python api.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

## 6. Ativar e Iniciar o Serviço

```bash
sudo systemctl daemon-reload
sudo systemctl enable sofia
sudo systemctl start sofia
```

## 7. Verificar Status

```bash
sudo systemctl status sofia
```

Deve mostrar "Active: active (running)".

## 8. Ver Logs em Tempo Real

```bash
sudo journalctl -u sofia -f
```

Pressione `Ctrl+C` para sair.

## 9. Testar o Servidor

```bash
curl http://localhost:5000/
```

Deve retornar HTML.

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Ola Sofia, voce esta funcionando?","session_id":"test"}'
```

Deve retornar uma resposta JSON com a resposta da Sofia (usando GPT-4o).

## 10. Testar da Internet

De volta ao seu computador (PowerShell):

```powershell
Invoke-RestMethod -Uri "http://52.226.167.30:5000/chat" `
  -Method Post `
  -Body (@{message = "Ola Sofia"; session_id = "test"} | ConvertTo-Json) `
  -ContentType "application/json"
```

## Resolução de Problemas

### Se o serviço não iniciar:

```bash
sudo journalctl -u sofia -n 50
```

### Se ainda estiver usando Ollama:

Verifique se as variáveis de ambiente estão definidas:

```bash
sudo systemctl cat sofia
```

Deve mostrar as linhas `Environment=` com os valores corretos.

### Reiniciar o serviço:

```bash
sudo systemctl restart sofia
sudo systemctl status sofia
```

### Matar processos antigos:

```bash
sudo pkill -f "python.*api.py"
sudo systemctl start sofia
```

## Informações da VM

- **IP Público**: 52.226.167.30
- **Porta**: 5000
- **Usuário**: sofiaadmin
- **Localização**: eastus
- **Custo**: USD 8.09/mês

## Desligar a VM (para economizar)

Se quiser desligar a VM temporariamente:

```powershell
az vm deallocate --resource-group sofia-rg --name sofia-vm
```

Para ligar novamente:

```powershell
az vm start --resource-group sofia-rg --name sofia-vm
```

**NOTA**: O IP público pode mudar após desligar/ligar. Para obter o novo IP:

```powershell
az vm show -d --resource-group sofia-rg --name sofia-vm --query publicIps -o tsv
```
