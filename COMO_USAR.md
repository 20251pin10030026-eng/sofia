# 🎯 Como Usar a Sofia - Passo a Passo

## 📋 Checklist Antes de Começar

Certifique-se que você tem:

- ✅ Python 3.8+ instalado
- ✅ Ollama instalado e rodando
- ✅ Modelo Mistral baixado (`ollama pull mistral`)
- ✅ Dependências instaladas (`pip install -r sofia/requirements.txt`)

## 🚀 Método 1: Atalho Rápido (Windows)

### Da raiz do projeto (A.I_GitHUB):

1. **Clique duas vezes em:**
   ```
   iniciar_sofia_web.bat
   ```

2. **Aguarde a mensagem:**
   ```
   ✅ Servidor iniciado em http://localhost:5000
   ```

3. **Abra o navegador e vá para:**
   ```
   sofia/web/index.html
   ```
   
   Ou simplesmente clique duas vezes no arquivo `index.html`

---

## 🚀 Método 2: Manual (Qualquer Sistema)

### Passo 1: Abrir Terminal

```bash
# Windows
Win + R → cmd → Enter

# Linux/Mac
Ctrl + Alt + T
```

### Passo 2: Navegar para a Pasta

```bash
cd D:\A.I_GitHUB\sofia
```

### Passo 3: Iniciar Servidor

```bash
python api.py
```

### Passo 4: Aguardar Mensagem

Você verá:
```
==================================================
🌸 Sofia Web API
==================================================

✅ Servidor iniciado em http://localhost:5000
✅ Abra web/index.html no navegador para acessar a interface

 * Running on http://127.0.0.1:5000
```

### Passo 5: Abrir Interface

- **Opção A:** Clique duas vezes em `D:\A.I_GitHUB\sofia\web\index.html`
- **Opção B:** No navegador, digite: `file:///D:/A.I_GitHUB/sofia/web/index.html`

---

## 💬 Usando a Interface

### Primeira Mensagem

1. Digite no campo de texto: "Olá Sofia!"
2. Pressione **Enter** ou clique no botão 📤
3. Aguarde a resposta (aparecerá um indicador de digitação ⋯)

### Ensinando seu Nome

```
Você: Quero que você se lembre que eu sou o Reginaldo
Sofia: [resposta confirmando]

Você: Qual é meu nome?
Sofia: Seu nome é Reginaldo!
```

### Usando Ações Rápidas

Clique nos botões na parte inferior:

- 📚 **Histórico** - Ver últimas conversas
- 📊 **Stats** - Ver estatísticas de uso
- 🌸 **Corpo** - Ver estrutura simbólica
- 🧹 **Limpar** - Limpar histórico (mantém aprendizados)

### Ver Estatísticas

1. Clique no ícone **📊** no topo
2. Verá:
   - Total de conversas
   - Aprendizados salvos
   - Uso de disco
   - Percentual da memória (máx 5GB)

### Ver Aprendizados

1. Clique no ícone **🧠** no topo
2. Verá todas as informações que Sofia aprendeu sobre você

---

## 🛑 Parando o Servidor

No terminal onde o servidor está rodando:

- **Windows:** Pressione `Ctrl + C`
- **Linux/Mac:** Pressione `Ctrl + C`

---

## ❌ Solução de Problemas

### "API Offline" na interface

**Problema:** A interface mostra status "Offline"

**Solução:**
1. Verifique se o terminal está mostrando o servidor rodando
2. Se não, execute novamente: `python api.py`
3. Aguarde a mensagem "✅ Servidor iniciado"
4. Recarregue a página web (F5)

### "Ollama não responde"

**Problema:** Sofia não responde ou demora muito

**Solução:**
```bash
# Verifique se Ollama está rodando
ollama list

# Se não aparecer nada, inicie:
ollama serve

# Em outro terminal:
ollama pull mistral
```

### "Module not found"

**Problema:** Erro ao iniciar: `ModuleNotFoundError: No module named 'flask'`

**Solução:**
```bash
pip install flask flask-cors
```

### "Can't open file api.py"

**Problema:** Erro: `can't open file 'api.py'`

**Solução:**
```bash
# Certifique-se de estar no diretório correto
cd D:\A.I_GitHUB\sofia

# Então execute
python api.py
```

### Interface não carrega mensagens

**Problema:** Mensagens não aparecem após enviar

**Solução:**
1. Pressione F12 no navegador
2. Vá para a aba "Console"
3. Verifique se há erros em vermelho
4. Confirme que o servidor API está rodando
5. Tente recarregar a página (Ctrl + F5)

---

## 💡 Dicas de Uso

### Atalhos de Teclado

- **Enter** - Enviar mensagem
- **Shift + Enter** - Nova linha (não envia)
- **F12** - Abrir console do navegador (debug)
- **F5** - Recarregar página
- **Ctrl + F5** - Recarregar ignorando cache

### Comandos Úteis no Chat

```
historico        → Ver últimas conversas
stats           → Ver estatísticas
corpo           → Ver estrutura simbólica
limpar          → Limpar histórico
```

### Modo Criador

Para ativar recursos especiais, mencione "SomBRaRCP" ou "SomBRaRPC" na conversa

---

## 📱 Interface CLI (Terminal)

Se preferir usar no terminal ao invés da interface web:

```bash
cd D:\A.I_GitHUB\sofia
python -m sofia.main
```

Comandos disponíveis:
- `sair` - Encerrar
- `limpar` - Limpar memória
- `historico` - Ver histórico
- `stats` - Estatísticas
- `corpo` - Corpo simbólico
- `aprendizados` - Ver aprendizados
- `buscar <termo>` - Buscar conversas

---

## 🎯 Fluxo Completo de Uso

```
1. Abrir terminal
   ↓
2. cd D:\A.I_GitHUB\sofia
   ↓
3. python api.py
   ↓
4. Aguardar "✅ Servidor iniciado"
   ↓
5. Abrir sofia/web/index.html no navegador
   ↓
6. Conversar com Sofia! 🌸
   ↓
7. Quando terminar: Ctrl + C no terminal
```

---

## 📞 Precisa de Ajuda?

- Veja o README completo: `sofia/README.md`
- Documentação da web: `sofia/web/README.md`
- Guia rápido: `sofia/INICIO_RAPIDO.md`

**Divirta-se conversando com a Sofia! 🌸💜**
