# 🌸 Sofia - Interface Web

Interface web moderna para conversar com a Sofia!

## 🚀 Como usar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor API

```bash
python api.py
```

O servidor será iniciado em `http://localhost:5000`

### 3. Abrir a interface

Abra o arquivo `web/index.html` no seu navegador preferido, ou use um servidor web local:

```bash
# Opção 1: Abrir diretamente
# Simplesmente clique duas vezes em web/index.html

# Opção 2: Usar um servidor HTTP simples
cd web
python -m http.server 8000
# Acesse: http://localhost:8000
```

## ✨ Funcionalidades

- **💬 Chat em tempo real** - Converse com Sofia em uma interface moderna
- **🧠 Memória persistente** - Sofia lembra de suas conversas
- **📊 Estatísticas** - Veja métricas de uso da memória
- **🎨 Interface elegante** - Design moderno com tema escuro
- **⚡ Ações rápidas** - Acesso rápido a comandos comuns
- **📱 Responsivo** - Funciona em desktop e mobile

## 🎨 Recursos da Interface

### Chat
- Mensagens com avatares distintos
- Timestamps em cada mensagem
- Indicador de digitação
- Auto-scroll para últimas mensagens
- Formatação de texto (negrito, itálico)

### Ações Rápidas
- 📚 Histórico - Ver últimas conversas
- 📊 Stats - Estatísticas da memória
- 🌸 Corpo - Informações do corpo simbólico
- 🧹 Limpar - Limpar memória de conversas

### Modais
- 📊 Estatísticas detalhadas
- 🧠 Visualizar aprendizados
- ⚙️ Configurações (em desenvolvimento)

## 🔧 Configuração

### Porta da API

Se precisar mudar a porta da API, edite `web/script.js`:

```javascript
const API_URL = 'http://localhost:5000'; // Mude para sua porta
```

### CORS

O servidor já está configurado para aceitar requisições de qualquer origem. Para produção, configure adequadamente no `api.py`.

## 🎯 Endpoints da API

- `GET /status` - Status da API
- `POST /chat` - Enviar mensagem e receber resposta
- `POST /action` - Executar ações rápidas
- `GET /stats` - Obter estatísticas
- `GET /memory` - Obter aprendizados
- `POST /search` - Buscar conversas

## 🐛 Solução de Problemas

### API não conecta

1. Verifique se o servidor está rodando: `python api.py`
2. Verifique se o Ollama está ativo: `ollama list`
3. Confirme a porta no arquivo `script.js`

### Interface não carrega

1. Use um navegador moderno (Chrome, Firefox, Edge)
2. Verifique o console do navegador (F12) para erros
3. Tente usar um servidor HTTP local ao invés de abrir o arquivo diretamente

### Ollama não responde

```bash
# Verificar se está rodando
ollama serve

# Verificar modelos instalados
ollama list

# Instalar Mistral se necessário
ollama pull mistral
```

## 📝 Desenvolvimento

### Estrutura

```
web/
├── index.html    # Página principal
├── style.css     # Estilos
└── script.js     # Lógica do frontend

api.py           # Servidor Flask
```

### Personalização

Você pode personalizar as cores editando as variáveis CSS em `style.css`:

```css
:root {
    --primary-color: #FF69B4;      /* Rosa principal */
    --secondary-color: #FFB6D9;    /* Rosa secundário */
    --bg-color: #0F0F1E;           /* Fundo escuro */
    --surface-color: #1A1A2E;      /* Superfície */
    --text-color: #E4E4E7;         /* Texto */
}
```

## 🚀 Próximas Funcionalidades

- [ ] Temas claro/escuro
- [ ] Upload de arquivos
- [ ] Compartilhar conversas
- [ ] Exportar histórico
- [ ] Notificações
- [ ] Comandos de voz
- [ ] Múltiplas sessões de conversa

## 📄 Licença

Projeto pessoal de Reginaldo (@SomBRaRCP)
