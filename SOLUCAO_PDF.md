# 🔧 Solução: Sofia não lê PDF no ngrok

## Problema
Sofia consegue fazer upload de PDF mas não extrai o texto, mostrando erro:
```
[UPLOAD PDF] PDF_DISPONIVEL: False
[UPLOAD PDF ERRO] PyPDF2 não disponível!
```

## Causa
O PyPDF2 está instalado, mas o servidor Python precisa ser **reiniciado** para reconhecer a biblioteca.

## ✅ Solução Rápida

### Opção 1: Usar o script automático
```powershell
cd D:\A.I_GitHUB
.\start_sofia.ps1
```

### Opção 2: Iniciar manualmente
1. **Pare o servidor** atual (Ctrl+C)

2. **Execute os comandos:**
```powershell
cd D:\A.I_GitHUB\sofia
$env:PYTHONPATH="D:\A.I_GitHUB"
$env:SOFIA_AUTORIDADE_DECLARADA="1"
& "D:\A.I_GitHUB\.venv\Scripts\python.exe" .\api_web.py
```

3. **Aguarde ver a mensagem:**
```
[VISAO INIT] ✅ PyPDF2 3.0.1 carregado com sucesso
```

4. **Teste novamente** o upload de PDF

## 📋 Verificação

Quando o servidor iniciar corretamente, você deve ver:
- ✅ `[VISAO INIT] ✅ PyPDF2 3.0.1 carregado com sucesso`
- ✅ Upload de PDF mostra: `PDF processado com sucesso! X caracteres extraídos`
- ✅ Sofia consegue ler e responder sobre o conteúdo do PDF

## 🔍 Troubleshooting

Se ainda não funcionar:
```powershell
# Verificar se PyPDF2 está instalado
& "D:\A.I_GitHUB\.venv\Scripts\python.exe" -m pip list | Select-String "PyPDF2"

# Se não aparecer, instalar:
& "D:\A.I_GitHUB\.venv\Scripts\python.exe" -m pip install PyPDF2

# Depois reiniciar o servidor
```

## 📝 Nota sobre Azure
O Azure Static Web App **NÃO** executa código Python - apenas serve HTML/CSS/JS.
**PDFs só funcionam via ngrok** (servidor local na sua máquina).
