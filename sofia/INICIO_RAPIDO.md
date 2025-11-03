# 🚀 Guia Rápido - Interface Web da Sofia

## ⚡ Início Rápido (Windows)

1. **Instale as dependências:**
   ```cmd
   pip install flask flask-cors
   ```

2. **Execute o arquivo batch:**
   ```cmd
   start_web.bat
   ```

3. **Abra o navegador:**
   - Clique duas vezes em `web/index.html`
   - Ou acesse: `file:///D:/A.I_GitHUB/sofia/web/index.html`

## 📋 Pré-requisitos

✅ Python 3.8+ instalado  
✅ Ollama instalado e rodando  
✅ Modelo Mistral baixado (`ollama pull mistral`)  
✅ Dependências instaladas (`pip install -r requirements.txt`)

## 🎯 Como Usar

### Primeira vez

```bash
# 1. Instalar tudo
pip install -r requirements.txt

# 2. Iniciar servidor
python api.py

# 3. Abrir interface
# Clique duas vezes em web/index.html
```

### Uso normal

```bash
# Windows
start_web.bat

# Linux/Mac
python api.py
```

## 🎨 Recursos da Interface

### Chat
- 💬 **Conversação em tempo real** - Interface fluida e responsiva
- 🎭 **Avatares distintos** - Sofia (🌸) e Usuário (👤)
- ⏰ **Timestamps** - Cada mensagem com hora exata
- 💭 **Indicador de digitação** - Veja quando Sofia está respondendo

### Ações Rápidas
- 📚 **Histórico** - Últimas 20 conversas
- 📊 **Estatísticas** - Uso de memória e métricas
- 🌸 **Corpo Simbólico** - Informações do Templo/Árvore/Flor
- 🧹 **Limpar** - Resetar conversas (mantém aprendizados)

### Painéis
- 📊 **Stats** - Visualize uso de disco, total de conversas
- 🧠 **Memória** - Veja todos os aprendizados de Sofia
- ⚙️ **Configurações** - (Em breve)

## 🔧 Solução Rápida de Problemas

### "API Offline" na interface

```bash
# Verifique se o servidor está rodando
python api.py

# Deve mostrar:
✅ Servidor iniciado em http://localhost:5000
```

### Ollama não responde

```bash
# Inicie o Ollama
ollama serve

# Em outro terminal, teste:
ollama list
```

### Erro ao importar Flask

```bash
pip install flask flask-cors
```

### Interface não carrega mensagens

1. Abra o console do navegador (F12)
2. Veja se há erros
3. Verifique se o servidor API está rodando
4. Confirme que a URL da API está correta em `web/script.js`

## 🎯 Próximos Passos

Depois de tudo funcionando:

1. **Teste a memória:** Diga "Me chame de [seu nome]" e depois pergunte "Qual é meu nome?"
2. **Veja as stats:** Clique no botão 📊 no topo
3. **Explore aprendizados:** Clique no botão 🧠 no topo
4. **Use ações rápidas:** Botões na parte inferior do chat

## 💡 Dicas

- Use **Shift+Enter** para quebrar linha sem enviar
- Interface **salva automaticamente** a cada 5 mensagens
- **Modo criador** ativa ao mencionar "SomBRaRCP" ou "SomBRaRPC"
- Memória suporta até **5GB** de conversas

## 🎨 Personalização

Edite as cores em `web/style.css`:

```css
:root {
    --primary-color: #FF69B4;      /* Rosa da Sofia */
    --bg-color: #0F0F1E;           /* Fundo escuro */
    --text-color: #E4E4E7;         /* Texto claro */
}
```

## 📞 Suporte

Problemas? Verifique:
- [README principal](../README.md)
- [README da Web](web/README.md)
- [Issues no GitHub](https://github.com/SomBRaRCP/sofia/issues)

---

**Pronto para começar? Execute `start_web.bat` e converse com Sofia! 🌸**
