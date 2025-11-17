# 🌐 Busca Web - Sofia

## Nova Funcionalidade Implementada

Adicionado botão de **Buscar na Web** na interface web de Sofia!

### 📍 Localização

O botão está localizado ao lado do botão "Enviar" na área de input da mensagem.

### 🎨 Visual

- **Ícone**: Globo terrestre (🌐) em SVG
- **Estado Inativo**: Botão com borda transparente
- **Estado Ativo**: Botão com gradiente rosa e brilho

### 🔧 Funcionalidade

**Ao clicar no botão:**
1. Alterna entre modo web ATIVO/INATIVO
2. Mostra notificação visual do estado
3. Envia comando para o backend ativar/desativar o modo web

**Modo Web ATIVO:**
- Sofia pode buscar informações na internet automaticamente
- Detecta palavras-chave: "busque", "pesquise", "procure", etc.
- Acessa links fornecidos automaticamente
- Integra resultados de busca nas respostas

**Modo Web INATIVO:**
- Sofia responde apenas com conhecimento local
- Links ainda são detectados e acessados
- Sem buscas automáticas

### 💻 Arquivos Modificados

1. **`sofia/web/index.html`**
   - Adicionado botão `#web-search-btn` com ícone SVG de globo

2. **`sofia/web/style.css`**
   - Estilo `.web-search-btn` com estados normal/hover/active
   - Animação de escala no hover
   - Gradiente rosa quando ativo

3. **`sofia/web/script.js`**
   - Variável `webSearchMode` para controlar estado
   - Função `toggleWebSearchMode()` para alternar modo
   - Comunicação com backend via `/chat` endpoint

### 🎯 Uso

1. **Ativar Modo Web:**
   - Clique no botão do globo 🌐
   - Notificação: "Modo Web ATIVADO"
   - Botão fica destacado em rosa

2. **Fazer Busca:**
   - Com modo ativo, digite: "Busque informações sobre IA"
   - Sofia busca na internet e responde com resultados

3. **Acessar Link:**
   - Digite ou cole um link: "O que tem nesse site? https://..."
   - Sofia acessa e resume o conteúdo

4. **Desativar:**
   - Clique novamente no botão
   - Notificação: "Modo Web DESATIVADO"

### ✨ Detalhes Técnicos

**Backend:**
- Comando `web on` ativa `SOFIA_MODO_WEB=1`
- Comando `web off` desativa o modo
- Módulo `web_search.py` processa buscas

**Frontend:**
- Estado persistente durante a sessão
- Indicador visual claro do modo ativo
- Feedback instantâneo ao usuário

### 🔄 Integração

A funcionalidade está totalmente integrada com:
- Sistema de detecção de URLs
- Módulo de busca DuckDuckGo
- Extração de conteúdo web
- Processamento de contexto no cerebro.py

---

**Desenvolvido em:** 7 de novembro de 2025  
**Status:** ✅ Implementado e testado
