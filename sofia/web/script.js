// API Configuration
const API_URL = 'https://a9948c416851.ngrok-free.app';
const WS_URL = 'wss://a9948c416851.ngrok-free.app';

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
const metaverseModal = document.getElementById('metaverse-modal');

// Initialize
let conversationHistory = [];
let attachedFiles = []; // Array para armazenar arquivos anexados temporariamente
let webSearchMode = false; // Estado do modo de busca web

// Inicializar WebSocket ao carregar
document.addEventListener('DOMContentLoaded', async () => {
    await initializeWebSocket();
});

// FunÃ§Ã£o para criar sessÃ£o
async function createSession() {
    try {
        const response = await fetch(`${API_URL}/api/session/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_name: 'UsuÃ¡rio'
            })
        });

        if (!response.ok) {
            throw new Error('Falha ao criar sessÃ£o');
        }

        const data = await response.json();
        sessionId = data.session_id;
        console.log('SessÃ£o criada:', sessionId);
        return sessionId;
    } catch (error) {
        console.error('Erro ao criar sessÃ£o:', error);
        updateStatus('connecting', 'Pensando...');
        throw error;
    }
}

// FunÃ§Ã£o para inicializar WebSocket
async function initializeWebSocket() {
    try {
        await createSession();
        connectWebSocket();
    } catch (error) {
        console.error('Erro ao inicializar:', error);
        updateStatus('connecting', 'Pensando...');
    }
}

// FunÃ§Ã£o para conectar WebSocket
function connectWebSocket() {
    if (!sessionId) {
        console.error('Session ID nÃ£o disponÃ­vel');
        return;
    }

    updateStatus('connecting', 'Conectando...');

    try {
        ws = new WebSocket(`${WS_URL}/ws/${sessionId}`);

        ws.onopen = () => {
            console.log('WebSocket conectado');
            isConnected = true;
            reconnectAttempts = 0;
            updateStatus('connected', 'Online');
            processMessageQueue();
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('Erro ao processar mensagem:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket erro:', error);
            updateStatus('connecting', 'Pensando...');
        };

        ws.onclose = () => {
            console.log('WebSocket desconectado');
            isConnected = false;
            updateStatus('connecting', 'Pensando...');
            attemptReconnect();
        };
    } catch (error) {
        console.error('Erro ao criar WebSocket:', error);
        updateStatus('connecting', 'Pensando...');
    }
}

// FunÃ§Ã£o para tentar reconexÃ£o
function attemptReconnect() {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        console.log(`Tentativa de reconexÃ£o ${reconnectAttempts}/${maxReconnectAttempts}`);
        updateStatus('connecting', 'Pensando...');
        
        setTimeout(() => {
            connectWebSocket();
        }, reconnectDelay * reconnectAttempts);
    } else {
        updateStatus('connecting', 'Pensando...');
        // Continua tentando apÃ³s delay maior
        setTimeout(() => {
            reconnectAttempts = 0;
            attemptReconnect();
        }, 5000);
    }
}

// Processar fila de mensagens
function processMessageQueue() {
    while (messageQueue.length > 0 && isConnected && ws.readyState === WebSocket.OPEN) {
        const message = messageQueue.shift();
        try {
            ws.send(JSON.stringify(message));
        } catch (error) {
            console.error('Erro ao processar fila:', error);
            messageQueue.unshift(message);
            break;
        }
    }
}

// Tratar mensagens do WebSocket
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'system':
            console.log('Sistema:', data.content);
            break;
        
        case 'ack':
            console.log('Ack:', data.content);
            showTypingIndicator();
            break;
        
        case 'response':
            hideTypingIndicator();
            addMessage('sofia', data.content);
            
            // Se estiver no metaverso, tambÃ©m adicionar lÃ¡
            const metaverseModal = document.getElementById('metaverse-modal');
            if (metaverseModal && metaverseModal.classList.contains('active')) {
                const messagesContainer = document.getElementById('metaverse-messages');
                const statusDiv = document.getElementById('metaverse-status');
                
                if (messagesContainer) {
                    // Remover mensagem temporÃ¡ria de "processando"
                    const tempMsg = document.getElementById('temp-processing-msg');
                    if (tempMsg) {
                        tempMsg.remove();
                    }
                    
                    // Ocultar status
                    if (statusDiv) {
                        statusDiv.classList.remove('active');
                    }
                    
                    // Adicionar resposta real
                    const sofiaMsg = document.createElement('div');
                    sofiaMsg.className = 'metaverse-message sofia';
                    sofiaMsg.textContent = 'ðŸŒ¸ ' + data.content;
                    messagesContainer.appendChild(sofiaMsg);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                    // Animar avatar de Sofia no metaverso
                    const sofiaAvatar = document.querySelector('.sofia-avatar-3d');
                    if (sofiaAvatar) {
                        sofiaAvatar.style.transform = 'scale(1.1)';
                        setTimeout(() => {
                            sofiaAvatar.style.transform = '';
                        }, 300);
                    }
                }
            }
            
            // Adicionar ao histÃ³rico
            conversationHistory.push(
                { de: 'Sofia', texto: data.content }
            );
            break;
        
        case 'cancelled':
            hideTypingIndicator();
            console.log('â¹ï¸ Processamento cancelado:', data.content);
            showNotification(data.content, 'warning');
            break;
        
        case 'error':
            hideTypingIndicator();
            showNotification(data.content, 'error');
            break;
        
        default:
            console.log('Mensagem desconhecida:', data);
    }
}

// Atualizar status de conexÃ£o
function updateStatus(status, text) {
    const statusElement = document.querySelector('.status');
    const statusTextElement = document.getElementById('status-text');
    
    if (statusElement) {
        statusElement.className = `status ${status}`;
    }
    
    if (statusTextElement) {
        statusTextElement.textContent = text;
    }
}

// Indicador de digitaÃ§Ã£o
function showTypingIndicator() {
    const existingIndicator = document.querySelector('.typing-indicator');
    if (!existingIndicator) {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <span style="margin-left: 10px;">Sofia estÃ¡ digitando...</span>
        `;
        chatContainer.appendChild(indicator);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

function hideTypingIndicator() {
    const indicator = document.querySelector('.typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);

// Web Search Button
webSearchBtn.addEventListener('click', toggleWebSearchMode);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Attach button
attachBtn.addEventListener('click', () => {
    fileInputChat.click();
});

fileInputChat.addEventListener('change', async (e) => {
    const files = Array.from(e.target.files);
    for (const file of files) {
        await addAttachedFile(file);
    }
    fileInputChat.value = ''; // Reset
    updateAttachedFilesUI();
});

// Auto-resize textarea
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
});

// Quick Actions
quickBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        handleQuickAction(action);
    });
});

// Modal Controls
statsBtn.addEventListener('click', () => openModal('stats'));
settingsBtn.addEventListener('click', () => openSettingsModal());
metaverseBtn.addEventListener('click', () => {
    metaverseModal.classList.add('active');
    // Inicializar metaverso Babylon.js
    if (typeof initMetaverse === 'function') {
        setTimeout(() => initMetaverse(), 100);
    }
});

// Input do chat do metaverso
const metaverseInput = document.getElementById('metaverse-input-text');
const metaverseSendBtn = document.getElementById('metaverse-send-btn');

if (metaverseInput && metaverseSendBtn) {
    metaverseSendBtn.addEventListener('click', () => {
        const message = metaverseInput.value.trim();
        if (message && typeof sendMetaverseMessage === 'function') {
            sendMetaverseMessage(message);
            metaverseInput.value = '';
        }
    });

    metaverseInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            metaverseSendBtn.click();
        }
    });
}

document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => {
        closeModals();
        // Fechar metaverso se estiver aberto
        if (metaverseModal && metaverseModal.classList.contains('active')) {
            if (typeof closeMetaverse === 'function') {
                closeMetaverse();
            }
        }
    });
});

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModals();
    });
});

// Functions
async function addAttachedFile(file) {
    // Verifica se jÃ¡ tem 10 arquivos
    if (attachedFiles.length >= 10) {
        showNotification('âŒ Limite de 10 arquivos atingido', 'error');
        return;
    }
    
    // Verifica tamanho (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showNotification(`âŒ ${file.name} muito grande (mÃ¡x 10MB)`, 'error');
        return;
    }
    
    // Verifica formato
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
        showNotification(`âŒ Formato nÃ£o suportado: ${file.name}`, 'error');
        return;
    }
    
    // Upload para o servidor
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_URL}/upload-file`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            attachedFiles.push({
                id: data.arquivo_id,
                name: file.name,
                type: data.tipo,
                file: file
            });
            showNotification(`âœ… ${file.name} anexado!`);
        } else {
            showNotification(`âŒ ${data.erro}`, 'error');
        }
    } catch (error) {
        showNotification(`âŒ Erro ao anexar ${file.name}`, 'error');
    }
}

function updateAttachedFilesUI() {
    if (attachedFiles.length === 0) {
        attachedFilesPreview.style.display = 'none';
        attachBtn.classList.remove('has-files');
        return;
    }
    
    attachedFilesPreview.style.display = 'block';
    attachBtn.classList.add('has-files');
    
    attachedFilesList.innerHTML = attachedFiles.map((file, index) => `
        <div class="attached-file-item">
            <span class="attached-file-icon">${file.type === 'imagem' ? 'ðŸ–¼ï¸' : 'ðŸ“„'}</span>
            <span class="attached-file-name" title="${file.name}">${file.name}</span>
            <button class="attached-file-remove" onclick="removeAttachedFile(${index})">âœ•</button>
        </div>
    `).join('');
}

function removeAttachedFile(index) {
    const file = attachedFiles[index];
    
    // Remove do servidor
    fetch(`${API_URL}/delete-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ arquivo_id: file.id })
    }).catch(err => console.error('Erro ao remover arquivo:', err));
    
    // Remove da lista local
    attachedFiles.splice(index, 1);
    updateAttachedFilesUI();
}

// Toggle Web Search Mode
function toggleWebSearchMode() {
    webSearchMode = !webSearchMode;
    
    if (webSearchMode) {
        webSearchBtn.classList.add('active');
        webSearchBtn.title = 'Modo Web ATIVO - Clique para desativar';
        showNotification('ðŸŒ Modo Web ATIVADO - Sofia buscarÃ¡ na internet');
        
        // Envia comando para ativar no backend
        fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: 'web on',
                history: []
            })
        }).catch(err => console.error('Erro ao ativar modo web:', err));
    } else {
        webSearchBtn.classList.remove('active');
        webSearchBtn.title = 'Buscar na Web';
        showNotification('ðŸŒ Modo Web DESATIVADO');
        
        // Envia comando para desativar no backend
        fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: 'web off',
                history: []
            })
        }).catch(err => console.error('Erro ao desativar modo web:', err));
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    
    // Permite enviar sÃ³ arquivos sem texto
    if (!message && attachedFiles.length === 0) return;

    // Cria mensagem a exibir (inclui info de arquivos)
    let displayMessage = message || '';
    if (attachedFiles.length > 0) {
        const filesInfo = attachedFiles.map(f => `ðŸ“Ž ${f.name}`).join('\n');
        displayMessage = displayMessage ? `${displayMessage}\n\n${filesInfo}` : filesInfo;
    }

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Remove welcome message if exists
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();

    // Add user message (com indicaÃ§Ã£o de arquivos)
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
            user_name: 'UsuÃ¡rio',
            web_search_mode: webSearchMode  // Incluir estado do modo web
        };

        console.log('ðŸ“¤ Tentando enviar:', wsMessage);
        console.log('ðŸŒ Modo Web:', webSearchMode);
        console.log('ðŸ”Œ WebSocket state:', ws ? ws.readyState : 'NULL');
        console.log('âœ… isConnected:', isConnected);

        if (isConnected && ws.readyState === WebSocket.OPEN) {
            console.log('âœ‰ï¸ Enviando via WebSocket...');
            ws.send(JSON.stringify(wsMessage));
            console.log('âœ… Mensagem enviada!');
        } else {
            console.log('âš ï¸ WebSocket nÃ£o conectado, adicionando Ã  fila');
            // Adicionar Ã  fila se nÃ£o conectado
            messageQueue.push(wsMessage);
            showNotification('Mensagem enviada. Aguardando conexÃ£o...', 'warning');
            updateStatus('connecting', 'Pensando...');
        }
        
        // Update history
        conversationHistory.push(
            { de: 'UsuÃ¡rio', texto: message }
        );
    } catch (error) {
        hideTypingIndicator();
        addMessage('sofia', 'âŒ NÃ£o foi possÃ­vel enviar a mensagem. Tentando reconectar...');
        console.error('Erro:', error);
    }
}

function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'sofia' ? 'ðŸŒ¸' : 'ðŸ‘¤';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = formatMessage(text);

    // Criar container para hora + Ã­cones
    const timeContainer = document.createElement('div');
    timeContainer.className = 'message-time-container';

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    timeContainer.appendChild(time);

    // Adicionar Ã­cones de aÃ§Ã£o apenas para mensagens do usuÃ¡rio
    if (sender === 'user') {
        const iconsDiv = document.createElement('div');
        iconsDiv.className = 'message-icons';

        // Ãcone Stop
        const stopIcon = document.createElement('span');
        stopIcon.className = 'message-icon stop-icon';
        stopIcon.innerHTML = 'â¹ï¸';
        stopIcon.title = 'Parar resposta';
        stopIcon.onclick = () => stopResponse();

        // Ãcone Editar
        const editIcon = document.createElement('span');
        editIcon.className = 'message-icon edit-icon';
        editIcon.innerHTML = 'âœï¸';
        editIcon.title = 'Editar mensagem';
        editIcon.onclick = () => editMessage(messageDiv, text);

        iconsDiv.appendChild(stopIcon);
        iconsDiv.appendChild(editIcon);
        timeContainer.appendChild(iconsDiv);
    }

    content.appendChild(timeContainer);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function formatMessage(text) {
    // Simple markdown-like formatting
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

// FunÃ§Ã£o para parar a resposta da Sofia
function stopResponse() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        // Envia comando de stop para o servidor
        try {
            ws.send(JSON.stringify({
                type: 'stop',
                session_id: sessionId
            }));
        } catch (error) {
            console.error('Erro ao enviar comando de stop:', error);
        }
        
        // Fecha a conexÃ£o WebSocket para forÃ§ar interrupÃ§Ã£o
        ws.close();
        hideTypingIndicator();
        showNotification('â¹ï¸ Processamento interrompido', 'warning');
        
        // Reconecta apÃ³s 500ms
        setTimeout(() => {
            connectWebSocket();
        }, 500);
    } else {
        hideTypingIndicator();
        showNotification('â¹ï¸ Resposta cancelada', 'info');
    }
}

// FunÃ§Ã£o para editar mensagem do usuÃ¡rio
function editMessage(messageDiv, originalText) {
    // Remove o conteÃºdo formatado e mostra um textarea
    const contentDiv = messageDiv.querySelector('.message-content');
    const actionsDiv = contentDiv.querySelector('.message-actions');
    const timeDiv = contentDiv.querySelector('.message-time');
    
    // Cria textarea para ediÃ§Ã£o
    const textarea = document.createElement('textarea');
    textarea.className = 'edit-textarea';
    textarea.value = originalText;
    textarea.rows = 3;
    
    // Limpa o conteÃºdo atual
    contentDiv.innerHTML = '';
    contentDiv.appendChild(textarea);
    
    // Cria botÃµes de confirmaÃ§Ã£o
    const editActionsDiv = document.createElement('div');
    editActionsDiv.className = 'message-actions edit-actions';
    
    const saveBtn = document.createElement('button');
    saveBtn.className = 'message-action-btn save-btn';
    saveBtn.innerHTML = 'âœ… Salvar';
    saveBtn.onclick = () => saveEditedMessage(messageDiv, textarea.value, originalText);
    
    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'message-action-btn cancel-btn';
    cancelBtn.innerHTML = 'âŒ Cancelar';
    cancelBtn.onclick = () => cancelEdit(messageDiv, originalText);
    
    editActionsDiv.appendChild(saveBtn);
    editActionsDiv.appendChild(cancelBtn);
    contentDiv.appendChild(editActionsDiv);
    
    // Foca no textarea
    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
}

// Salvar mensagem editada e reenviar
function saveEditedMessage(messageDiv, newText, oldText) {
    if (!newText.trim()) {
        showNotification('âŒ A mensagem nÃ£o pode estar vazia', 'error');
        return;
    }
    
    // Primeiro, encontra e remove a resposta da Sofia se existir
    const allMessages = Array.from(chatContainer.querySelectorAll('.message'));
    const messageIndex = allMessages.indexOf(messageDiv);
    
    // Remove a resposta da Sofia que veio depois desta mensagem
    if (messageIndex !== -1 && messageIndex + 1 < allMessages.length) {
        const nextMessage = allMessages[messageIndex + 1];
        if (nextMessage.classList.contains('sofia')) {
            nextMessage.remove();
            
            // Remove do histÃ³rico de conversaÃ§Ã£o
            // Encontra e remove a resposta correspondente
            const lastSofiaResponse = conversationHistory.findIndex(
                (msg, idx) => idx > 0 && msg.de === 'Sofia' && 
                conversationHistory[idx - 1].texto === oldText
            );
            if (lastSofiaResponse !== -1) {
                conversationHistory.splice(lastSofiaResponse, 1);
            }
        }
    }
    
    // Remove a mensagem antiga do usuÃ¡rio
    messageDiv.remove();
    
    // Remove do histÃ³rico a mensagem antiga do usuÃ¡rio
    const oldMessageIndex = conversationHistory.findIndex(
        msg => msg.de === 'UsuÃ¡rio' && msg.texto === oldText
    );
    if (oldMessageIndex !== -1) {
        conversationHistory.splice(oldMessageIndex, 1);
    }
    
    // Atualiza o input com o novo texto
    messageInput.value = newText;
    
    // Envia a mensagem editada como uma nova pergunta
    sendMessage();
    
    showNotification('âœï¸ Mensagem reenviada', 'success');
}

// Cancelar ediÃ§Ã£o
function cancelEdit(messageDiv, originalText) {
    const contentDiv = messageDiv.querySelector('.message-content');
    
    // Restaura o conteÃºdo original
    contentDiv.innerHTML = formatMessage(originalText);
    
    // Recria container de hora + Ã­cones
    const timeContainer = document.createElement('div');
    timeContainer.className = 'message-time-container';

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    timeContainer.appendChild(time);
    
    // Recria os Ã­cones de aÃ§Ã£o
    const iconsDiv = document.createElement('div');
    iconsDiv.className = 'message-icons';
    
    const stopIcon = document.createElement('span');
    stopIcon.className = 'message-icon stop-icon';
    stopIcon.innerHTML = 'â¹ï¸';
    stopIcon.title = 'Parar resposta';
    stopIcon.onclick = () => stopResponse();
    
    const editIcon = document.createElement('span');
    editIcon.className = 'message-icon edit-icon';
    editIcon.innerHTML = 'âœï¸';
    editIcon.title = 'Editar mensagem';
    editIcon.onclick = () => editMessage(messageDiv, originalText);
    
    iconsDiv.appendChild(stopIcon);
    iconsDiv.appendChild(editIcon);
    timeContainer.appendChild(iconsDiv);
    
    contentDiv.appendChild(timeContainer);
}

function toggleWebSearchMode() {
    webSearchMode = !webSearchMode;
    webSearchBtn.classList.toggle('active', webSearchMode);
    const status = webSearchMode ? 'Modo Web Ativado' : 'Modo Web Desativado';
    showNotification(`ðŸŒ ${status}`, webSearchMode ? 'success' : 'info');
}

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

        if (data.result) {
            addMessage('sofia', data.result);
        }
    } catch (error) {
        addMessage('sofia', 'âŒ Erro ao executar aÃ§Ã£o.');
        console.error('Erro:', error);
    }
}

async function openModal(type) {
    const modal = statsModal;
    const contentEl = document.getElementById('stats-content');

    modal.classList.add('active');
    contentEl.innerHTML = '<div class="loading">Carregando estatÃ­sticas...</div>';

    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();

        contentEl.innerHTML = formatStats(data);
    } catch (error) {
        contentEl.innerHTML = '<div class="loading">âŒ Erro ao carregar estatÃ­sticas da memÃ³ria</div>';
        console.error('Erro ao carregar stats:', error);
    }
}

function closeModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
}

function formatStats(data) {
    const totalConversas = data.total_conversas || 0;
    const totalAprendizados = data.total_aprendizados || 0;
    const tamanhoMB = data.tamanho_mb || 0;
    const percentual = data.percentual || 0;
    const cache = data.cache || 0;
    const limiteGB = 5;
    
    // Calcular espaÃ§o disponÃ­vel
    const espacoUsadoGB = (tamanhoMB / 1024).toFixed(3);
    const espacoDisponivelGB = (limiteGB - parseFloat(espacoUsadoGB)).toFixed(3);
    
    // Determinar cor da barra de progresso
    let barColor = '#4CAF50'; // Verde
    if (percentual > 70) barColor = '#ff9800'; // Laranja
    if (percentual > 90) barColor = '#f44336'; // Vermelho
    
    return `
        <div class="stats-container">
            <!-- Resumo Principal -->
            <div class="stats-summary">
                <div class="stat-card">
                    <div class="stat-icon">ðŸ’¬</div>
                    <div class="stat-info">
                        <div class="stat-label">Conversas Salvas</div>
                        <div class="stat-value">${totalConversas.toLocaleString('pt-BR')}</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">ðŸ§ </div>
                    <div class="stat-info">
                        <div class="stat-label">Aprendizados</div>
                        <div class="stat-value">${totalAprendizados.toLocaleString('pt-BR')}</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">ðŸ”¢</div>
                    <div class="stat-info">
                        <div class="stat-label">Cache (RAM)</div>
                        <div class="stat-value">${cache.toLocaleString('pt-BR')}</div>
                        <div class="stat-sublabel">mensagens ativas</div>
                    </div>
                </div>
            </div>
            
            <!-- Uso de Armazenamento -->
            <div class="storage-section">
                <h4 style="margin: 1.5rem 0 1rem 0; color: var(--text-color); font-size: 1rem;">
                    ðŸ’¾ Armazenamento em Disco
                </h4>
                
                <div class="storage-info">
                    <div class="storage-row">
                        <span class="storage-label">EspaÃ§o Usado:</span>
                        <span class="storage-value">${tamanhoMB.toFixed(2)} MB (${espacoUsadoGB} GB)</span>
                    </div>
                    <div class="storage-row">
                        <span class="storage-label">EspaÃ§o DisponÃ­vel:</span>
                        <span class="storage-value">${espacoDisponivelGB} GB de ${limiteGB} GB</span>
                    </div>
                </div>
                
                <!-- Barra de Progresso -->
                <div class="progress-bar-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${percentual}%; background-color: ${barColor};">
                            <span class="progress-text">${percentual.toFixed(1)}%</span>
                        </div>
                    </div>
                    <div class="progress-labels">
                        <span>0%</span>
                        <span>50%</span>
                        <span>100%</span>
                    </div>
                </div>
                
                <!-- Detalhes de Uso -->
                <div class="usage-details">
                    <div class="usage-item">
                        <span class="usage-icon">ðŸ“</span>
                        <span class="usage-text">
                            <strong>MÃ©dia por conversa:</strong> 
                            ${totalConversas > 0 ? (tamanhoMB / totalConversas).toFixed(2) : 0} MB
                        </span>
                    </div>
                    <div class="usage-item">
                        <span class="usage-icon">ðŸ“ˆ</span>
                        <span class="usage-text">
                            <strong>Status:</strong> 
                            ${percentual < 50 ? 'âœ… SaudÃ¡vel' : percentual < 80 ? 'âš ï¸ Moderado' : 'ðŸ”´ CrÃ­tico'}
                        </span>
                    </div>
                </div>
            </div>
            
            <!-- RecomendaÃ§Ãµes -->
            ${percentual > 70 ? `
            <div class="recommendations">
                <h4 style="margin: 1.5rem 0 1rem 0; color: #ff9800; font-size: 1rem;">
                    âš ï¸ RecomendaÃ§Ãµes
                </h4>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    ${percentual > 90 ? '<li style="padding: 0.5rem; margin: 0.25rem 0; background: rgba(244, 67, 54, 0.1); border-left: 3px solid #f44336; border-radius: 4px;">ðŸ”´ EspaÃ§o crÃ­tico! Limpe conversas antigas urgentemente.</li>' : ''}
                    ${percentual > 70 && percentual <= 90 ? '<li style="padding: 0.5rem; margin: 0.25rem 0; background: rgba(255, 152, 0, 0.1); border-left: 3px solid #ff9800; border-radius: 4px;">âš ï¸ Considere limpar conversas antigas nas ConfiguraÃ§Ãµes.</li>' : ''}
                    <li style="padding: 0.5rem; margin: 0.25rem 0; background: rgba(33, 150, 243, 0.1); border-left: 3px solid #2196F3; border-radius: 4px;">ðŸ’¡ Use o botÃ£o âš™ï¸ ConfiguraÃ§Ãµes â†’ Limpeza para liberar espaÃ§o.</li>
                </ul>
            </div>
            ` : ''}
            
            <!-- Footer com timestamp -->
            <div class="stats-footer">
                <small style="color: var(--text-muted);">
                    Atualizado em ${new Date().toLocaleString('pt-BR')}
                </small>
            </div>
        </div>
        
        <style>
            .stats-container {
                padding: 0.5rem;
            }
            
            .stats-summary {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin-bottom: 1.5rem;
            }
            
            .stat-card {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1rem;
                background: linear-gradient(135deg, rgba(103, 58, 183, 0.1), rgba(103, 58, 183, 0.05));
                border-radius: 12px;
                border: 1px solid rgba(103, 58, 183, 0.2);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(103, 58, 183, 0.2);
            }
            
            .stat-icon {
                font-size: 2rem;
                opacity: 0.9;
            }
            
            .stat-info {
                flex: 1;
            }
            
            .stat-label {
                font-size: 0.75rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.25rem;
            }
            
            .stat-value {
                font-size: 1.75rem;
                font-weight: bold;
                color: var(--primary-color);
                line-height: 1;
            }
            
            .stat-sublabel {
                font-size: 0.7rem;
                color: var(--text-muted);
                margin-top: 0.25rem;
            }
            
            .storage-section {
                background: rgba(0, 0, 0, 0.2);
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 1rem;
            }
            
            .storage-info {
                margin-bottom: 1.5rem;
            }
            
            .storage-row {
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            
            .storage-row:last-child {
                border-bottom: none;
            }
            
            .storage-label {
                color: var(--text-muted);
                font-size: 0.9rem;
            }
            
            .storage-value {
                color: var(--text-color);
                font-weight: 600;
                font-size: 0.9rem;
            }
            
            .progress-bar-container {
                margin: 1rem 0;
            }
            
            .progress-bar {
                width: 100%;
                height: 32px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 16px;
                overflow: hidden;
                position: relative;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            
            .progress-fill {
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: width 0.6s ease, background-color 0.3s ease;
                position: relative;
                border-radius: 16px;
            }
            
            .progress-text {
                font-size: 0.85rem;
                font-weight: bold;
                color: white;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
                z-index: 1;
            }
            
            .progress-labels {
                display: flex;
                justify-content: space-between;
                margin-top: 0.5rem;
                font-size: 0.75rem;
                color: var(--text-muted);
            }
            
            .usage-details {
                margin-top: 1rem;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }
            
            .usage-item {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.75rem;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                border-left: 3px solid var(--primary-color);
            }
            
            .usage-icon {
                font-size: 1.25rem;
            }
            
            .usage-text {
                font-size: 0.9rem;
                color: var(--text-color);
            }
            
            .recommendations {
                background: rgba(255, 152, 0, 0.05);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid rgba(255, 152, 0, 0.2);
            }
            
            .stats-footer {
                text-align: center;
                margin-top: 1.5rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
        </style>
    `;
}

// Check API status on load
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_URL}/status`);
        if (response.ok) {
            statusText.textContent = 'Online';
        } else {
            statusText.textContent = 'Pensando...';
        }
    } catch (error) {
        statusText.textContent = 'Pensando...';
        console.error('API nÃ£o estÃ¡ respondendo');
    }
}

// Initialize
checkAPIStatus();
setInterval(checkAPIStatus, 30000); // Check every 30 seconds
loadPreferences();

// ========== SETTINGS MODAL FUNCTIONS ==========

function openSettingsModal() {
    settingsModal.classList.add('active');
    loadConversationsList();
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active from all tabs and contents
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Add active to clicked tab
        btn.classList.add('active');
        const tabId = btn.dataset.tab;
        document.getElementById(tabId).classList.add('active');
        
        // Load data for specific tabs
        if (tabId === 'memory-tab') {
            loadConversationsList();
        }
    });
});

// Load conversations list
async function loadConversationsList() {
    const listEl = document.getElementById('conversations-list');
    listEl.innerHTML = '<div class="loading">Carregando conversas...</div>';
    
    try {
        const response = await fetch(`${API_URL}/conversations`);
        const data = await response.json();
        
        if (data.conversas && data.conversas.length > 0) {
            listEl.innerHTML = '';
            data.conversas.forEach((conv) => {
                const item = document.createElement('div');
                item.className = 'conversation-item';
                const absoluteIndex = conv._index !== undefined ? conv._index : 0;
                item.innerHTML = `
                    <div class="conversation-info">
                        <div class="conversation-text">
                            <strong>${conv.de}:</strong> ${conv.texto.substring(0, 80)}${conv.texto.length > 80 ? '...' : ''}
                        </div>
                        <div class="conversation-meta">
                            ${conv.timestamp ? new Date(conv.timestamp).toLocaleString('pt-BR') : 'Sem data'}
                        </div>
                    </div>
                    <div class="conversation-actions">
                        <button class="btn-icon" onclick="deleteConversation(${absoluteIndex})" title="Deletar">
                            ðŸ—‘ï¸
                        </button>
                    </div>
                `;
                listEl.appendChild(item);
            });
        } else {
            listEl.innerHTML = '<p class="text-muted">Nenhuma conversa salva ainda.</p>';
        }
    } catch (error) {
        listEl.innerHTML = '<p class="text-muted">âŒ Erro ao carregar conversas</p>';
        console.error('Erro:', error);
    }
}

// Search conversations
document.getElementById('search-btn').addEventListener('click', async () => {
    const searchTerm = document.getElementById('search-conversations').value.trim();
    if (!searchTerm) {
        loadConversationsList();
        return;
    }
    
    const listEl = document.getElementById('conversations-list');
    listEl.innerHTML = '<div class="loading">Buscando...</div>';
    
    try {
        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ termo: searchTerm, limite: 50 })
        });
        
        const data = await response.json();
        
        if (data.resultados && data.resultados.length > 0) {
            listEl.innerHTML = '';
            data.resultados.forEach((conv) => {
                const item = document.createElement('div');
                item.className = 'conversation-item';
                item.innerHTML = `
                    <div class="conversation-info">
                        <div class="conversation-text">
                            <strong>${conv.de}:</strong> ${conv.texto.substring(0, 80)}${conv.texto.length > 80 ? '...' : ''}
                        </div>
                        <div class="conversation-meta">
                            ${conv.timestamp ? new Date(conv.timestamp).toLocaleString('pt-BR') : 'Sem data'}
                        </div>
                    </div>
                `;
                listEl.appendChild(item);
            });
        } else {
            listEl.innerHTML = `<p class="text-muted">Nenhuma conversa encontrada com "${searchTerm}"</p>`;
        }
    } catch (error) {
        listEl.innerHTML = '<p class="text-muted">âŒ Erro ao buscar</p>';
        console.error('Erro:', error);
    }
});

// Delete conversation
async function deleteConversation(index) {
    if (!confirm('Deseja realmente deletar esta conversa?')) return;
    
    try {
        const response = await fetch(`${API_URL}/delete-conversation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            loadConversationsList();
            alert('âœ… Conversa deletada!');
        } else {
            alert(`âŒ Erro: ${result.error || 'Falha ao deletar'}`);
        }
    } catch (error) {
        alert('âŒ Erro ao deletar conversa');
        console.error('Erro:', error);
    }
}

// Expor funÃ§Ã£o globalmente para onclick
window.deleteConversation = deleteConversation;

// Cleanup actions
document.getElementById('clear-cache-btn').addEventListener('click', async () => {
    if (!confirm('Limpar cache da sessÃ£o atual?')) return;
    
    try {
        const response = await fetch(`${API_URL}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'limpar' })
        });
        
        if (response.ok) {
            alert('âœ… Cache limpo!');
        }
    } catch (error) {
        alert('âŒ Erro ao limpar cache');
    }
});

document.getElementById('clear-conversations-btn').addEventListener('click', async () => {
    if (!confirm('âš ï¸ Isso vai apagar TODAS as conversas salvas. Aprendizados serÃ£o mantidos. Continuar?')) return;
    
    try {
        const response = await fetch(`${API_URL}/clear-conversations`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadConversationsList();
            alert('âœ… Conversas apagadas!');
        }
    } catch (error) {
        alert('âŒ Erro ao limpar conversas');
    }
});

// BotÃ£o "Limpar Tudo" removido por seguranÃ§a

// Preferences
function loadPreferences() {
    const prefs = localStorage.getItem('sofia-preferences');
    if (prefs) {
        const preferences = JSON.parse(prefs);
        document.getElementById('language-select').value = preferences.language || 'pt-BR';
        document.getElementById('theme-select').value = preferences.theme || 'dark';
        document.getElementById('save-history').checked = preferences.saveHistory !== false;
        document.getElementById('show-timestamps').checked = preferences.showTimestamps !== false;
    }
}

document.getElementById('save-preferences-btn').addEventListener('click', () => {
    const preferences = {
        language: document.getElementById('language-select').value,
        theme: document.getElementById('theme-select').value,
        saveHistory: document.getElementById('save-history').checked,
        showTimestamps: document.getElementById('show-timestamps').checked
    };
    
    localStorage.setItem('sofia-preferences', JSON.stringify(preferences));
    alert('âœ… PreferÃªncias salvas!');
    
    // Apply theme if changed
    applyTheme(preferences.theme);
});

function applyTheme(theme) {
    // Implementar mudanÃ§a de tema no futuro
    console.log('Tema selecionado:', theme);
}

function showNotification(message, type = 'success') {
    // Simple notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#EF4444' : '#10B981'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ==================== AJUSTES MOBILE ====================

// Detectar e ajustar layout quando teclado mobile abre/fecha
let initialViewportHeight = window.innerHeight;
let currentViewportHeight = window.innerHeight;

function handleViewportResize() {
    currentViewportHeight = window.innerHeight;
    const keyboardHeight = initialViewportHeight - currentViewportHeight;
    
    // Se o viewport diminuiu mais de 150px, considera que o teclado abriu
    if (keyboardHeight > 150) {
        document.body.classList.add('keyboard-open');
        document.body.style.setProperty('--keyboard-height', `${keyboardHeight}px`);
        
        // Scroll para a mensagem mais recente
        if (chatContainer) {
            setTimeout(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 100);
        }
    } else {
        document.body.classList.remove('keyboard-open');
        document.body.style.setProperty('--keyboard-height', '0px');
    }
}

// Prevenir comportamento padrÃ£o de scroll no mobile
if (messageInput) {
    messageInput.addEventListener('focus', () => {
        setTimeout(() => {
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 300);
    });
    
    messageInput.addEventListener('blur', () => {
        // Pequeno delay para permitir animaÃ§Ã£o suave
        setTimeout(() => {
            window.scrollTo(0, 0);
        }, 100);
    });
}

// Listener para mudanÃ§as no viewport (detecta teclado)
window.addEventListener('resize', handleViewportResize);

// Atualizar altura inicial quando pÃ¡gina carrega
window.addEventListener('load', () => {
    initialViewportHeight = window.innerHeight;
});

// Prevenir zoom no iOS em inputs
if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (viewportMeta) {
        viewportMeta.content = 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no';
    }
}

// Melhorar scroll do chat para mobile
if (chatContainer) {
    // Habilitar smooth scroll
    chatContainer.style.scrollBehavior = 'smooth';
    chatContainer.style.webkitOverflowScrolling = 'touch';
    
    // Prevenir apenas o scroll elÃ¡stico que vai alÃ©m dos limites
    let isScrolling = false;
    
    chatContainer.addEventListener('touchstart', () => {
        isScrolling = true;
    }, { passive: true });
    
    chatContainer.addEventListener('touchend', () => {
        isScrolling = false;
    }, { passive: true });
    
    // Permitir scroll livre dentro do container
    chatContainer.addEventListener('scroll', () => {
        // Scroll automÃ¡tico funciona normalmente
    }, { passive: true });
}

