# Guia: Expor Sofia com ngrok

## O que é ngrok?

ngrok cria um túnel seguro (HTTPS) que expõe seu servidor local para a internet. Perfeito para:
- Expor Sofia do seu PC para o site na VM Azure
- Não precisa abrir portas no roteador
- Certificado SSL automático (HTTPS)
- URLs amigáveis

## Instalação

### 1. Baixar ngrok

Acesse: https://ngrok.com/download

Ou instale via Chocolatey:
```powershell
choco install ngrok
```

### 2. Criar conta (grátis)

1. Acesse: https://dashboard.ngrok.com/signup
2. Crie conta (pode usar GitHub)
3. Pegue seu authtoken em: https://dashboard.ngrok.com/get-started/your-authtoken

### 3. Configurar authtoken

```powershell
ngrok config add-authtoken SEU_TOKEN_AQUI
```

Exemplo:
```powershell
ngrok config add-authtoken 2abc123XYZ_456def789GHI
```

## Uso Básico

### Iniciar Sofia

Terminal 1:
```powershell
cd D:\A.I_GitHUB
& .venv/Scripts/Activate.ps1
cd sofia
python sofia/api.py
```

Você verá:
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### Expor com ngrok

Terminal 2:
```powershell
ngrok http 5000
```

Você verá algo assim:
```
ngrok

Session Status                online
Account                       seu_email@email.com
Version                       3.x.x
Region                        United States (us)
Latency                       50ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Copie a URL**: `https://abc123.ngrok.io`

## Atualizar Site para Usar ngrok

Edite `sofia/web/script.js`:

```javascript
// ANTES:
const API_URL = 'http://localhost:5000';

// DEPOIS:
const API_URL = 'https://abc123.ngrok.io';  // Sua URL do ngrok
```

## Enviar Site para VM

```powershell
scp -r sofia/web/* sofiaadmin@52.226.167.30:/var/www/sofia/
```

## Testar

1. Acesse: http://52.226.167.30
2. Converse com Sofia
3. Sofia processará no seu PC (mais potente!)
4. Resposta volta via ngrok

## Monitoramento

ngrok oferece uma interface web local:
```
http://127.0.0.1:4040
```

Você pode ver:
- Todas as requisições
- Payloads (request/response)
- Tempo de resposta
- Replay de requisições

## Planos ngrok

### Grátis
- ✅ HTTPS automático
- ✅ 1 processo ngrok por vez
- ✅ URLs aleatórias (ex: abc123.ngrok.io)
- ⚠️ URL muda a cada reinício
- ⚠️ Limite de 40 conexões/minuto

### Paid (USD 8/mês)
- ✅ Domínio fixo (ex: sofia.ngrok.io)
- ✅ Múltiplos túneis simultâneos
- ✅ Sem limite de conexões
- ✅ IP whitelist

## Alternativa: Cloudflare Tunnel

Se preferir domínio fixo grátis:

```powershell
# Instalar
winget install --id Cloudflare.cloudflared

# Autenticar
cloudflared tunnel login

# Criar tunel
cloudflared tunnel create sofia

# Expor
cloudflared tunnel --url http://localhost:5000
```

Cloudflare oferece:
- Domínio fixo grátis (ex: sofia-abc.trycloudflare.com)
- Sem limite de conexões
- DDoS protection

## Script Automatizado

Crie `iniciar_sofia_com_tunel.ps1`:

```powershell
# Terminal 1: Sofia
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd D:\A.I_GitHUB
& .venv/Scripts/Activate.ps1
cd sofia
python sofia/api.py
"@

# Aguardar Sofia iniciar
Start-Sleep -Seconds 5

# Terminal 2: ngrok
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 5000"

Write-Host ""
Write-Host "Sofia e ngrok iniciados!" -ForegroundColor Green
Write-Host ""
Write-Host "1. Aguarde ngrok carregar (5 segundos)" -ForegroundColor Yellow
Write-Host "2. Copie a URL https://xxx.ngrok.io" -ForegroundColor Yellow
Write-Host "3. Atualize script.js com a URL" -ForegroundColor Yellow
Write-Host "4. Envie para VM: scp -r sofia/web/* sofiaadmin@52.226.167.30:/var/www/sofia/" -ForegroundColor Yellow
Write-Host ""
```

Execute:
```powershell
powershell -ExecutionPolicy Bypass -File iniciar_sofia_com_tunel.ps1
```

## Dicas

### Domínio Customizado (ngrok paid)

Se comprar plano ngrok:
```powershell
ngrok http 5000 --domain=sofia.ngrok.io
```

### Executar como Serviço Windows

Crie tarefa agendada para iniciar automaticamente:
```powershell
$action = New-ScheduledTaskAction -Execute "ngrok.exe" -Argument "http 5000"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "SofiaNgrok" -Action $action -Trigger $trigger -User $env:USERNAME
```

### Ver Logs ngrok

```powershell
Get-Content "$env:USERPROFILE\.ngrok2\ngrok.log" -Tail 50 -Wait
```

## Troubleshooting

### Erro: "tunnel not found"
```powershell
ngrok config add-authtoken SEU_TOKEN
```

### Erro: "failed to start tunnel"
Verifique se porta 5000 está livre:
```powershell
netstat -ano | findstr :5000
```

### Erro: "account limit reached"
Plano grátis permite 1 túnel. Feche outros ngrok:
```powershell
Get-Process ngrok | Stop-Process
```

### URL muito longa
Use encurtador ou compre plano para domínio fixo.

## Resumo

```powershell
# 1. Instalar
choco install ngrok
ngrok config add-authtoken SEU_TOKEN

# 2. Iniciar Sofia
cd sofia; python sofia/api.py

# 3. Expor (outro terminal)
ngrok http 5000

# 4. Atualizar site
# script.js: API_URL = 'https://sua-url.ngrok.io'

# 5. Enviar para VM
scp -r sofia/web/* sofiaadmin@52.226.167.30:/var/www/sofia/

# 6. Testar
# http://52.226.167.30
```

**Pronto!** Seu PC processa (potente), VM serve (leve), ngrok conecta (seguro).
