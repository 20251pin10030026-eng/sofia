# 🌸 Sofia - Arquivos para Deploy Azure

Esta pasta contém todos os arquivos necessários para fazer deploy da Sofia no Azure com **CUSTO ZERO**.

## 📁 Estrutura de Arquivos Criados

```
sofia/
├── 📄 .env.example                    # Variáveis de ambiente (copie para .env)
├── 📄 Dockerfile                      # Container Docker (opcional)
├── 📄 docker-compose.yml              # Orquestração Docker (opcional)
├── 📄 staticwebapp.config.json        # Config Azure Static Web Apps
├── 📄 DEPLOY_AZURE_GRATUITO.md        # 📚 GUIA COMPLETO DE DEPLOY
│
├── .github/
│   └── workflows/
│       └── azure-static-web-apps.yml  # CI/CD automático
│
└── core/
    ├── cerebro_cloud.py               # IA usando GitHub Models (GPT-4o)
    ├── cerebro_selector.py            # Alterna entre local/cloud
    └── storage_adapter.py             # Storage Azure Blob ou local
```

---

## 🚀 Como Usar

### 1️⃣ **Modo Local (Ollama) - Como antes**
```powershell
python api_web.py
```
Continua funcionando normalmente!

### 2️⃣ **Modo Cloud (GitHub Models) - Novo!**
```powershell
# Configurar
copy .env.example .env
# Editar .env e adicionar GITHUB_TOKEN

# Rodar
$env:SOFIA_USE_CLOUD="true"
python api_web.py
```

### 3️⃣ **Deploy no Azure - Custo Zero**
Siga o guia: [DEPLOY_AZURE_GRATUITO.md](DEPLOY_AZURE_GRATUITO.md)

---

## 🔧 Configuração Rápida

### Obter GitHub Token
1. https://github.com/settings/tokens
2. Generate new token (classic)
3. Marcar: `repo`, `read:user`, `read:org`
4. Copiar token

### Configurar .env
```env
SOFIA_USE_CLOUD=true
GITHUB_TOKEN=ghp_seu_token_aqui
GITHUB_MODEL=gpt-4o
```

### Testar
```powershell
pip install -r requirements.txt
python -c "from sofia.core import cerebro_cloud; print(cerebro_cloud.perguntar('Teste'))"
```

---

## 💰 Custos

| Modo | IA | Storage | Custo |
|------|----|---------| ------|
| **Local** | Ollama | Arquivo local | R$ 0 (hardware próprio) |
| **Cloud** | GitHub Models | Azure Blob (5GB) | **R$ 0/mês** ✅ |

---

## 📊 Comparação

### Local (Ollama)
✅ Controle total  
✅ Privacidade  
✅ Sem limites de uso  
❌ Precisa GPU potente  
❌ Só funciona no seu PC  
❌ Mais lento (GTX 1650)  

### Cloud (GitHub Models + Azure)
✅ **Grátis** com Copilot Pro  
✅ GPT-4o (melhor que Llama)  
✅ Acessível 24/7 de qualquer lugar  
✅ Rápido (servidores da Microsoft)  
✅ Escalável  
❌ Dependente de internet  
❌ Limites de uso (generosos)  

---

## 🎯 Recomendação

**Desenvolvimento:** Local (Ollama)  
**Produção/Compartilhar:** Cloud (Azure)

Ou use **AMBOS**! O código suporta os dois modos 🎉

---

## 📚 Documentação

- **Deploy:** [DEPLOY_AZURE_GRATUITO.md](DEPLOY_AZURE_GRATUITO.md)
- **GitHub Models:** https://github.com/marketplace/models
- **Azure Static Web Apps:** https://docs.microsoft.com/azure/static-web-apps/

---

## ✅ Próximos Passos

1. Ler [DEPLOY_AZURE_GRATUITO.md](DEPLOY_AZURE_GRATUITO.md)
2. Criar GitHub Token
3. Configurar .env
4. Testar localmente
5. Fazer deploy quando quiser!

---

**Tudo pronto para deploy CUSTO ZERO! 🚀**
