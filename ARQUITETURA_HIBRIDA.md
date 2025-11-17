# Arquitetura Híbrida Sofia - PC Local + Azure VM

## 📊 Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERNET (Usuários)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/80
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             AZURE VM (52.226.167.30)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  NGINX (Servidor Web Estático)                        │  │
│  │  - Serve HTML/CSS/JS                                  │  │
│  │  - 1 vCPU, 1 GB RAM                                   │  │
│  │  - Custo: USD 8.09/mês                                │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS (ngrok)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    NGROK TUNNEL                             │
│  - https://abc123.ngrok.io → localhost:5000                 │
│  - Certificado SSL automático                               │
│  - Grátis (ou USD 8/mês para domínio fixo)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/5000
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             SEU PC (Processamento Principal)                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  SOFIA API (Flask)                                    │  │
│  │  - Python 3.11                                        │  │
│  │  - GitHub Models (GPT-4o)                             │  │
│  │  - Hardware mais potente                              │  │
│  │  - Grátis (seu PC + Copilot Pro)                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Vantagens

### ✅ Custos Otimizados
- **VM Azure**: USD 8.09/mês (apenas nginx, muito leve)
- **ngrok grátis**: Suficiente para uso pessoal
- **GitHub Models**: Grátis com Copilot Pro
- **Total**: ~USD 8/mês (vs USD 50+/mês com VM potente)

### ✅ Performance Superior
- **Processamento**: Seu PC (mais potente que VM 1GB)
- **Latência**: API local (sem latência Azure ↔ GitHub Models)
- **Escalabilidade**: Upgrade no PC quando quiser

### ✅ Facilidade de Desenvolvimento
- **Debug local**: Logs, breakpoints, IDE completo
- **Testes rápidos**: Sem deploy, mudanças instantâneas
- **Sem limite de requisições**: Seu PC, suas regras

### ✅ Segurança
- **HTTPS**: ngrok fornece certificado SSL
- **Token seguro**: GitHub token no .env local
- **Firewall**: Controle total no seu PC

## 📋 Componentes

### 1. Azure VM (Servidor Web)
**Função**: Servir arquivos estáticos (HTML, CSS, JS, imagens)

**Configuração**:
- OS: Ubuntu 22.04
- CPU: 1 vCPU
- RAM: 1 GB
- Software: nginx
- Porta: 80 (HTTP)

**Custo**: USD 8.09/mês (24/7)

### 2. Seu PC (Processamento)
**Função**: Executar Sofia e processar requisições

**Configuração**:
- Python 3.11+
- Sofia API (Flask)
- GitHub Models (GPT-4o)
- Virtual environment (.venv)

**Custo**: Grátis (seu PC)

### 3. ngrok (Túnel)
**Função**: Conectar VM (pública) ao PC (privado)

**Configuração**:
- Túnel HTTPS
- URL pública: https://xxx.ngrok.io
- Porta local: 5000

**Custo**: Grátis (plano básico)

## 🚀 Setup Completo

### Passo 1: Simplificar VM

```powershell
# Execute uma vez
powershell -ExecutionPolicy Bypass -File simplificar_vm_para_web.ps1
```

Isso vai:
- Remover Sofia da VM
- Instalar nginx
- Configurar para servir arquivos estáticos
- Abrir porta 80

### Passo 2: Configurar Sofia Local

```powershell
# Execute uma vez
powershell -ExecutionPolicy Bypass -File configurar_sofia_local.ps1
```

Isso vai:
- Ativar virtual environment
- Instalar dependências
- Configurar .env com GitHub Models
- Testar importações

### Passo 3: Instalar ngrok

```powershell
# Baixar e instalar
# https://ngrok.com/download

# Criar conta e pegar token
# https://dashboard.ngrok.com/signup

# Configurar
ngrok config add-authtoken SEU_TOKEN_AQUI
```

### Passo 4: Iniciar Sofia

**Terminal 1 (Sofia)**:
```powershell
cd D:\A.I_GitHUB
& .venv/Scripts/Activate.ps1
cd sofia
python sofia/api.py
```

**Terminal 2 (ngrok)**:
```powershell
ngrok http 5000
```

Copie a URL: `https://abc123.ngrok.io`

### Passo 5: Atualizar Site

Edite `sofia/web/script.js`:
```javascript
const API_URL = 'https://abc123.ngrok.io';  // Sua URL do ngrok
```

### Passo 6: Enviar Site para VM

```powershell
scp -r sofia/web/* sofiaadmin@52.226.167.30:/var/www/sofia/
```

### Passo 7: Testar

Acesse: http://52.226.167.30

## 📊 Comparação de Custos

### Arquitetura Anterior (Tudo na VM)
```
VM Azure (4 vCPU, 8 GB RAM)      USD 120/mês
Storage                          USD 5/mês
────────────────────────────────────────────
TOTAL                            USD 125/mês
```

### Arquitetura Atual (Híbrida)
```
VM Azure (1 vCPU, 1 GB RAM)      USD 8.09/mês
ngrok (plano grátis)             USD 0/mês
Seu PC (já tem)                  USD 0/mês
GitHub Models (Copilot Pro)      USD 0/mês (já incluído)
────────────────────────────────────────────
TOTAL                            USD 8.09/mês
```

**Economia: USD 116.91/mês (93%)**

## 🔧 Manutenção

### Iniciar Sofia Diariamente

Crie atalho ou script:
```powershell
# iniciar_sofia.ps1
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd D:\A.I_GitHUB; & .venv/Scripts/Activate.ps1; cd sofia; python sofia/api.py
"@

Start-Sleep -Seconds 5

Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 5000"

Write-Host "Sofia e ngrok iniciados!" -ForegroundColor Green
```

### Atualizar Site

```powershell
# Fazer mudanças em sofia/web/
# Enviar para VM
scp -r sofia/web/* sofiaadmin@52.226.167.30:/var/www/sofia/
```

### Atualizar Sofia (código)

Não precisa fazer nada! Mudanças são instantâneas (está rodando local).

### Monitorar

- **Sofia logs**: Veja no terminal
- **ngrok dashboard**: http://127.0.0.1:4040
- **nginx logs**: `ssh sofiaadmin@52.226.167.30 "sudo tail -f /var/log/nginx/sofia_access.log"`

## 🌐 Melhorias Futuras

### Domínio Personalizado

#### Opção 1: ngrok pago (USD 8/mês)
```powershell
ngrok http 5000 --domain=sofia.seu-dominio.com
```

#### Opção 2: Cloudflare Tunnel (grátis)
```powershell
cloudflared tunnel --url http://localhost:5000
```

### Backup Automático

```powershell
# Script de backup
$date = Get-Date -Format "yyyy-MM-dd"
Compress-Archive -Path "D:\A.I_GitHUB\sofia" -DestinationPath "D:\Backups\sofia-$date.zip"
```

### Auto-start com Windows

Tarefa agendada:
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File D:\A.I_GitHUB\iniciar_sofia.ps1"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "SofiaAutoStart" -Action $action -Trigger $trigger
```

## 🛠️ Troubleshooting

### Sofia não conecta ao GitHub Models

Verifique `.env`:
```powershell
cat sofia/.env
```

Deve conter:
```
SOFIA_USE_CLOUD=true
GITHUB_TOKEN=ghp_REDACTED
GITHUB_MODEL=gpt-4o
```

### ngrok não inicia

Verifique authtoken:
```powershell
ngrok config check
```

### Site não carrega na VM

Verifique nginx:
```bash
ssh sofiaadmin@52.226.167.30
sudo systemctl status nginx
sudo nginx -t
```

### Porta 5000 em uso

```powershell
# Ver qual processo está usando
netstat -ano | findstr :5000

# Matar processo
Stop-Process -Id PID_AQUI
```

## 📚 Arquivos de Referência

- `simplificar_vm_para_web.ps1` - Configurar VM como servidor web
- `configurar_sofia_local.ps1` - Configurar Sofia no PC
- `GUIA_NGROK.md` - Tutorial completo do ngrok
- `STATUS_AZURE.md` - Status da infraestrutura

## 🎓 Conclusão

Esta arquitetura híbrida oferece:

1. **Melhor custo-benefício**: USD 8/mês vs USD 125/mês
2. **Melhor performance**: Seu PC é mais potente
3. **Facilidade de desenvolvimento**: Tudo local, debug fácil
4. **Escalabilidade**: Upgrade no PC quando quiser
5. **Segurança**: HTTPS, tokens locais, controle total

**Resultado**: Sofia potente rodando no seu PC, site servido pela VM Azure, conexão segura via ngrok. O melhor dos dois mundos! 🚀
