# 📱 Ajustes Mobile - Sofia

## ✅ Alterações Implementadas

### 🎨 **CSS (style.css)**

1. **Altura Dinâmica**
   - Substituído `100vh` por `100dvh` (Dynamic Viewport Height)
   - Isso faz o layout se adaptar quando o teclado abre/fecha
   - Body com `position: fixed` para prevenir scroll indesejado

2. **Layout Responsivo Mobile**
   - Container com `flex-direction: column` e `overflow: hidden`
   - Chat container com `flex: 1` e `min-height: 0`
   - Input area com `flex-shrink: 0` (não encolhe)

3. **Prevenção de Zoom no iOS**
   - Input com `font-size: 16px` (previne zoom automático)
   - `appearance: none` para remover estilo padrão

4. **Ajustes de Espaçamento**
   - Header: padding reduzido para `0.75rem 1rem`
   - Input area: padding `0.75rem 1rem`
   - Isso economiza ~5px em cima e embaixo como solicitado

### 📜 **JavaScript (script.js)**

1. **Detecção de Teclado**
   ```javascript
   function handleViewportResize()
   ```
   - Detecta quando viewport diminui (teclado abre)
   - Adiciona classe `keyboard-open` no body
   - Calcula e armazena altura do teclado em CSS var

2. **Auto-scroll**
   - Quando input recebe foco, scroll automático para última mensagem
   - Quando perde foco, volta ao topo

3. **Prevenção de Scroll Elástico**
   - Previne o "bounce" do iOS quando scroll atinge topo/fundo
   - Melhora experiência de navegação

### 🌐 **HTML (index.html)**

1. **Meta Tags Adicionadas**
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
   <meta name="mobile-web-app-capable" content="yes">
   <meta name="apple-mobile-web-app-capable" content="yes">
   ```
   - Previne zoom manual
   - Modo PWA (Progressive Web App)
   - Barra de status translúcida no iOS

## 📏 **Comportamento no Mobile**

### Antes (Problema):
```
┌─────────────────┐
│    Header       │ ← Fixo
├─────────────────┤
│                 │
│     Chat        │ ← Jogado para cima
│                 │
├─────────────────┤
│  [Teclado]      │ ← Cobre parte do site
│                 │
└─────────────────┘
```

### Depois (Corrigido):
```
┌─────────────────┐
│    Header       │ ← Fixo (5px menos padding)
├─────────────────┤
│     Chat        │ ← Redimensiona
│   (diminui)     │ ← Não sobe!
├─────────────────┤
│    Input        │ ← Fixo (5px menos padding)
├─────────────────┤
│  [Teclado]      │ ← Layout se ajusta
└─────────────────┘
```

## 🧪 **Como Testar**

### No Desktop (Chrome DevTools):
1. Abra `http://localhost:8000`
2. Pressione `F12` (DevTools)
3. Clique no ícone de celular (Toggle Device Toolbar)
4. Selecione um dispositivo (ex: iPhone 12 Pro)
5. Clique no input de mensagem
6. Observe que o site **não sobe**, apenas redimensiona

### No Celular Real:
1. Acesse a URL ngrok no celular
2. Toque no campo de mensagem
3. O teclado vai abrir
4. O chat vai **diminuir** (não vai subir)
5. Header e input ficam visíveis
6. Quando fechar o teclado, volta ao tamanho normal

## 🎯 **Resultado Esperado**

✅ Site não "pula" quando teclado abre  
✅ Layout se adapta dinamicamente  
✅ Header sempre visível  
✅ Input sempre acessível  
✅ Chat redimensiona automaticamente  
✅ Sem zoom indesejado no iOS  
✅ Scroll suave e natural  
✅ 5px menos padding em cima e embaixo  

## 🔧 **CSS Custom Properties Criadas**

```css
--keyboard-height: 0px; /* Altura do teclado mobile */
```

Esta variável é atualizada dinamicamente quando o teclado abre.

## 📱 **Suporte**

- ✅ iOS Safari
- ✅ Android Chrome
- ✅ Android Firefox
- ✅ iOS Chrome
- ✅ Samsung Internet

## 🚀 **Próximos Passos (Opcional)**

Se quiser melhorar ainda mais:
1. PWA completo (manifest.json)
2. Service Worker (offline mode)
3. Instalação na home screen
4. Notificações push

---

**Desenvolvido com 💜 | Mobile-First Design**
