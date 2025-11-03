# 🔧 Resolver Problema: Sofia Não Lê PDFs

## 🚨 Problema
Sofia responde: *"PyPDF2 não foi instalado em meu sistema"*

## ✅ Solução

### Passo 1: Parar o Servidor
Se o servidor Flask está rodando, **pare-o**:
- Pressione `Ctrl + C` no terminal

### Passo 2: Verificar Instalação
```bash
D:/A.I_GitHUB/.venv/Scripts/python.exe -c "import PyPDF2; print('PyPDF2:', PyPDF2.__version__)"
```

Se aparecer `PyPDF2: 3.0.1` → Está instalado! ✅

### Passo 3: Reiniciar o Servidor
```bash
cd D:\A.I_GitHUB\sofia
python api.py
```

### Passo 4: Testar Diagnóstico
Abra no navegador:
```
http://localhost:5000/status
```

Você deve ver:
```json
{
  "status": "online",
  "sofia": "ready",
  "bibliotecas": {
    "PyPDF2": "✅ Disponível (v3.0.1)",
    "Pillow": "✅ Disponível",
    "pytesseract": "✅ Disponível",
    "numpy": "✅ Disponível (v2.3.4)"
  }
}
```

### Passo 5: Testar PDF
1. Recarregue a interface web (F5)
2. Clique em 📎 Anexar
3. Selecione um PDF
4. Digite: "Resuma este documento"
5. Envie

Sofia deve responder com:
```
Variável criada: pdftex_[timestamp]

[Resumo do conteúdo...]
```

## 🔍 Se Ainda Não Funcionar

### Opção A: Reinstalar PyPDF2
```bash
D:/A.I_GitHUB/.venv/Scripts/pip.exe uninstall PyPDF2 -y
D:/A.I_GitHUB/.venv/Scripts/pip.exe install PyPDF2==3.0.1
```

### Opção B: Verificar Ambiente Virtual
```bash
# Ver qual Python está sendo usado
D:/A.I_GitHUB/.venv/Scripts/python.exe -c "import sys; print(sys.executable)"
```

Deve mostrar: `D:\A.I_GitHUB\.venv\Scripts\python.exe`

### Opção C: Instalar Todas as Dependências Novamente
```bash
cd D:\A.I_GitHUB\sofia
D:/A.I_GitHUB/.venv/Scripts/pip.exe install -r requirements.txt
```

## 📌 Lembre-se

**SEMPRE reinicie o servidor após instalar bibliotecas!**

Python carrega os imports apenas uma vez quando o servidor inicia. Se você instalou PyPDF2 com o servidor já rodando, ele não será detectado até reiniciar.

## 🎯 Checklist Rápido

- [ ] PyPDF2 instalado no ambiente virtual
- [ ] Servidor Flask **reiniciado** após instalação
- [ ] Teste `/status` mostra PyPDF2 ✅
- [ ] Interface web recarregada (F5)
- [ ] PDF anexado com sucesso
- [ ] Sofia responde com `Variável criada: pdftex_...`

Se todos os checkmarks estiverem ✅, o sistema está funcionando corretamente! 🌸
