// =====================================================
// Metaverso 3D - Sofia (Integrado com Chat WebSocket)
// Three.js + Babylon.js design + Chat em tempo real
// =====================================================

let metaverseScene = null;
let metaverseCamera = null;
let metaverseRenderer = null;
let metaverseControls = {
    forward: false,
    backward: false,
    left: false,
    right: false,
    jump: false
};
let playerVelocity = { x: 0, y: 0, z: 0 };
let playerPosition = { x: 0, y: 1.6, z: 5 };
let sofiaAvatar = null;
let sofiaParticles = null;
let animationId = null;
let mouseX = 0;
let mouseY = 0;
let cameraRotationX = 0;
let cameraRotationY = 0;
let isPointerLocked = false;

// Configuração da cena 3D
function initMetaverse() {
    const container = document.getElementById('metaverse-container');
    if (!container) return;

    // Limpar cena anterior se existir
    if (metaverseRenderer) {
        metaverseRenderer.dispose();
        container.innerHTML = '';
    }

    // Cena
    metaverseScene = new THREE.Scene();
    metaverseScene.background = new THREE.Color(0x0a0a14);
    metaverseScene.fog = new THREE.Fog(0x0a0a14, 10, 50);

    // Câmera
    metaverseCamera = new THREE.PerspectiveCamera(
        75,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    metaverseCamera.position.set(playerPosition.x, playerPosition.y, playerPosition.z);

    // Renderer
    metaverseRenderer = new THREE.WebGLRenderer({ antialias: true });
    metaverseRenderer.setSize(container.clientWidth, container.clientHeight);
    metaverseRenderer.shadowMap.enabled = true;
    metaverseRenderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(metaverseRenderer.domElement);

    // Iluminação
    const ambientLight = new THREE.AmbientLight(0x404040, 1.5);
    metaverseScene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    metaverseScene.add(directionalLight);

    // Luz rosa para Sofia
    const sofiaLight = new THREE.PointLight(0xff69b4, 2, 20);
    sofiaLight.position.set(0, 3, 0);
    metaverseScene.add(sofiaLight);

    // Chão (grid futurista)
    const gridHelper = new THREE.GridHelper(100, 50, 0xff69b4, 0x1a1a2e);
    gridHelper.position.y = 0;
    metaverseScene.add(gridHelper);

    // Plataforma
    const platformGeometry = new THREE.BoxGeometry(20, 0.5, 20);
    const platformMaterial = new THREE.MeshStandardMaterial({
        color: 0x1a1a2e,
        roughness: 0.5,
        metalness: 0.5
    });
    const platform = new THREE.Mesh(platformGeometry, platformMaterial);
    platform.position.y = -0.25;
    platform.receiveShadow = true;
    metaverseScene.add(platform);

    // Avatar de Sofia (esfera com gradiente)
    const sofiaGeometry = new THREE.SphereGeometry(0.8, 32, 32);
    const sofiaMaterial = new THREE.MeshStandardMaterial({
        color: 0xff69b4,
        emissive: 0xff69b4,
        emissiveIntensity: 0.3,
        roughness: 0.3,
        metalness: 0.7
    });
    sofiaAvatar = new THREE.Mesh(sofiaGeometry, sofiaMaterial);
    sofiaAvatar.position.set(0, 2, -5);
    sofiaAvatar.castShadow = true;
    metaverseScene.add(sofiaAvatar);

    // Partículas ao redor de Sofia
    createSofiaParticles();

    // Objetos decorativos
    createDecorativeObjects();

    // Controles do teclado
    setupKeyboardControls();

    // Mouse controls
    setupMouseControls(container);

    // Resize handler
    window.addEventListener('resize', onMetaverseResize);

    // Iniciar animação
    animateMetaverse();

    console.log('🌐 Metaverso inicializado!');
}

function createSofiaParticles() {
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 100;
    const positions = new Float32Array(particlesCount * 3);

    for (let i = 0; i < particlesCount * 3; i++) {
        positions[i] = (Math.random() - 0.5) * 5;
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const particlesMaterial = new THREE.PointsMaterial({
        color: 0xffb6d9,
        size: 0.05,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
    });

    const particles = new THREE.Points(particlesGeometry, particlesMaterial);
    particles.position.set(0, 2, -5);
    metaverseScene.add(particles);

    // Animar partículas
    particles.userData.animate = (time) => {
        particles.rotation.y = time * 0.5;
        const positions = particles.geometry.attributes.position.array;
        for (let i = 1; i < positions.length; i += 3) {
            positions[i] = Math.sin((time + i) * 2) * 0.5 + 2;
        }
        particles.geometry.attributes.position.needsUpdate = true;
    };

    return particles;
}

function createDecorativeObjects() {
    // Cubos flutuantes
    for (let i = 0; i < 5; i++) {
        const size = Math.random() * 0.5 + 0.3;
        const geometry = new THREE.BoxGeometry(size, size, size);
        const material = new THREE.MeshStandardMaterial({
            color: Math.random() > 0.5 ? 0x667eea : 0xff69b4,
            emissive: Math.random() > 0.5 ? 0x667eea : 0xff69b4,
            emissiveIntensity: 0.2,
            roughness: 0.4,
            metalness: 0.6
        });
        const cube = new THREE.Mesh(geometry, material);
        
        const angle = (i / 5) * Math.PI * 2;
        const radius = 8;
        cube.position.set(
            Math.cos(angle) * radius,
            Math.random() * 3 + 1,
            Math.sin(angle) * radius
        );
        
        cube.rotation.set(
            Math.random() * Math.PI,
            Math.random() * Math.PI,
            Math.random() * Math.PI
        );
        
        cube.castShadow = true;
        metaverseScene.add(cube);
        
        // Animação de rotação
        cube.userData.rotationSpeed = {
            x: (Math.random() - 0.5) * 0.02,
            y: (Math.random() - 0.5) * 0.02,
            z: (Math.random() - 0.5) * 0.02
        };
    }
}

function setupKeyboardControls() {
    document.addEventListener('keydown', (e) => {
        const modal = document.getElementById('metaverse-modal');
        if (!modal.classList.contains('active')) return;

        switch(e.key.toLowerCase()) {
            case 'w':
                metaverseControls.forward = true;
                break;
            case 's':
                metaverseControls.backward = true;
                break;
            case 'a':
                metaverseControls.left = true;
                break;
            case 'd':
                metaverseControls.right = true;
                break;
            case ' ':
                if (playerPosition.y <= 1.6) {
                    playerVelocity.y = 0.15;
                }
                break;
        }
    });

    document.addEventListener('keyup', (e) => {
        switch(e.key.toLowerCase()) {
            case 'w':
                metaverseControls.forward = false;
                break;
            case 's':
                metaverseControls.backward = false;
                break;
            case 'a':
                metaverseControls.left = false;
                break;
            case 'd':
                metaverseControls.right = false;
                break;
        }
    });
}

// Variáveis de controle de mouse já declaradas no topo

function setupMouseControls(container) {
    container.addEventListener('click', () => {
        container.requestPointerLock();
    });

    document.addEventListener('pointerlockchange', () => {
        isPointerLocked = document.pointerLockElement === container;
    });

    document.addEventListener('mousemove', (e) => {
        if (!isPointerLocked) return;

        mouseX = e.movementX || 0;
        mouseY = e.movementY || 0;

        cameraRotationY -= mouseX * 0.002;
        cameraRotationX -= mouseY * 0.002;

        // Limitar rotação vertical
        cameraRotationX = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, cameraRotationX));
    });
}

function updatePlayerMovement() {
    const speed = 0.1;
    const direction = new THREE.Vector3();

    // Calcular direção baseada na rotação da câmera
    const forward = new THREE.Vector3(
        Math.sin(cameraRotationY),
        0,
        Math.cos(cameraRotationY)
    );
    const right = new THREE.Vector3(
        Math.sin(cameraRotationY + Math.PI / 2),
        0,
        Math.cos(cameraRotationY + Math.PI / 2)
    );

    if (metaverseControls.forward) direction.add(forward);
    if (metaverseControls.backward) direction.sub(forward);
    if (metaverseControls.left) direction.sub(right);
    if (metaverseControls.right) direction.add(right);

    direction.normalize().multiplyScalar(speed);

    playerPosition.x += direction.x;
    playerPosition.z += direction.z;

    // Gravidade
    playerVelocity.y -= 0.01;
    playerPosition.y += playerVelocity.y;

    // Colisão com o chão
    if (playerPosition.y <= 1.6) {
        playerPosition.y = 1.6;
        playerVelocity.y = 0;
    }

    // Limites do mapa
    const limit = 10;
    playerPosition.x = Math.max(-limit, Math.min(limit, playerPosition.x));
    playerPosition.z = Math.max(-limit, Math.min(limit, playerPosition.z));

    // Atualizar câmera
    metaverseCamera.position.set(playerPosition.x, playerPosition.y, playerPosition.z);
    metaverseCamera.rotation.order = 'YXZ';
    metaverseCamera.rotation.x = cameraRotationX;
    metaverseCamera.rotation.y = cameraRotationY;
}

function animateMetaverse() {
    const modal = document.getElementById('metaverse-modal');
    if (!modal.classList.contains('active')) {
        return;
    }

    animationId = requestAnimationFrame(animateMetaverse);

    const time = Date.now() * 0.001;

    // Atualizar movimento do jogador
    updatePlayerMovement();

    // Animar Sofia
    if (sofiaAvatar) {
        sofiaAvatar.position.y = Math.sin(time * 2) * 0.2 + 2;
        sofiaAvatar.rotation.y = time * 0.5;
    }

    // Animar objetos decorativos
    metaverseScene.children.forEach(child => {
        if (child.userData.rotationSpeed) {
            child.rotation.x += child.userData.rotationSpeed.x;
            child.rotation.y += child.userData.rotationSpeed.y;
            child.rotation.z += child.userData.rotationSpeed.z;
        }
        if (child.userData.animate) {
            child.userData.animate(time);
        }
    });

    metaverseRenderer.render(metaverseScene, metaverseCamera);
}

function onMetaverseResize() {
    const container = document.getElementById('metaverse-container');
    if (!container || !metaverseCamera || !metaverseRenderer) return;

    metaverseCamera.aspect = container.clientWidth / container.clientHeight;
    metaverseCamera.updateProjectionMatrix();
    metaverseRenderer.setSize(container.clientWidth, container.clientHeight);
}

function cleanupMetaverse() {
    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }
    
    window.removeEventListener('resize', onMetaverseResize);
    
    if (metaverseRenderer) {
        metaverseRenderer.dispose();
        metaverseRenderer = null;
    }
    
    metaverseScene = null;
    metaverseCamera = null;
    
    console.log('🌐 Metaverso limpo');
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    const metaverseBtn = document.getElementById('metaverse-btn');
    const metaverseModal = document.getElementById('metaverse-modal');
    const metaverseSendBtn = document.getElementById('metaverse-send-btn');
    const metaverseInput = document.getElementById('metaverse-input-text');

    if (metaverseBtn) {
        metaverseBtn.addEventListener('click', () => {
            metaverseModal.classList.add('active');
            setTimeout(() => {
                initMetaverse();
            }, 100);
        });
    }

    // Fechar modal
    const closeButtons = metaverseModal.querySelectorAll('.modal-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            metaverseModal.classList.remove('active');
            cleanupMetaverse();
            if (document.pointerLockElement) {
                document.exitPointerLock();
            }
        });
    });

    // Enviar mensagem no metaverso
    function sendMetaverseMessage() {
        const message = metaverseInput.value.trim();
        if (!message) return;

        const messagesContainer = document.getElementById('metaverse-messages');
        
        // Adicionar mensagem do usuário
        const userMsg = document.createElement('div');
        userMsg.className = 'metaverse-message user';
        userMsg.textContent = message;
        messagesContainer.appendChild(userMsg);

        metaverseInput.value = '';
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Mostrar status de processamento
        const statusDiv = document.getElementById('metaverse-status');
        if (statusDiv) {
            statusDiv.classList.add('active');
        }

        // Enviar para Sofia via WebSocket (usando a conexão existente)
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'message',
                content: message,
                user_name: 'Usuário',
                metaverse: true
            }));
        }

        // Mensagem temporária de processamento
        setTimeout(() => {
            const sofiaMsg = document.createElement('div');
            sofiaMsg.className = 'metaverse-message sofia';
            sofiaMsg.textContent = '🌸 Sofia está pensando...';
            sofiaMsg.id = 'temp-processing-msg';
            messagesContainer.appendChild(sofiaMsg);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 300);
    }

    if (metaverseSendBtn) {
        metaverseSendBtn.addEventListener('click', sendMetaverseMessage);
    }

    if (metaverseInput) {
        metaverseInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMetaverseMessage();
            }
        });
    }

    // Fechar ao clicar fora
    metaverseModal.addEventListener('click', (e) => {
        if (e.target === metaverseModal) {
            metaverseModal.classList.remove('active');
            cleanupMetaverse();
            if (document.pointerLockElement) {
                document.exitPointerLock();
            }
        }
    });
});
