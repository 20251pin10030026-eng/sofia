# 🌸 Sofia no Azure - Guia de Deploy **CUSTO ZERO**

## 🎯 Objetivo
Deploy da Sofia no Azure usando **100% recursos gratuitos**:
- ✅ Azure Static Web Apps (Frontend)
- ✅ GitHub Models API (IA - GRÁTIS com Copilot Pro)
- ✅ Azure Blob Storage (5GB grátis)
- ✅ GitHub Actions (CI/CD automático)

**Custo Total: R$ 0,00/mês** 🎉

---

## 📋 Pré-requisitos

### 1. Contas Necessárias
- [x] Conta GitHub (com Copilot Pro)
- [ ] Conta Azure (Azure for Students ou gratuita)
- [ ] GitHub Personal Access Token

### 2. Ferramentas Locais
- [x] Git instalado
- [x] Python 3.11+
- [ ] Azure CLI (opcional, mas recomendado)

---

## 🚀 Passo a Passo - Deploy

### **Etapa 1: Preparar GitHub Token**

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Configurações:
   - **Note:** `Sofia AI Access`
   - **Expiration:** 90 days (ou mais)
   - **Scopes:** Marque:
     - [x] `repo` (Full control)
     - [x] `read:user`
     - [x] `read:org`
4. Clique em **"Generate token"**
5. **COPIE O TOKEN** (só aparece uma vez!)

```
Exemplo: ghp_REDACTED
```

---

### **Etapa 2: Configurar Variáveis Locais**

1. Copie o arquivo de exemplo:
```powershell
cd d:\A.I_GitHUB\sofia
copy .env.example .env
```

2. Edite `.env` e configure:
```env
# Modo Cloud
SOFIA_USE_CLOUD=true

# GitHub Token (cole aqui)
GITHUB_TOKEN=ghp_seu_token_aqui

# Modelo (GPT-4o é o melhor e grátis!)
GITHUB_MODEL=gpt-4o

# Azure Storage (deixe vazio por enquanto)
AZURE_STORAGE_CONNECTION_STRING=
```

---

### **Etapa 3: Testar Localmente**

Antes de fazer deploy, vamos testar se funciona:

```powershell
# Instalar dependências
pip install -r requirements.txt

# Testar com GitHub Models
python -c "from sofia.core import cerebro_cloud; print(cerebro_cloud.perguntar('Olá, você está funcionando?'))"
```

**Resultado esperado:**
```
🌐 Sofia rodando em modo CLOUD (GitHub Models)
[DEBUG] Usando GitHub Models: gpt-4o
Olá! Sim, estou funcionando perfeitamente! 🌸
```

Se funcionar ✅, continue!

---

### **Etapa 4: Criar Azure Static Web App**

#### Opção A: Via Portal Azure (Recomendado)

1. Acesse: https://portal.azure.com
2. Faça login com sua conta de estudante
3. Clique em **"+ Create a resource"**
4. Busque por **"Static Web App"**
5. Clique em **"Create"**

**Configurações:**
```yaml
Subscription: Azure for Students
Resource Group: (criar novo) sofia-rg
Name: sofia-ai
Region: East US (ou Brazil South)
Plan type: Free
Deployment: GitHub
```

6. Clique em **"Sign in with GitHub"**
7. Autorize o acesso
8. Configure o repositório:
```yaml
Organization: SomBRaRCP
Repository: sofia
Branch: master
```

9. **Build Details:**
```yaml
Build Presets: Custom
App location: /sofia/web
Api location: /sofia
Output location: (deixe vazio)
```

10. Clique em **"Review + create"** → **"Create"**

**⏳ Aguarde 2-3 minutos...**

---

#### Opção B: Via Azure CLI (Avançado)

```powershell
# Login no Azure
az login

# Criar resource group
az group create --name sofia-rg --location eastus

# Criar Static Web App
az staticwebapp create \
  --name sofia-ai \
  --resource-group sofia-rg \
  --location eastus \
  --source https://github.com/SomBRaRCP/sofia \
  --branch master \
  --app-location "/sofia/web" \
  --api-location "/sofia" \
  --login-with-github
```

---

### **Etapa 5: Configurar Secrets no GitHub**

1. Vá para seu repositório no GitHub
2. Clique em **Settings** → **Secrets and variables** → **Actions**
3. Clique em **"New repository secret"**

Adicione os seguintes secrets:

#### Secret 1: AZURE_STATIC_WEB_APPS_API_TOKEN
```
Nome: AZURE_STATIC_WEB_APPS_API_TOKEN
Valor: (copie do Azure Portal)
```

**Como obter:**
- Azure Portal → sua Static Web App → **Manage deployment token**
- Copie o token

#### Secret 2: GITHUB_TOKEN_MODELS
```
Nome: GITHUB_TOKEN_MODELS
Valor: ghp_seu_token_github_aqui
```

---

### **Etapa 6: Push e Deploy Automático**

```powershell
# Commit das mudanças
git add .
git commit -m "🚀 Deploy Sofia para Azure com GitHub Models"

# Push para GitHub
git push origin master
```

**GitHub Actions vai automaticamente:**
1. ✅ Detectar o push
2. ✅ Rodar testes
3. ✅ Fazer build
4. ✅ Deploy no Azure
5. ✅ Configurar SSL/HTTPS

**⏳ Acompanhe em:** https://github.com/SomBRaRCP/sofia/actions

---

### **Etapa 7: Configurar Variáveis de Ambiente no Azure**

1. Azure Portal → sua Static Web App
2. Clique em **"Configuration"** (menu lateral)
3. Clique em **"+ Add"** em "Application settings"

Adicione:

| Nome | Valor |
|------|-------|
| `SOFIA_USE_CLOUD` | `true` |
| `GITHUB_TOKEN` | `ghp_seu_token` |
| `GITHUB_MODEL` | `gpt-4o` |
| `ENVIRONMENT` | `production` |

4. Clique em **"Save"**

---

### **Etapa 8: Testar a Aplicação**

1. Azure Portal → sua Static Web App
2. Copie a **URL** (ex: `https://sofia-ai.azurestaticapps.net`)
3. Abra no navegador

**Teste:**
- Digite: "Olá Sofia, você está na nuvem?"
- Resultado esperado: Resposta do GPT-4o!

---

## 🎉 **PRONTO! Sofia está no ar!**

### URLs de Acesso:
```
Frontend: https://sofia-ai.azurestaticapps.net
GitHub Actions: https://github.com/SomBRaRCP/sofia/actions
Azure Portal: https://portal.azure.com
```

---

## 🔧 Manutenção e Updates

### Deploy Automático
Todo push na branch `master` faz deploy automático!

```powershell
# Fazer mudança
git add .
git commit -m "Nova feature"
git push

# Deploy acontece automaticamente!
```

### Ver Logs
```powershell
# Via Azure CLI
az staticwebapp logs tail --name sofia-ai --resource-group sofia-rg
```

Ou no Azure Portal → sua app → **Log stream**

---

## 💰 Custos (ZERO!)

| Recurso | Limite Grátis | Custo |
|---------|---------------|-------|
| Azure Static Web Apps | 100GB bandwidth/mês | R$ 0 |
| GitHub Models (GPT-4o) | Uso moderado | R$ 0 |
| Azure Blob Storage | 5GB | R$ 0 |
| GitHub Actions | 2000 min/mês | R$ 0 |
| **TOTAL** | | **R$ 0/mês** |

---

## 🐛 Troubleshooting

### Erro: "GitHub Token inválido"
**Solução:**
1. Verifique se o token está correto em `.env` e no Azure
2. Token deve ter scope `repo` e `read:user`
3. Gere novo token se necessário

### Erro: "Deploy failed"
**Solução:**
1. Veja logs no GitHub Actions
2. Verifique se `app_location` e `api_location` estão corretos
3. Rode `git pull` para sincronizar

### Site não carrega
**Solução:**
1. Aguarde 5 minutos após primeiro deploy
2. Limpe cache do navegador (Ctrl+Shift+R)
3. Verifique URL correta no Azure Portal

### Sofia não responde
**Solução:**
1. Verifique variáveis de ambiente no Azure
2. Teste localmente primeiro
3. Veja logs no Azure Portal

---

## 📊 Monitoramento

### Verificar Status
```powershell
# Via CLI
az staticwebapp show --name sofia-ai --resource-group sofia-rg

# Via API
curl https://sofia-ai.azurestaticapps.net/status
```

### Métricas no Azure
Azure Portal → sua app → **Metrics**
- Requests
- Data in/out
- Response time

---

## 🔐 Segurança

### Boas Práticas Implementadas:
- ✅ HTTPS automático (SSL grátis)
- ✅ Tokens em secrets (não no código)
- ✅ CORS configurado
- ✅ Headers de segurança (CSP, X-Frame-Options)

### Recomendações:
- 🔒 Rotacione GitHub Token a cada 90 dias
- 🔒 Não commite arquivos `.env`
- 🔒 Use Azure Key Vault para produção (opcional)

---

## 🚀 Próximos Passos

### Opcional - Custom Domain
1. Azure Portal → sua app → **Custom domains**
2. Adicione seu domínio (ex: `sofia.seunome.com.br`)
3. Configure DNS conforme instruções

### Opcional - Azure Blob Storage
Se quiser persistir memória na nuvem:

```powershell
# Criar storage account
az storage account create \
  --name sofiastorage \
  --resource-group sofia-rg \
  --location eastus \
  --sku Standard_LRS

# Obter connection string
az storage account show-connection-string \
  --name sofiastorage \
  --resource-group sofia-rg
```

Adicione no Azure → Configuration:
```
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=...
AZURE_STORAGE_CONTAINER=sofia-memoria
```

---

## 📚 Recursos Úteis

- [Azure Static Web Apps Docs](https://docs.microsoft.com/azure/static-web-apps/)
- [GitHub Models API](https://github.com/marketplace/models)
- [Azure for Students](https://azure.microsoft.com/free/students/)
- [GitHub Actions](https://docs.github.com/actions)

---

## ❓ Precisa de Ajuda?

**Problemas?** Crie uma issue no GitHub:
https://github.com/SomBRaRCP/sofia/issues

**Dúvidas?** Consulte a documentação oficial do Azure.

---

## ✅ Checklist Final

- [ ] GitHub Token criado
- [ ] `.env` configurado
- [ ] Teste local funcionando
- [ ] Azure Static Web App criada
- [ ] Secrets configurados no GitHub
- [ ] Push realizado
- [ ] Deploy bem-sucedido
- [ ] Site acessível via HTTPS
- [ ] Sofia respondendo perguntas
- [ ] Variáveis de ambiente no Azure configuradas

**Tudo ✅? Parabéns! Sofia está na nuvem! 🎉**

---

**Última atualização:** 10/11/2025  
**Versão:** 1.0 - Deploy Grátis
