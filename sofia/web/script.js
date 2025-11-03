// API Configuration
const API_URL = 'http://localhost:5000';

// DOM Elements
const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const statusText = document.getElementById('status-text');
const quickBtns = document.querySelectorAll('.quick-btn');
const statsBtn = document.getElementById('stats-btn');
const memoryBtn = document.getElementById('memory-btn');
const statsModal = document.getElementById('stats-modal');
const memoryModal = document.getElementById('memory-modal');

// Initialize
let conversationHistory = [];

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
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
memoryBtn.addEventListener('click', () => openModal('memory'));

document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => closeModals());
});

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModals();
    });
});

// Functions
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Remove welcome message if exists
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();

    // Add user message
    addMessage('user', message);

    // Show typing indicator
    showTypingIndicator();

    try {
        // Send to API
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory
            })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        if (data.response) {
            // Add Sofia's response
            addMessage('sofia', data.response);
            
            // Update history
            conversationHistory.push(
                { de: 'Usuário', texto: message },
                { de: 'Sofia', texto: data.response }
            );
        } else {
            addMessage('sofia', '❌ Desculpe, ocorreu um erro ao processar sua mensagem.');
        }
    } catch (error) {
        removeTypingIndicator();
        addMessage('sofia', '❌ Não foi possível conectar ao servidor. Certifique-se de que a API está rodando.');
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

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    content.appendChild(time);
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

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message sofia typing';
    typingDiv.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🌸';

    const content = document.createElement('div');
    content.className = 'message-content';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    
    content.appendChild(indicator);
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(content);
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
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
    const modal = type === 'stats' ? statsModal : memoryModal;
    const contentEl = type === 'stats' ? 
        document.getElementById('stats-content') : 
        document.getElementById('memory-content');

    modal.classList.add('active');
    contentEl.innerHTML = '<div class="loading">Carregando...</div>';

    try {
        const response = await fetch(`${API_URL}/${type}`);
        const data = await response.json();

        if (type === 'stats') {
            contentEl.innerHTML = formatStats(data);
        } else {
            contentEl.innerHTML = formatMemory(data);
        }
    } catch (error) {
        contentEl.innerHTML = '<div class="loading">❌ Erro ao carregar dados</div>';
        console.error('Erro:', error);
    }
}

function closeModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
}

function formatStats(data) {
    return `
        <div style="line-height: 1.8;">
            <p><strong>💾 Conversas:</strong> ${data.total_conversas || 0}</p>
            <p><strong>🧠 Aprendizados:</strong> ${data.total_aprendizados || 0}</p>
            <p><strong>📁 Uso de disco:</strong> ${data.tamanho_mb?.toFixed(2) || 0} MB</p>
            <p><strong>📈 Capacidade:</strong> ${data.percentual?.toFixed(2) || 0}% de 5 GB</p>
            <p><strong>🔢 Cache (RAM):</strong> ${data.cache || 0} mensagens</p>
        </div>
    `;
}

function formatMemory(data) {
    if (!data.aprendizados || Object.keys(data.aprendizados).length === 0) {
        return '<p>Ainda não há aprendizados registrados.</p>';
    }

    let html = '';
    for (const [categoria, itens] of Object.entries(data.aprendizados)) {
        html += `<h4 style="margin-top: 1rem; margin-bottom: 0.5rem;">📂 ${categoria.toUpperCase()}</h4>`;
        html += '<ul style="list-style: none; padding-left: 0;">';
        for (const [chave, dados] of Object.entries(itens)) {
            html += `<li style="margin: 0.5rem 0; padding: 0.5rem; background: var(--bg-color); border-radius: 8px;">
                <strong>${chave}:</strong> ${dados.valor} 
                <span style="color: var(--text-muted); font-size: 0.875rem;">(freq: ${dados.frequencia})</span>
            </li>`;
        }
        html += '</ul>';
    }
    return html;
}

// Check API status on load
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_URL}/status`);
        if (response.ok) {
            statusText.textContent = 'Online';
        } else {
            statusText.textContent = 'Offline';
        }
    } catch (error) {
        statusText.textContent = 'Offline';
        console.error('API não está respondendo');
    }
}

// Initialize
checkAPIStatus();
setInterval(checkAPIStatus, 30000); // Check every 30 seconds
