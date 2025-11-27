// API Configuration
const API_URL = 'https://bb2c49e1f597.ngrok-free.app';
const WS_URL = 'wss://bb2c49e1f597.ngrok-free.app';

// WebSocket
let ws = null;
let sessionId = null;
let isConnected = false;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;
let reconnectDelay = 2000;
let messageQueue = [];

// DOM Elements
const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const webSearchBtn = document.getElementById('web-search-btn');
const attachBtn = document.getElementById('attach-btn');
const fileInputChat = document.getElementById('file-input-chat');
const attachedFilesPreview = document.getElementById('attached-files-preview');
const attachedFilesList = document.getElementById('attached-files-list');
const statusText = document.getElementById('status-text');
const quickBtns = document.querySelectorAll('.quick-btn');
const statsBtn = document.getElementById('stats-btn');
const settingsBtn = document.getElementById('settings-btn');
const metaverseBtn = document.getElementById('metaverse-btn');
const statsModal = document.getElementById('stats-modal');
const settingsModal = document.getElementById('settings-modal');
const modalCloses = document.querySelectorAll('.modal-close');
const topButtonsGroup = document.querySelector('.top-buttons-group');

// Web Search Mode state
let webSearchMode = false;

// Função para atualizar o texto do botão de modo web
function updateWebSearchButton() {
    if (!webSearchBtn) return;
    if (webSearchMode) {
        webSearchBtn.textContent = '🌐 Modo Web: ON';
        webSearchBtn.classList.add('active');
    } else {
        webSearchBtn.textContent = '🌐 Modo Web: OFF';
        webSearchBtn.classList.remove('active');
    }
}

// Event listener for web search toggle
if (webSearchBtn) {
    webSearchBtn.addEventListener('click', async () => {
        try {
            webSearchMode = !webSearchMode;
            updateWebSearchButton();

            const statusElement = document.getElementById('status-text');
            const statusIcon = document.querySelector('.status-icon');

            if (statusElement) {
                statusElement.className = 'status-text';
                statusElement.textContent = webSearchMode
                    ? 'Modo Web ativado'
                    : 'Modo Web desativado';
            }

            if (statusIcon) {
                statusIcon.className = 'status-icon ' + (webSearchMode ? 'status-online' : 'status-offline');
            }

            if (webSearchMode) {
                await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: 'web on',
                        history: []
                    })
                }).catch(err => console.error('Erro ao ativar modo web:', err));
            } else {
                await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: 'web off',
                        history: []
                    })
                }).catch(err => console.error('Erro ao desativar modo web:', err));
            }
        } catch (error) {
            console.error('Erro ao alternar o modo web:', error);
        }
    });
}

// Attached Files State
let attachedFiles = [];

// Atualiza o texto de status
function updateStatus(status, message) {
    const statusIcon = document.querySelector('.status-icon');
    const statusText = document.querySelector('.status-text');
    
    if (!statusIcon || !statusText) return;
    
    statusIcon.className = 'status-icon';
    statusText.className = 'status-text';

    if (status === 'online') {
        statusIcon.classList.add('status-online');
        statusText.textContent = 'Online';
    } else if (status === 'typing') {
        statusIcon.classList.add('status-typing');
        statusText.textContent = message || 'Sofia está pensando...';
    } else if (status === 'connecting') {
        statusIcon.classList.add('status-connecting');
        statusText.textContent = message || 'Conectando...';
    } else if (status === 'error') {
        statusIcon.classList.add('status-error');
        statusText.textContent = message || 'Erro de conexão';
    }
}

// Function to add message to chat
function addMessage(sender, text, options = {}) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender + '-message');

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble');

    if (options.isSystem) {
        messageElement.classList.add('system-message');
    }

    if (options.includesFiles) {
        messageElement.classList.add('message-with-files');
    }

    const messageText = document.createElement('div');
    messageText.classList.add('message-text');

    // Parse markdown-like formatting
    const formattedText = formatMessageText(text);
    messageText.innerHTML = formattedText;

    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.classList.add('message-timestamp');
    const now = new Date();
    timestamp.textContent = now.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });

    messageBubble.appendChild(messageText);
    messageBubble.appendChild(timestamp);
    messageElement.appendChild(messageBubble);
    chatContainer.appendChild(messageElement);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Simple markdown-like formatting
function formatMessageText(text) {
    let formatted = text;

    // Headers (#, ##, ###)
    formatted = formatted.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold (**text** or __text__)
    formatted = formatted.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/gim, '<strong>$1</strong>');

    // Italic (*text* or _text_)
    formatted = formatted.replace(/\*(.*?)\*/gim, '<em>$1</em>');
    formatted = formatted.replace(/_(.*?)_/gim, '<em>$1</em>');

    // Inline code (`code`)
    formatted = formatted.replace(/`([^`]+)`/gim, '<code>$1</code>');

    // Code blocks (```code```)
    formatted = formatted.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>');

    // Links [text](url)
    formatted = formatted.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/gim,
        '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );

    // New lines
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted.trim();
}

// Input auto resize
if (messageInput) {
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        const maxHeight = 120; // 6 lines aprox
        messageInput.style.height = Math.min(messageInput.scrollHeight, maxHeight) + 'px';
    });
}

// Send message with Enter
if (messageInput) {
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// Event listeners
if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
}

// File input change
if (fileInputChat) {
    fileInputChat.addEventListener('change', handleFileSelection);
}

// Attach button
if (attachBtn) {
    attachBtn.addEventListener('click', () => {
        if (fileInputChat) fileInputChat.click();
    });
}

// Quick action buttons
if (quickBtns) {
    quickBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.getAttribute('data-action');
            handleQuickAction(action);
        });
    });
}

// Stats button
if (statsBtn && statsModal) {
    statsBtn.addEventListener('click', () => {
        statsModal.classList.add('show');
        loadStats();
    });
}

// Settings button
if (settingsBtn && settingsModal) {
    settingsBtn.addEventListener('click', () => {
        settingsModal.classList.add('show');
    });
}

// Metaverse button
if (metaverseBtn) {
    metaverseBtn.addEventListener('click', () => {
        abrirMetaverso();
    });
}

// Modal close buttons
if (modalCloses) {
    modalCloses.forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            if (modal) modal.classList.remove('show');
        });
    });
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === statsModal) {
        statsModal.classList.remove('show');
    }
    if (e.target === settingsModal) {
        settingsModal.classList.remove('show');
    }
});

// Show welcome message
function showWelcomeMessage() {
    const welcomeMessage = `
        <div class="welcome-message">
            <h2>🌸 Bem-vindo à Sofia</h2>
            <p>Sou sua assistente virtual, pronta para te ajudar com estudos, dúvidas e reflexões.</p>
            <p>Você pode:</p>
            <ul>
                <li>💬 Fazer perguntas diretas</li>
                <li>📎 Enviar arquivos (PDF, imagens, etc.)</li>
                <li>🌐 Ativar o modo Web para buscas em tempo real</li>
            </ul>
            <p><strong>Dica:</strong> Comece perguntando: <em>"Sofia, me ajude a estudar [tema]"</em>.</p>
        </div>
    `;
    const messageElement = document.createElement('div');
    messageElement.innerHTML = welcomeMessage;
    chatContainer.appendChild(messageElement);
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    showWelcomeMessage();
    await initializeWebSocket();
});

// Função para criar sessão
async function createSession() {
    try {
        const response = await fetch(`${API_URL}/api/session/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_name: 'Usuario'
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao criar sessão');
        }

        const data = await response.json();
        sessionId = data.session_id;
        console.log('🆔 Sessão criada:', sessionId);
    } catch (error) {
        console.error('Erro ao criar sessão:', error);
        showNotification('Erro ao criar sessão com o servidor.', 'error');
    }
}

// Initialize WebSocket
async function initializeWebSocket() {
    if (!sessionId) {
        await createSession();
    }

    if (!sessionId) {
        console.error('Não foi possível criar sessão para o WebSocket.');
        updateStatus('error', 'Erro ao conectar');
        return;
    }

    const wsUrl = `${WS_URL}/ws/chat/${sessionId}`;
    console.log('🔌 Conectando WebSocket em:', wsUrl);
    updateStatus('connecting', 'Conectando...');

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ WebSocket conectado!');
        isConnected = true;
        reconnectAttempts = 0;
        updateStatus('online', 'Online');

        // Processar mensagens na fila
        while (messageQueue.length > 0 && ws.readyState === WebSocket.OPEN) {
            const msg = messageQueue.shift();
            console.log('📨 Enviando mensagem em fila:', msg);
            ws.send(JSON.stringify(msg));
        }
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('📥 Recebido do WS:', data);

            if (data.type === 'status') {
                if (data.status === 'thinking') {
                    updateStatus('typing', data.message || 'Sofia está pensando...');
                } else if (data.status === 'idle') {
                    updateStatus('online', 'Online');
                }
                return;
            }

            if (data.type === 'message') {
                const resposta = data.content || data.response || '';
                addMessage('assistant', resposta);
                updateStatus('online', 'Online');
                return;
            }

            if (data.type === 'error') {
                const errMsg = data.message || 'Erro interno da Sofia.';
                addMessage('assistant', `⚠️ ${errMsg}`, { isSystem: true });
                updateStatus('error', 'Erro de processamento');
                return;
            }

            // Fallback: se não tiver type, trata como mensagem normal
            if (!data.type && (data.response || data.content)) {
                const resposta = data.response || data.content;
                addMessage('assistant', resposta);
                updateStatus('online', 'Online');
                return;
            }
        } catch (error) {
            console.error('Erro ao processar mensagem WebSocket:', error);
            addMessage('assistant', '⚠️ Erro ao processar resposta da Sofia.', {
                isSystem: true
            });
        }
    };

    ws.onclose = () => {
        console.log('⚠️ WebSocket fechado.');
        isConnected = false;
        updateStatus('error', 'Desconectado');
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(() => {
                console.log(`Tentando reconectar... (tentativa ${reconnectAttempts})`);
                initializeWebSocket();
            }, reconnectDelay);
        } else {
            console.log('Número máximo de tentativas de reconexão atingido.');
        }
    };

    ws.onerror = (error) => {
        console.error('Erro no WebSocket:', error);
        updateStatus('error', 'Erro de conexão');
    };
}

// Função para enviar mensagem
async function sendMessage() {
    const message = messageInput.value.trim();

    // Permite enviar só arquivos sem texto
    if (!message && attachedFiles.length === 0) return;

    // Cria mensagem a exibir (inclui info de arquivos)
    let displayMessage = message || '';
    if (attachedFiles.length > 0) {
        const filesInfo = attachedFiles.map(f => `📎 ${f.name}`).join('\n');
        displayMessage = displayMessage ? `${displayMessage}\n\n${filesInfo}` : filesInfo;
    }

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Remove welcome message if exists
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();

    // Add user message (com indicação de arquivos)
    addMessage('user', displayMessage);

    // Limpa anexos da UI
    const tempAttachedFiles = [...attachedFiles];
    attachedFiles = [];
    updateAttachedFilesUI();

    try {
        // Prepara mensagem incluindo contexto dos arquivos
        let fullMessage = message || 'Veja os arquivos que enviei.';

        // Enviar via WebSocket
        const wsMessage = {
            type: 'message',
            content: fullMessage,
            user_name: 'Usuário',
            web_search_mode: webSearchMode  // Incluir estado do modo web
        };

        console.log('📤 Tentando enviar:', wsMessage);
        console.log('🌐 Modo Web:', webSearchMode);
        console.log('🔌 WebSocket state:', ws ? ws.readyState : 'NULL');
        console.log('✅ isConnected:', isConnected);

        if (isConnected && ws.readyState === WebSocket.OPEN) {
            console.log('📨 Enviando via WebSocket...');
            ws.send(JSON.stringify(wsMessage));
            console.log('✅ Mensagem enviada!');
        } else {
            console.log('⚠️ WebSocket não conectado, adicionando à fila');
            // Adicionar à fila se não conectado
            messageQueue.push(wsMessage);
            showNotification('Mensagem enviada. Aguardando conexão...', 'warning');
            updateStatus('connecting', 'Reconectando...');
            if (!isConnected) {
                initializeWebSocket();
            }
        }

        // Upload de arquivos (se houver)
        if (tempAttachedFiles.length > 0) {
            await uploadFiles(tempAttachedFiles);
        }

        updateStatus('typing', 'Sofia está pensando...');
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        addMessage('assistant', '⚠️ Ocorreu um erro ao enviar sua mensagem.', {
            isSystem: true
        });
        updateStatus('error', 'Erro ao enviar');
    }
}

// Upload de arquivos
async function uploadFiles(files) {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    try {
        const response = await fetch(`${API_URL}/api/upload-files`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Erro ao enviar arquivos');
        }

        const data = await response.json();
        console.log('Arquivos enviados:', data);

        if (data.extracted_texts && Array.isArray(data.extracted_texts)) {
            const summary = data.extracted_texts
                .map((t, i) => `📎 Arquivo ${i + 1}:\n${t.substring(0, 500)}...`)
                .join('\n\n');

            addMessage('assistant', `📚 Li os arquivos que você enviou. Aqui vai um resumo inicial:\n\n${summary}`);
        } else {
            addMessage('assistant', '📎 Arquivos recebidos! Eles já estão disponíveis para análise nas próximas respostas.');
        }
    } catch (error) {
        console.error('Erro ao enviar arquivos:', error);
        addMessage('assistant', '⚠️ Ocorreu um erro ao enviar seus arquivos.', {
            isSystem: true
        });
    }
}

// Seleção de arquivos
function handleFileSelection(event) {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    attachedFiles = [...attachedFiles, ...files];
    updateAttachedFilesUI();
}

// Atualiza a UI dos arquivos anexados
function updateAttachedFilesUI() {
    if (!attachedFilesPreview || !attachedFilesList) return;

    if (attachedFiles.length === 0) {
        attachedFilesPreview.style.display = 'none';
        attachedFilesList.innerHTML = '';
        return;
    }

    attachedFilesPreview.style.display = 'block';
    attachedFilesList.innerHTML = '';

    attachedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.classList.add('attached-file-item');

        const fileInfo = document.createElement('span');
        fileInfo.textContent = `📎 ${file.name}`;

        const removeBtn = document.createElement('button');
        removeBtn.classList.add('remove-file-btn');
        removeBtn.textContent = '×';
        removeBtn.addEventListener('click', () => {
            attachedFiles.splice(index, 1);
            updateAttachedFilesUI();
        });

        fileItem.appendChild(fileInfo);
        fileItem.appendChild(removeBtn);
        attachedFilesList.appendChild(fileItem);
    });
}

// Quick actions
async function handleQuickAction(action) {
    try {
        const response = await fetch(`${API_URL}/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action })
        });

        const data = await response.json();

        if (data.response) {
            addMessage('assistant', data.response);
        } else {
            addMessage('assistant', '⚠️ Não foi possível executar a ação rápida.', {
                isSystem: true
            });
        }
    } catch (error) {
        console.error('Erro ao executar ação rápida:', error);
        addMessage('assistant', '⚠️ Ocorreu um erro ao executar a ação rápida.', {
            isSystem: true
        });
    }
}

// Carregar estatísticas da memória
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`, {
            method: 'GET'
        });

        const data = await response.json();

        if (data && data.memoria) {
            const statsContent = document.getElementById('stats-content');
            if (statsContent) {
                statsContent.innerHTML = `
                    <p><strong>Total de conversas:</strong> ${data.memoria.total_conversas || 0}</p>
                    <p><strong>Total de mensagens:</strong> ${data.memoria.total_mensagens || 0}</p>
                    <p><strong>Último acesso:</strong> ${data.memoria.ultimo_acesso || 'N/A'}</p>
                    <p><strong>Primeiro acesso:</strong> ${data.memoria.primeiro_acesso || 'N/A'}</p>
                    <p><strong>Versão da Sofia:</strong> ${data.versao || 'N/A'}</p>
                `;
            }
        } else {
            addMessage('assistant', '⚠️ Não foi possível carregar as estatísticas da memória.', {
                isSystem: true
            });
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        addMessage('assistant', '⚠️ Ocorreu um erro ao carregar as estatísticas.', {
            isSystem: true
        });
    }
}

// Abrir Metaverso em nova aba
function abrirMetaverso() {
    window.open('metaverse.html', '_blank');
}

// Conversas salvas
const conversationsList = document.getElementById('conversations-list');
const searchConversationsInput = document.getElementById('search-conversations');

if (conversationsList) {
    loadConversationsList();
}

// Função para carregar lista de conversas
async function loadConversationsList(searchTerm = '') {
    if (!conversationsList) return;

    try {
        conversationsList.innerHTML = '<div class="loading">Carregando conversas...</div>';

        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ termo: searchTerm, limite: 50 })
        });

        const data = await response.json();

        if (data.resultados && data.resultados.length > 0) {
            conversationsList.innerHTML = '';

            data.resultados.forEach((conv, index) => {
                const item = document.createElement('div');
                item.className = 'conversation-item';

                const title = document.createElement('div');
                title.className = 'conversation-title';
                title.textContent = `${conv.data || 'Data desconhecida'} - ${conv.preview || 'Sem título'}`;

                const preview = document.createElement('div');
                preview.className = 'conversation-preview';
                preview.textContent = conv.preview || '';

                item.appendChild(title);
                item.appendChild(preview);

                item.addEventListener('click', () => {
                    loadConversationDetail(index);
                });

                conversationsList.appendChild(item);
            });
        } else {
            conversationsList.innerHTML = '<div class="empty">Nenhuma conversa encontrada.</div>';
        }
    } catch (error) {
        console.error('Erro ao carregar lista de conversas:', error);
        conversationsList.innerHTML = '<div class="error">Erro ao carregar conversas.</div>';
    }
}

// Buscar conversas
if (searchConversationsInput) {
    searchConversationsInput.addEventListener('input', () => {
        const term = searchConversationsInput.value.trim();
        loadConversationsList(term);
    });
}

// Carregar detalhes da conversa
async function loadConversationDetail(index) {
    try {
        const response = await fetch(`${API_URL}/get-conversation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index })
        });

        const data = await response.json();

        if (data.conversa) {
            chatContainer.innerHTML = '';

            data.conversa.mensagens.forEach(msg => {
                addMessage(msg.remetente === 'sofia' ? 'assistant' : 'user', msg.texto || '');
            });
        } else {
            showNotification('⚠️ Não foi possível carregar a conversa selecionada.', 'warning');
        }
    } catch (error) {
        console.error('Erro ao carregar detalhes da conversa:', error);
        showNotification('❌ Erro ao carregar detalhes da conversa.', 'error');
    }
}

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// =========================
// Telemetria TRQ + Qwen
// =========================

const btnAtualizarTrq = document.getElementById('btn-atualizar-trq');
const btnOtimizarTrq = document.getElementById('btn-otimizar-trq');
const trqLogsEl = document.getElementById('trq-logs');
const trqQwenEl = document.getElementById('trq-qwen-sugestao');

async function carregarTelemetriaTRQ() {
    if (!trqLogsEl) return;

    trqLogsEl.textContent = 'Carregando telemetria...';

    try {
        const resp = await fetch(`${API_URL}/trq/logs`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!resp.ok) {
            throw new Error(`HTTP ${resp.status}`);
        }

        const data = await resp.json();
        const logs =
            data.logs ||
            data.conteudo ||
            data.mensagem ||
            JSON.stringify(data, null, 2);

        trqLogsEl.textContent = logs || 'Nenhum dado de execução encontrado.';
        showNotification('✅ Telemetria TRQ atualizada.', 'success');
    } catch (error) {
        console.error('Erro ao carregar telemetria TRQ:', error);
        trqLogsEl.textContent =
            'Erro ao carregar telemetria. Verifique se o serviço TRQ/Qwen está rodando.';
        showNotification('❌ Erro ao carregar telemetria TRQ.', 'error');
    }
}

async function rodarOtimizacaoQwen() {
    if (!trqQwenEl) return;

    trqQwenEl.textContent = 'Executando Qwen e gerando sugestão...';

    try {
        const resp = await fetch(`${API_URL}/trq/qwen-optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        if (!resp.ok) {
            throw new Error(`HTTP ${resp.status}`);
        }

        const data = await resp.json();

        const sugestao =
            data.sugestao ||
            data.sugestao_qwen ||
            data.response ||
            JSON.stringify(data, null, 2);

        if (data.logs && trqLogsEl) {
            trqLogsEl.textContent = data.logs;
        }

        trqQwenEl.textContent = sugestao || 'Qwen não retornou sugestão.';
        showNotification('✅ Sugestão do Qwen gerada.', 'success');
    } catch (error) {
        console.error('Erro ao rodar Qwen:', error);
        trqQwenEl.textContent =
            'Erro ao executar Qwen. Verifique se o serviço Qwen está ativo.';
        showNotification('❌ Erro ao rodar Qwen (otimização).', 'error');
    }
}

if (btnAtualizarTrq) {
    btnAtualizarTrq.addEventListener('click', carregarTelemetriaTRQ);
}

if (btnOtimizarTrq) {
    btnOtimizarTrq.addEventListener('click', rodarOtimizacaoQwen);
}
