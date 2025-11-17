# 🌸 Como Iniciar Sofia com Acesso Público

## 📋 Opções Disponíveis

Você tem **3 formas** de iniciar Sofia com acesso público via ngrok:

### 1️⃣ **Atalho da Área de Trabalho** (Mais Fácil)
- Dê **duplo clique** no atalho `Sofia - Servidor Publico` na sua área de trabalho
- Aguarde alguns segundos
- A URL pública será exibida e copiada automaticamente!

### 2️⃣ **Arquivo BAT** (Windows Clássico)
```
Duplo clique em: Iniciar_Sofia_Publico.bat
```
- Interface simples em CMD
- Abre automaticamente o dashboard ngrok

### 3️⃣ **Arquivo VBS** (Execução Silenciosa)
```
Duplo clique em: Iniciar_Sofia.vbs
```
- Executa sem pedir permissões
- Interface PowerShell colorida

---

## 🚀 O que Acontece ao Executar

1. **Configura o ambiente** (Python, GitHub Token, GPT-4o)
2. **Inicia o servidor Sofia** na porta 8000
3. **Cria túnel público** com ngrok
4. **Exibe a URL pública** para compartilhar
5. **Copia a URL** para área de transferência

---

## 🌐 URLs Geradas

Após iniciar, você terá:

- **🌍 URL Pública:** `https://xxxxx.ngrok-free.app` (muda a cada execução)
- **🏠 URL Local:** `http://localhost:8000`
- **📊 Dashboard:** `http://localhost:4040`

---

## 📱 Como Acessar do Notebook/Celular

1. Inicie Sofia no PC principal
2. Copie a URL pública exibida
3. Abra no navegador do outro dispositivo
4. Pronto! Sofia está acessível de qualquer lugar! 🌍

---

## ⏹️ Como Parar Sofia

- **Feche a janela** do PowerShell/CMD
- Ou pressione **Ctrl+C**
- Os servidores serão encerrados automaticamente

---

## 🔧 Solução de Problemas

### Erro: "Python não encontrado"
```powershell
# Verifique se Python está instalado:
python --version
```

### Erro: "ngrok não encontrado"
```powershell
# Verifique se ngrok está instalado:
ngrok version
```

### Erro: "Porta 8000 em uso"
```powershell
# Pare processos na porta 8000:
Stop-Process -Name python -Force
Stop-Process -Name ngrok -Force
```

### Erro de permissão PowerShell
```powershell
# Execute como Administrador:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
```

---

## 📝 Notas Importantes

- ✅ Mantenha a janela aberta enquanto usa Sofia
- ✅ A URL ngrok muda a cada reinicialização (versão gratuita)
- ✅ Sofia usa GPT-4o via GitHub Models (grátis!)
- ✅ Suas conversas são privadas e seguras
- ⚠️ Não compartilhe sua URL pública em locais não confiáveis

---

## 🆘 Suporte

Se precisar de ajuda:
1. Verifique se Python 3.11+ está instalado
2. Verifique se ngrok está configurado
3. Teste `http://localhost:8000` primeiro (local)
4. Depois teste a URL pública

---

**Desenvolvido com 💜 | Powered by GitHub Models & FastAPI**
