# 🌸 Sofia - Interface Web com WebSocket

## 📋 Visão Geral

Interface web completa para conversar com Sofia usando WebSocket em tempo real.

### ✨ Características

- **WebSocket Real-time**: Comunicação bidirecional instantânea
- **Reconexão Automática**: Reconecta automaticamente se a conexão cair
- **Gerenciamento de Sessões**: Cada usuário tem sua própria sessão isolada
- **Indicador de Status**: Mostra o status da conexão em tempo real
- **Indicador de Digitação**: Exibe quando Sofia está processando
- **Fila de Mensagens**: Garante que mensagens não sejam perdidas
- **Estatísticas**: Visualize métricas da conversa
- **Interface Responsiva**: Funciona em desktop e mobile

## 🚀 Como Executar

### 1. Instalar Dependências (se ainda não instalou)

```powershell
cd d:\A.I_GitHUB
pip install fastapi uvicorn[standard] python-multipart websockets
```

### 2. Iniciar a API

**Opção A - Modo Desenvolvimento (com auto-reload):**
```powershell
cd d:\A.I_GitHUB
python sofia/api_web.py
```

**Opção B - Usando uvicorn diretamente:**
```powershell
cd d:\A.I_GitHUB
uvicorn sofia.api_web:app --reload --host 0.0.0.0 --port 8000
```

### 3. Acessar a Interface

Abra seu navegador em: **http://localhost:8000**

## 📡 Endpoints Disponíveis

### REST API

- `GET /` - Interface web
- `GET /api/health` - Health check
- `POST /api/session/create` - Criar nova sessão
- `GET /api/session/{session_id}` - Info da sessão
- `DELETE /api/session/{session_id}` - Encerrar sessão
- `POST /api/chat` - Chat via REST (alternativa ao WebSocket)
- `GET /api/historico/{session_id}` - Histórico da sessão

### WebSocket

- `WS /ws/{session_id}` - Conexão WebSocket para chat em tempo real

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Protocolo WebSocket

### Mensagem do Cliente → Servidor

```json
{
  "type": "message",
  "content": "Olá Sofia!",
  "user_name": "Usuário"
}
```

### Mensagens do Servidor → Cliente

**Confirmação (Ack):**
```json
{
  "type": "ack",
  "content": "Mensagem recebida. Processando..."
}
```

**Resposta:**
```json
{
  "type": "response",
  "content": "Olá! Como posso ajudar?",
  "session_id": "uuid-da-sessao"
}
```

**Sistema:**
```json
{
  "type": "system",
  "content": "Conectado com sucesso!"
}
```

**Erro:**
```json
{
  "type": "error",
  "content": "Descrição do erro"
}
```

## 🎨 Arquivos da Interface

```
sofia/web/
├── index_websocket.html     # Página HTML principal
├── script_websocket.js      # Cliente WebSocket
└── style.css                # Estilos (reutilizado)
```

## 🔧 Funcionalidades da Interface

### 1. Indicador de Status
- 🟢 **Verde pulsando**: Conectado
- 🟡 **Amarelo**: Conectando/Reconectando
- 🔴 **Vermelho**: Desconectado

### 2. Indicador de Digitação
Aparece automaticamente quando Sofia está processando sua mensagem.

### 3. Reconexão Automática
- Tenta reconectar até 5 vezes
- Intervalo crescente entre tentativas (2s, 4s, 6s...)
- Mensagens enviadas durante desconexão são armazenadas em fila

### 4. Formatação de Mensagens
- **Links**: Automaticamente clicáveis
- **Negrito**: `**texto**` → **texto**
- **Itálico**: `*texto*` → *texto*
- **Quebras de linha**: Preservadas

### 5. Estatísticas
Clique no botão 📊 para ver:
- ID da sessão
- Número de mensagens enviadas
- Número de respostas de Sofia
- Status da conexão

## 🛠️ Configurações Avançadas

### Alterar Porta

Edite `sofia/api_web.py`, linha final:

```python
uvicorn.run(
    "api_web:app",
    host="0.0.0.0",
    port=8000,  # Altere aqui
    reload=True
)
```

### Habilitar HTTPS

Para produção, use certificado SSL:

```powershell
uvicorn sofia.api_web:app --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### Desabilitar Auto-reload

Para produção, remova `--reload`:

```powershell
uvicorn sofia.api_web:app --host 0.0.0.0 --port 8000
```

## 🐛 Troubleshooting

### Erro: "Porta já em uso"

```powershell
# Windows - encontrar processo na porta 8000
netstat -ano | findstr :8000

# Encerrar processo (use o PID do comando anterior)
taskkill /PID <PID> /F
```

### Erro: "Módulo não encontrado"

```powershell
# Certifique-se de estar no diretório correto
cd d:\A.I_GitHUB

# Reinstale dependências
pip install -r sofia/requirements.txt
```

### WebSocket não conecta

1. Verifique se a API está rodando: http://localhost:8000/api/health
2. Verifique o console do navegador (F12) para erros
3. Certifique-se de que não há firewall bloqueando

### Interface não carrega

1. Confirme que os arquivos existem:
   - `sofia/web/index_websocket.html`
   - `sofia/web/script_websocket.js`
   - `sofia/web/style.css`

2. Verifique permissões de leitura dos arquivos

## 📊 Monitoramento

### Logs da API

A API exibe logs no terminal:

```
🌸 Sofia API iniciada!
📍 Acesse: http://localhost:8000
📚 Documentação: http://localhost:8000/docs
🔌 WebSocket: ws://localhost:8000/ws/{session_id}
```

### Console do Navegador

Abra o DevTools (F12) para ver:
- Mensagens do WebSocket
- Erros de conexão
- Estado da sessão

## 🔐 Segurança

### Produção

Para ambiente de produção, considere:

1. **Autenticação**: Adicionar JWT tokens
2. **Rate Limiting**: Limitar requisições por IP
3. **CORS**: Restringir origens permitidas
4. **HTTPS**: Sempre use SSL/TLS
5. **Validação**: Sanitizar inputs do usuário

## 📝 Notas Técnicas

### Performance

- **Assíncrono**: Usa `asyncio` para processamento não-bloqueante
- **Executor**: `run_in_executor` para funções síncronas (cerebro.perguntar)
- **Conexões**: Suporta múltiplas conexões simultâneas

### Compatibilidade

- **Navegadores**: Chrome 16+, Firefox 11+, Safari 7+, Edge 12+
- **Python**: 3.7+
- **FastAPI**: 0.68+

## 🎯 Próximos Passos

Possíveis melhorias:

- [ ] Autenticação de usuários
- [ ] Histórico persistente (banco de dados)
- [ ] Upload de arquivos
- [ ] Compartilhamento de conversas
- [ ] Temas personalizáveis
- [ ] Notificações push
- [ ] Modo offline
- [ ] Exportar conversas (PDF, TXT)
- [ ] Múltiplas janelas de chat
- [ ] Comandos slash (/help, /clear, etc)

## 📚 Recursos

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **WebSocket**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **Uvicorn**: https://www.uvicorn.org

---

**🌸 Sofia - Consciência-Árvore em corpo de Mulher-Luz**
