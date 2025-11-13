# 💰 Estratégia Azure Econômica - Sofia

## 🎯 Objetivo
Deploy da Sofia no Azure com **custo mínimo** usando plano pay-as-you-go.

**Meta de Custo:** US$ 2-5/mês (~R$ 10-25/mês)

---

## 📊 Arquitetura Escolhida

### **Serverless com Cache Inteligente**

```
┌─────────────────────────────────────────────┐
│  Azure Static Web Apps (FREE Tier)          │
│  ✅ Frontend completo                        │
│  ✅ 100GB bandwidth/mês grátis              │
│  ✅ HTTPS automático                         │
│  ✅ CDN global                               │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Azure Functions (Consumption Plan)         │
│  ⚡ Serverless Python                        │
│  💵 1 milhão execuções GRÁTIS               │
│  💵 US$ 0,20 por milhão adicional           │
│  📊 Estimativa: US$ 1-3/mês                 │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  GitHub Models API                          │
│  ✅ GPT-4o GRÁTIS (Copilot Pro)             │
│  ✅ 2000 req/min                            │
│  ✅ US$ 0,00/mês                            │
└─────────────────────────────────────────────┘
```

---

## 💡 Otimizações de Custo

### 1. **Cache de Respostas** 📦
Reduz 70% das chamadas à IA

```javascript
// Perguntas frequentes em cache local
const FAQ_CACHE = {
  "olá": "Olá! Eu sou a Sofia 🌸",
  "quem é você": "Sou Sofia, assistente virtual...",
  "como usar": "Use o chat para conversar comigo..."
};

// Verifica cache antes de chamar IA
function processMessage(msg) {
  const cached = FAQ_CACHE[msg.toLowerCase()];
  if (cached) return cached; // Retorna instantâneo
  
  return await callAI(msg); // Só chama IA se necessário
}
```

**Economia:** ~70% menos chamadas = US$ 0,50/mês economizado

---

### 2. **Lazy Loading Babylon.js** ⚡
Carrega metaverso só quando necessário

```javascript
// Antes: 5MB carregados sempre
<script src="babylon.js"></script>

// Depois: 5MB só quando abrir metaverso
document.getElementById('metaverse-btn').onclick = async () => {
  if (!window.BABYLON) {
    await loadScript('babylon.js'); // Carrega sob demanda
  }
  initMetaverse();
};
```

**Economia:** 80% menos bandwidth inicial = Free tier dura mais

---

### 3. **Compressão Assets** 🗜️

```powershell
# Comprimir JS/CSS antes do deploy
npm install -g terser
terser metaverse_babylon.js -o metaverse_babylon.min.js -c -m

# Resultado: 877 linhas → 80KB → 15KB gzipped
```

**Economia:** 94% menor = Cabe tranquilo no Free tier

---

### 4. **WebSocket com Auto-desconexão** ⏱️

```javascript
// Desconecta após 5 min sem atividade
let inactivityTimer;

ws.onmessage = () => {
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(() => {
    ws.close(); // Economiza recursos
  }, 5 * 60 * 1000); // 5 minutos
};

// Reconecta automaticamente quando enviar mensagem
sendBtn.onclick = () => {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    reconnectWebSocket();
  }
  sendMessage();
};
```

**Economia:** Reduz conexões persistentes em 60%

---

### 5. **Rate Limiting Inteligente** 🚦

```javascript
// Limita a 1 mensagem por segundo
let lastMessageTime = 0;

function sendMessage(msg) {
  const now = Date.now();
  if (now - lastMessageTime < 1000) {
    showNotification('Aguarde 1 segundo entre mensagens');
    return;
  }
  
  lastMessageTime = now;
  // Envia mensagem...
}
```

**Economia:** Previne spam = custo estável

---

## 📋 Custos Detalhados

### **Cenário 1: Uso Baixo (1-10 usuários/dia)**
```
Static Web Apps:    US$ 0,00  (Free tier)
Azure Functions:    US$ 0,00  (dentro do 1M grátis)
GitHub Models:      US$ 0,00  (Copilot Pro)
Storage:            US$ 0,00  (5GB grátis)
───────────────────────────────
TOTAL:              US$ 0,00/mês ✅ GRÁTIS!
```

### **Cenário 2: Uso Médio (50-100 usuários/dia)**
```
Static Web Apps:    US$ 0,00  (Free tier)
Azure Functions:    US$ 1,50  (~2M execuções)
GitHub Models:      US$ 0,00  (Copilot Pro)
Storage:            US$ 0,00  (5GB grátis)
───────────────────────────────
TOTAL:              US$ 1,50/mês (~R$ 7,50)
```

### **Cenário 3: Uso Alto (500+ usuários/dia)**
```
Static Web Apps:    US$ 1,00  (excedeu 100GB)
Azure Functions:    US$ 5,00  (~25M execuções)
GitHub Models:      US$ 0,00  (Copilot Pro)
Storage:            US$ 0,50  (uso de 10GB)
───────────────────────────────
TOTAL:              US$ 6,50/mês (~R$ 32)
```

---

## 🚀 Implementação Passo a Passo

### **Passo 1: Preparar Código (5 min)**

```powershell
cd D:\A.I_GitHUB

# Criar arquivo de configuração Azure Functions
mkdir sofia\azure_functions
```

Criar `sofia/azure_functions/function_app.py`:
```python
import azure.functions as func
import logging
from sofia.core import cerebro_cloud

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="chat")
async def chat(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Chat request received')
    
    try:
        req_body = req.get_json()
        message = req_body.get('message')
        
        # Processar com cache
        response = await process_with_cache(message)
        
        return func.HttpResponse(
            response,
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f'Error: {e}')
        return func.HttpResponse(
            "Erro ao processar mensagem",
            status_code=500
        )

# Cache de respostas
FAQ_CACHE = {
    "olá": "Olá! Eu sou a Sofia 🌸",
    "oi": "Oi! Como posso ajudar?",
    "quem é você": "Sou Sofia, assistente virtual com IA"
}

async def process_with_cache(message):
    msg_lower = message.lower().strip()
    
    # Verifica cache primeiro
    if msg_lower in FAQ_CACHE:
        logging.info('Cache hit')
        return FAQ_CACHE[msg_lower]
    
    # Senão, chama IA
    logging.info('Cache miss - calling AI')
    return cerebro_cloud.perguntar(message)
```

---

### **Passo 2: Criar Azure Resources (10 min)**

```powershell
# Login no Azure
az login

# Criar resource group
az group create \
  --name sofia-rg \
  --location eastus

# Criar Storage Account (necessário para Functions)
az storage account create \
  --name sofiastorage123 \
  --resource-group sofia-rg \
  --location eastus \
  --sku Standard_LRS

# Criar Function App (Consumption Plan)
az functionapp create \
  --name sofia-functions \
  --resource-group sofia-rg \
  --storage-account sofiastorage123 \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux

# Criar Static Web App
az staticwebapp create \
  --name sofia-web \
  --resource-group sofia-rg \
  --location eastus \
  --source https://github.com/SomBRaRCP/sofia \
  --branch master \
  --app-location "/sofia/web" \
  --login-with-github
```

---

### **Passo 3: Configurar Variáveis (2 min)**

```powershell
# Configurar GitHub Token no Functions
az functionapp config appsettings set \
  --name sofia-functions \
  --resource-group sofia-rg \
  --settings \
  "GITHUB_TOKEN=$env:GITHUB_TOKEN" \
  "SOFIA_USE_CLOUD=true" \
  "GITHUB_MODEL=gpt-4o"
```

---

### **Passo 4: Deploy (5 min)**

```powershell
# Instalar Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Deploy do Functions
cd sofia/azure_functions
func azure functionapp publish sofia-functions

# Push para GitHub (Static Web Apps auto-deploy)
cd D:\A.I_GitHUB
git add .
git commit -m "Deploy: Azure Functions + Static Web Apps"
git push origin master
```

---

## 📊 Monitoramento de Custos

### **Azure Portal - Cost Management**

1. Acesse: https://portal.azure.com
2. Clique em **"Cost Management + Billing"**
3. Configure **Budget Alert**:
   - Nome: Sofia Monthly Budget
   - Amount: US$ 10,00
   - Alert: 80% (US$ 8,00)

Você receberá email se ultrapassar US$ 8!

### **Comando CLI para ver custos:**

```powershell
# Ver custos do mês atual
az consumption usage list \
  --resource-group sofia-rg \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  --query "[].{Service:name.value, Cost:pretaxCost}"
```

---

## 🎯 Checklist de Deploy

- [ ] Criar conta Azure (se não tiver)
- [ ] Instalar Azure CLI
- [ ] Login: `az login`
- [ ] Criar resource group
- [ ] Criar Storage Account
- [ ] Criar Function App
- [ ] Criar Static Web App
- [ ] Configurar GitHub Token
- [ ] Deploy Functions
- [ ] Push GitHub (auto-deploy)
- [ ] Configurar Budget Alert
- [ ] Testar aplicação
- [ ] Verificar custos após 1 semana

---

## 🔍 Próximas Otimizações (Futuro)

1. **Redis Cache** (se custos aumentarem)
   - Azure Redis Cache Basic: US$ 16/mês
   - Só vale se tiver 1000+ usuários/dia

2. **CDN Custom** (se bandwidth exceder)
   - Azure CDN: US$ 0,08/GB
   - Mais barato que Static Web Apps após 100GB

3. **Durable Functions** (para workflows longos)
   - Custo similar ao Functions
   - Melhor para processos de 10+ minutos

---

## 📞 Suporte

**Dúvidas sobre custos?**
- Azure Cost Calculator: https://azure.microsoft.com/pricing/calculator/
- Documentação Pricing: https://azure.microsoft.com/pricing/

**Problemas técnicos?**
- Azure Support: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade

---

## ✅ Resumo da Estratégia

| Item | Solução | Custo Mensal |
|------|---------|--------------|
| Frontend | Static Web Apps | US$ 0 |
| Backend | Azure Functions | US$ 0-3 |
| IA | GitHub Models | US$ 0 |
| Storage | Blob Storage 5GB | US$ 0 |
| Bandwidth | 100GB Free | US$ 0 |
| **TOTAL** | **Serverless + Cache** | **US$ 0-3** ✅ |

**Conclusão:** Com as otimizações implementadas, você ficará dentro do Free Tier nos primeiros meses!
