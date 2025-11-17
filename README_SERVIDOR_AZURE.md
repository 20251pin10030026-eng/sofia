# 🌸 Sofia - Servidor Azure VM

## Informações do Servidor

**IP Público:** `52.226.167.30`  
**Porta:** `5000`  
**URL API:** http://52.226.167.30:5000  
**URL Web:** http://52.226.167.30:5000/web  

**Usuário SSH:** `sofiaadmin`  
**Resource Group:** `sofia-rg`  
**VM Name:** `sofia-vm`  
**Location:** `eastus`  

## Custo

- **Mensal 24/7:** USD 8.09/mês
- **Desligada:** USD 0.50/mês (apenas disco)

## Comandos Úteis

### Conectar via SSH
```bash
ssh sofiaadmin@52.226.167.30
```

### Ver Logs em Tempo Real
```bash
ssh sofiaadmin@52.226.167.30 'sudo journalctl -u sofia -f'
```

### Gerenciar VM

**Parar VM (economizar):**
```powershell
az vm deallocate --resource-group sofia-rg --name sofia-vm
```

**Iniciar VM:**
```powershell
az vm start --resource-group sofia-rg --name sofia-vm
```

**Reiniciar Sofia:**
```bash
ssh sofiaadmin@52.226.167.30 'sudo systemctl restart sofia'
```

**Status do Serviço:**
```bash
ssh sofiaadmin@52.226.167.30 'sudo systemctl status sofia'
```

### Testar Servidor Localmente

```powershell
powershell -ExecutionPolicy Bypass -File testar_servidor_vm.ps1
```

### Deletar VM (CUIDADO!)
```powershell
az vm delete --resource-group sofia-rg --name sofia-vm --yes
```

## Configuração Local

O arquivo `.env` local está configurado para usar o servidor remoto:

```properties
SOFIA_SERVER_URL=http://52.226.167.30:5000
USE_REMOTE_SERVER=true
```

## Arquitetura

```
┌─────────────────┐
│   Seu PC Local  │
│                 │
│  Sofia Cliente  │
└────────┬────────┘
         │
         │ HTTP
         │
         ▼
┌─────────────────┐
│   Azure VM      │
│  52.226.167.30  │
│                 │
│  Sofia Server   │◄─────┐
│  (Flask API)    │      │
│                 │      │
│  Port: 5000     │      │
└────────┬────────┘      │
         │               │
         │               │
         ▼               │
┌─────────────────┐      │
│  GitHub Models  │      │
│    GPT-4o       │──────┘
│  (API Gratuita) │
└─────────────────┘
```

## Troubleshooting

### Servidor não responde
```bash
# Ver logs
ssh sofiaadmin@52.226.167.30 'sudo journalctl -u sofia -n 50'

# Reiniciar serviço
ssh sofiaadmin@52.226.167.30 'sudo systemctl restart sofia'
```

### Reconfigurar completamente
```powershell
$azPath = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
$script = Get-Content configurar_sofia_vm.sh -Raw
& $azPath vm run-command invoke --resource-group sofia-rg --name sofia-vm --command-id RunShellScript --scripts $script
```

### IP mudou após desligar
```powershell
# Obter novo IP
az vm show --resource-group sofia-rg --name sofia-vm --show-details --query publicIps --output tsv

# Atualizar .env local com novo IP
```

## Segurança

🔒 **Token GitHub está configurado diretamente na VM**  
⚠️ **Não comitar o token no Git**  
✅ **Porta 5000 aberta apenas para HTTP**  
🔐 **SSH protegido por senha (12+ caracteres)**  

## Monitoramento

**Ver uso de recursos:**
```bash
ssh sofiaadmin@52.226.167.30 'htop'
```

**Ver uso de disco:**
```bash
ssh sofiaadmin@52.226.167.30 'df -h'
```

**Ver processos Sofia:**
```bash
ssh sofiaadmin@52.226.167.30 'ps aux | grep sofia'
```

## Backup

**Fazer backup do código:**
```bash
ssh sofiaadmin@52.226.167.30 'cd sofia && git pull'
```

**Backup da memória (se houver):**
```bash
ssh sofiaadmin@52.226.167.30 'tar -czf sofia-backup.tar.gz sofia/sofia/.sofia_internal'
scp sofiaadmin@52.226.167.30:~/sofia-backup.tar.gz ./
```
