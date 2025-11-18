// API Configuration
const API_URL = 'https://eaf55f1d3101.ngrok-free.app';
const WS_URL = 'wss://eaf55f1d3101.ngrok-free.app';

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
            throw new Error('Falha ao criar sessão');
        }

        const data = await response.json();
        sessionId = data.session_id;
        console.log('Sessão criada:', sessionId);
        return sessionId;
    } catch (error) {
        console.error('Erro ao criar sessão:', error);
        updateStatus('connecting', 'Pensando...');
        throw error;
    }
}

// Função para inicializar WebSocket
async function initializeWebSocket() {
    try {
        await createSession();
        connectWebSocket();
    } catch (error) {
        console.error('Erro ao inicializar:', error);
        updateStatus('connecting', 'Pensando...');
    }
}

// Função para conectar WebSocket
function connectWebSocket() {
    if (!sessionId) {
        console.error('Session ID não disponível');
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
            console.error('Erro no WebSocket:', error);
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

// Função para tentar reconexão
function attemptReconnect() {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        console.log(`Tentativa de reconexão ${reconnectAttempts}/${maxReconnectAttempts}`);
        updateStatus('connecting', 'Pensando...');

        setTimeout(() => {
            connectWebSocket();
        }, reconnectDelay * reconnectAttempts);
    } else {
        updateStatus('connecting', 'Pensando...');
        // Continua tentando após delay maior
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

            // Se estiver no metaverso, também adicionar lá
            const metaverseModal = document.getElementById('metaverse-modal');
            if (metaverseModal && metaverseModal.classList.contains('active')) {
                const messagesContainer = document.getElementById('metaverse-messages');
                const statusDiv = document.getElementById('metaverse-status');

                if (messagesContainer) {
                    // Remover mensagem temporária de "processando"
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
                    sofiaMsg.textContent = '🌸 ' + data.content;
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

            // Adicionar ao histórico
            conversationHistory.push(
                { de: 'Sofia', texto: data.content }
            );
            break;

        case 'cancelled':
            hideTypingIndicator();
            console.log('⏹️ Processamento cancelado:', data.content);
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

// Atualizar status de conexão
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

// Indicador de digitação
function showTypingIndicator() {
    const existingIndicator = document.querySelector('.typing-indicator');
    if (!existingIndicator) {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <span style="margin-left: 10px;">Sofia está digitando...</span>
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
    // Verifica se já tem 10 arquivos
    if (attachedFiles.length >= 10) {
        showNotification('❌ Limite de 10 arquivos atingido', 'error');
        return;
    }

    // Verifica tamanho (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showNotification(`❌ ${file.name} muito grande (máx. 10MB)`, 'error');
        return;
    }

    // Verifica formato
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
        showNotification(`❌ Formato não suportado: ${file.name}`, 'error');
        return;
    }

    // Upload para o servidor
    try {
        showNotification(`📤 Enviando ${file.name}...`, 'info');
        
        const formData = new FormData();
        formData.append('file', file);

        console.log(`[UPLOAD] Enviando para: ${API_URL}/upload-file`);
        console.log(`[UPLOAD] Arquivo: ${file.name}, Tipo: ${file.type}, Tamanho: ${file.size} bytes`);

        const response = await fetch(`${API_URL}/upload-file`, {
            method: 'POST',
            body: formData
        });

        console.log(`[UPLOAD] Status da resposta: ${response.status}`);
        const data = await response.json();
        console.log(`[UPLOAD] Resposta completa:`, data);

        if (data.sucesso) {
            console.log(`[UPLOAD] ✅ Arquivo processado com sucesso!`);
            console.log(`[UPLOAD] - ID: ${data.arquivo_id}`);
            console.log(`[UPLOAD] - Tipo: ${data.tipo}`);
            console.log(`[UPLOAD] - Nome: ${data.nome}`);
            
            attachedFiles.push({
                id: data.arquivo_id,
                name: file.name,
                type: data.tipo,
                file: file
            });
            
            updateAttachedFilesUI(); // Atualiza a UI
            
            const mensagem = data.mensagem || `✅ ${file.name} anexado!`;
            showNotification(mensagem, 'success');
            
            if (data.tipo === 'pdf') {
                if (data.conteudo) {
                    console.log(`[PDF] ✅ Conteúdo extraído (preview):`);
                    console.log(data.conteudo.substring(0, 500));
                    showNotification(`📄 PDF lido! ${data.conteudo.length} caracteres`, 'success');
                } else {
                    console.warn(`[PDF] ⚠️ PDF salvo mas sem conteúdo extraído`);
                    showNotification(`⚠️ PDF anexado mas texto não foi extraído`, 'warning');
                }
            }
        } else {
            console.error(`[UPLOAD ERRO]`, data.erro);
            showNotification(`❌ ${data.erro}`, 'error');
        }
    } catch (error) {
        console.error(`[UPLOAD EXCEÇÃO]`, error);
        showNotification(`❌ Erro ao anexar ${file.name}: ${error.message}`, 'error');
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
            <span class="attached-file-icon">${file.type === 'imagem' ? '🖼️' : '📄'}</span>
            <span class="attached-file-name" title="${file.name}">${file.name}</span>
            <button class="attached-file-remove" onclick="removeAttachedFile(${index})">✕</button>
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
        showNotification('🌐 Modo Web ATIVADO - Sofia buscará na internet');

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
        showNotification('🌐 Modo Web DESATIVADO', 'info');

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
            updateStatus('connecting', 'Pensando...');
        }

        // Update history
        conversationHistory.push(
            { de: 'Usuário', texto: message }
        );
    } catch (error) {
        hideTypingIndicator();
        addMessage('sofia', '❌ Não foi possível enviar a mensagem. Tentando reconectar...');
        console.error('Erro:', error);
    }
}

function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'sofia' ? '🌸' : '👤';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = formatMessage(text);

    // Criar container para hora + ícones
    const timeContainer = document.createElement('div');
    timeContainer.className = 'message-time-container';

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });

    timeContainer.appendChild(time);

    // Adicionar ícones de ação apenas para mensagens do usuário
    if (sender === 'user') {
        const iconsDiv = document.createElement('div');
        iconsDiv.className = 'message-icons';

        // Ícone Stop
        const stopIcon = document.createElement('span');
        stopIcon.className = 'message-icon stop-icon';
        stopIcon.innerHTML = '⏹️';
        stopIcon.title = 'Parar resposta';
        stopIcon.onclick = () => stopResponse();

        // Ícone Editar
        const editIcon = document.createElement('span');
        editIcon.className = 'message-icon edit-icon';
        editIcon.innerHTML = '✏️';
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

// Função para parar a resposta da Sofia
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

        // Fecha a conexão WebSocket para forçar interrupção
        ws.close();
        hideTypingIndicator();
        showNotification('⏹️ Processamento interrompido', 'warning');

        // Reconecta após 500ms
        setTimeout(() => {
            connectWebSocket();
        }, 500);
    } else {
        hideTypingIndicator();
        showNotification('⏹️ Resposta cancelada', 'info');
    }
}

// Função para editar mensagem do usuário
function editMessage(messageDiv, originalText) {
    // Remove o conteúdo formatado e mostra um textarea
    const contentDiv = messageDiv.querySelector('.message-content');

    // Cria textarea para edição
    const textarea = document.createElement('textarea');
    textarea.className = 'edit-textarea';
    textarea.value = originalText;
    textarea.rows = 3;

    // Limpa o conteúdo atual
    contentDiv.innerHTML = '';
    contentDiv.appendChild(textarea);

    // Cria botões de confirmação
    const editActionsDiv = document.createElement('div');
    editActionsDiv.className = 'message-actions edit-actions';

    const saveBtn = document.createElement('button');
    saveBtn.className = 'message-action-btn save-btn';
    saveBtn.innerHTML = '✅ Salvar';
    saveBtn.onclick = () => saveEditedMessage(messageDiv, textarea.value, originalText);

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'message-action-btn cancel-btn';
    cancelBtn.innerHTML = '❌ Cancelar';
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
        showNotification('❌ A mensagem não pode estar vazia', 'error');
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

            // Remove do histórico de conversação
            const lastSofiaResponse = conversationHistory.findIndex(
                (msg, idx) => idx > 0 && msg.de === 'Sofia' &&
                    conversationHistory[idx - 1].texto === oldText
            );
            if (lastSofiaResponse !== -1) {
                conversationHistory.splice(lastSofiaResponse, 1);
            }
        }
    }

    // Remove a mensagem antiga do usuário
    messageDiv.remove();

    // Remove do histórico a mensagem antiga do usuário
    const oldMessageIndex = conversationHistory.findIndex(
        msg => msg.de === 'Usuário' && msg.texto === oldText
    );
    if (oldMessageIndex !== -1) {
        conversationHistory.splice(oldMessageIndex, 1);
    }

    // Atualiza o input com o novo texto
    messageInput.value = newText;

    // Envia a mensagem editada como uma nova pergunta
    sendMessage();

    showNotification('✏️ Mensagem reenviada', 'success');
}

// Cancelar edição
function cancelEdit(messageDiv, originalText) {
    const contentDiv = messageDiv.querySelector('.message-content');

    // Restaura o conteúdo original
    contentDiv.innerHTML = formatMessage(originalText);

    // Recria container de hora + ícones
    const timeContainer = document.createElement('div');
    timeContainer.className = 'message-time-container';

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });

    timeContainer.appendChild(time);

    // Recria os ícones de ação
    const iconsDiv = document.createElement('div');
    iconsDiv.className = 'message-icons';

    const stopIcon = document.createElement('span');
    stopIcon.className = 'message-icon stop-icon';
    stopIcon.innerHTML = '⏹️';
    stopIcon.title = 'Parar resposta';
    stopIcon.onclick = () => stopResponse();

    const editIcon = document.createElement('span');
    editIcon.className = 'message-icon edit-icon';
    editIcon.innerHTML = '✏️';
    editIcon.title = 'Editar mensagem';
    editIcon.onclick = () => editMessage(messageDiv, originalText);

    iconsDiv.appendChild(stopIcon);
    iconsDiv.appendChild(editIcon);
    timeContainer.appendChild(iconsDiv);

    contentDiv.appendChild(timeContainer);
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
        addMessage('sofia', '❌ Erro ao executar ação.');
        console.error('Erro:', error);
    }
}

async function openModal(type) {
    const modal = statsModal;
    const contentEl = document.getElementById('stats-content');

    console.log('Abrindo modal de estatisticas...');
    modal.classList.add('active');
    contentEl.innerHTML = '<div class="loading">Carregando estatisticas...</div>';

    try {
        console.log('Buscando stats de:', `${API_URL}/stats`);
        const response = await fetch(`${API_URL}/stats`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Stats recebidos:', data);

        contentEl.innerHTML = formatStats(data);
    } catch (error) {
        console.error('Erro ao carregar stats:', error);
        contentEl.innerHTML = '<div class="loading">Erro ao carregar estatisticas da memoria. Verifique o console.</div>';
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

    // Calcular espaço disponível
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
                    <div class="stat-icon">💬</div>
                    <div class="stat-info">
                        <div class="stat-label">Conversas Salvas</div>
                        <div class="stat-value">${totalConversas.toLocaleString('pt-BR')}</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">🧠</div>
                    <div class="stat-info">
                        <div class="stat-label">Aprendizados</div>
                        <div class="stat-value">${totalAprendizados.toLocaleString('pt-BR')}</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">⚙️</div>
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
                    💾 Armazenamento em Disco
                </h4>
                
                <div class="storage-info">
                    <div class="storage-row">
                        <span class="storage-label">Espaço usado:</span>
                        <span class="storage-value">${tamanhoMB.toFixed(2)} MB (${espacoUsadoGB} GB)</span>
                    </div>
                    <div class="storage-row">
                        <span class="storage-label">Espaço disponível:</span>
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
                        <span class="usage-icon">📚</span>
                        <span class="usage-text">
                            <strong>Média por conversa:</strong> 
                            ${totalConversas > 0 ? (tamanhoMB / totalConversas).toFixed(2) : 0} MB
                        </span>
                    </div>
                    <div class="usage-item">
                        <span class="usage-icon">📈</span>
                        <span class="usage-text">
                            <strong>Status:</strong> 
                            ${percentual < 50 ? '✅ Saudável' : percentual < 80 ? '⚠️ Moderado' : '🚨 Crítico'}
                        </span>
                    </div>
                </div>
            </div>
            
            <!-- Recomendações -->
            ${percentual > 70 ? `
            <div class="recommendations">
                <h4 style="margin: 1.5rem 0 1rem 0; color: #ff9800; font-size: 1rem;">
                    ⚠️ Recomendações
                </h4>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    ${percentual > 90 ? '<li style="padding: 0.5rem; margin: 0.25rem 0; background: rgba(244, 67, 54, 0.1); border-left: 3px solid #f44336; border-radius: 4px;">🚨 Espaço crítico! Limpe conversas antigas urgentemente.</li>' : ''}
                    ${percentual > 70 && percentual <= 90 ? '<li style="padding: 0.5rem; margin: 0.25rem 0; background: rgba(255, 152, 0, 0.1); border-left: 3px solid #ff9800; border-radius: 4px;">⚠️ Considere limpar conversas antigas nas Configurações.</li>' : ''}
                    <li style="padding: 0.5rem; margin: 0.25rem 0; background: rgba(33, 150, 243, 0.1); border-left: 3px solid #2196F3; border-radius: 4px;">💡 Use o botão ⚙️ Configurações → Limpeza para liberar espaço.</li>
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
        const response = await fetch(`${API_URL}/api/health`);
        if (response.ok) {
            statusText.textContent = 'Online';
        } else {
            statusText.textContent = 'Pensando...';
        }
    } catch (error) {
        statusText.textContent = 'Pensando...';
        console.error('API não está respondendo');
    }
}

// Initialize
checkAPIStatus();
setInterval(checkAPIStatus, 30000); // Check every 30 seconds
loadPreferences();

// ========== SETTINGS MODAL FUNCTIONS ==========

function openSettingsModal() {
    console.log('Abrindo modal de configuracoes...');
    if (!settingsModal) {
        console.error('settingsModal nao encontrado!');
        return;
    }
    settingsModal.classList.add('active');
    loadConversationsList();
}

// Tab switching - executar quando DOM estiver pronto
function initTabSwitching() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    console.log('Inicializando tabs. Encontrados:', tabButtons.length);
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = btn.dataset.tab;
            console.log('Tab clicada:', tabId);
            
            // Remove active from all tabs and contents
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Add active to clicked tab
            btn.classList.add('active');
            const tabContent = document.getElementById(tabId);
            if (tabContent) {
                tabContent.classList.add('active');
                console.log('Tab content ativado:', tabId);
            } else {
                console.error('Tab content nao encontrado:', tabId);
            }

            // Load data for specific tabs
            if (tabId === 'memory-tab') {
                loadConversationsList();
            }
        });
    });
}

// Chamar inicializacao quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTabSwitching);
} else {
    initTabSwitching();
}

// Load conversations list
async function loadConversationsList() {
    const listEl = document.getElementById('conversations-list');
    if (!listEl) {
        console.error('Elemento conversations-list nao encontrado!');
        return;
    }
    
    listEl.innerHTML = '<div class="loading">Carregando conversas...</div>';

    try {
        console.log('Buscando conversas de:', `${API_URL}/conversations`);
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
                            🗑️
                        </button>
                    </div>
                `;
                listEl.appendChild(item);
            });
        } else {
            listEl.innerHTML = '<p class="text-muted">Nenhuma conversa salva ainda.</p>';
        }
    } catch (error) {
        listEl.innerHTML = '<p class="text-muted">❌ Erro ao carregar conversas</p>';
        console.error('Erro:', error);
    }
}

    // Search conversations
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', async () => {
            const searchInput = document.getElementById('search-conversations');
            const searchTerm = searchInput ? searchInput.value.trim() : '';
            if (!searchTerm) {
                loadConversationsList();
                return;
            }

            const listEl = document.getElementById('conversations-list');
            if (!listEl) return;

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
                listEl.innerHTML = '<p class="text-muted">❌ Erro ao buscar</p>';
                console.error('Erro:', error);
            }
        });
    }

    
    // Delete conversation
    async function deleteConversation(index) {
        if (!confirm('Tem certeza que deseja deletar esta conversa?')) return;
    
        try {
            const response = await fetch(`${API_URL}/delete-conversation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index })
            });
    
            const data = await response.json();
            if (data.sucesso) {
                showNotification('✅ Conversa deletada');
                loadConversationsList();
            } else {
                showNotification('❌ Erro ao deletar', 'error');
            }
        } catch (error) {
            showNotification('❌ Erro ao deletar', 'error');
            console.error('Erro:', error);
        }
    }
    
    // Cleanup actions
    const clearCacheBtn = document.getElementById('clear-cache-btn');
    if (clearCacheBtn) {
        clearCacheBtn.addEventListener('click', async () => {
            if (!confirm('Limpar cache da sessão atual?')) return;

            try {
                const response = await fetch(`${API_URL}/action`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'limpar' })
                });

                if (response.ok) {
                    showNotification('✅ Cache limpo!', 'success');
                }
            } catch (error) {
                showNotification('❌ Erro ao limpar cache', 'error');
            }
        });
    }
const clearConversationsBtn = document.getElementById('clear-conversations-btn');
if (clearConversationsBtn) {
    clearConversationsBtn.addEventListener('click', async () => {
        if (!confirm('⚠️ Isso vai apagar TODAS as conversas salvas. Aprendizados serão mantidos. Continuar?')) return;

        try {
            const response = await fetch(`${API_URL}/clear-conversations`, {
                method: 'POST'
            });

            if (response.ok) {
                loadConversationsList();
                showNotification('✅ Conversas apagadas!', 'success');
            }
        } catch (error) {
            showNotification('❌ Erro ao limpar conversas', 'error');
        }
    });
}

    
    // Preferences functions
    function loadPreferences() {
    const prefs = localStorage.getItem('sofia-preferences');
    if (!prefs) return;

    const preferences = JSON.parse(prefs);

    const langSelect = document.getElementById('language-select');
    if (langSelect) langSelect.value = preferences.language || 'pt-BR';

    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) themeSelect.value = preferences.theme || 'dark';

    const saveHistoryCheckbox = document.getElementById('save-history');
    if (saveHistoryCheckbox) saveHistoryCheckbox.checked = preferences.saveHistory !== false;

    const showTimestampsCheckbox = document.getElementById('show-timestamps');
    if (showTimestampsCheckbox) showTimestampsCheckbox.checked = preferences.showTimestamps !== false;
}

    
    const savePreferencesBtn = document.getElementById('save-preferences-btn');
if (savePreferencesBtn) {
    savePreferencesBtn.addEventListener('click', () => {
        const languageSelect = document.getElementById('language-select');
        const themeSelect = document.getElementById('theme-select');
        const saveHistoryCheckbox = document.getElementById('save-history');
        const showTimestampsCheckbox = document.getElementById('show-timestamps');

        const preferences = {
            language: languageSelect ? languageSelect.value : 'pt-BR',
            theme: themeSelect ? themeSelect.value : 'dark',
            saveHistory: saveHistoryCheckbox ? saveHistoryCheckbox.checked : true,
            showTimestamps: showTimestampsCheckbox ? showTimestampsCheckbox.checked : true
        };

        localStorage.setItem('sofia-preferences', JSON.stringify(preferences));
        showNotification('✅ Preferências salvas!', 'success');

        // Apply theme if changed
        applyTheme(preferences.theme);
    });
}

    // Notification function
    function showNotification(message, type = 'success') {
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
