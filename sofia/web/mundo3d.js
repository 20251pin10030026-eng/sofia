// Configuração da API
const API_URL = 'http://localhost:5000';

// Variáveis globais
let scene, camera, renderer, controls;
let player, sofia;
let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
let canJump = false, isRunning = false;
let velocity = new THREE.Vector3();
let direction = new THREE.Vector3();
let prevTime = performance.now();
let isPointerLocked = false;

// Inicialização
document.addEventListener('DOMContentLoaded', init);

function init() {
    // Click to start
    const clickToStart = document.getElementById('click-to-start');
    const startBtn = clickToStart.querySelector('.start-btn');
    
    startBtn.addEventListener('click', () => {
        clickToStart.style.display = 'none';
        initWorld();
    });
}

function initWorld() {
    // Esconde loading
    setTimeout(() => {
        document.getElementById('loading').style.display = 'none';
    }, 1000);

    // Criar cena
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB); // Céu azul
    scene.fog = new THREE.Fog(0x87CEEB, 0, 750);

    // Câmera (primeira pessoa)
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(0, 1.6, 5); // Altura dos olhos

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('canvas-container').appendChild(renderer.domElement);

    // Iluminação
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 100, 50);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.left = -100;
    directionalLight.shadow.camera.right = 100;
    directionalLight.shadow.camera.top = 100;
    directionalLight.shadow.camera.bottom = -100;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    // Chão (grama)
    const groundGeometry = new THREE.PlaneGeometry(200, 200);
    const groundMaterial = new THREE.MeshLambertMaterial({ 
        color: 0x3a8c3a,
        side: THREE.DoubleSide 
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grid para referência
    const gridHelper = new THREE.GridHelper(200, 50, 0x000000, 0x555555);
    gridHelper.material.opacity = 0.2;
    gridHelper.material.transparent = true;
    scene.add(gridHelper);

    // Criar Sofia
    createSofia();

    // Criar alguns objetos no mundo
    createEnvironment();

    // Criar player (invisível, mas com colisão)
    const playerGeometry = new THREE.CapsuleGeometry(0.5, 1.6, 4, 8);
    const playerMaterial = new THREE.MeshBasicMaterial({ 
        color: 0x00ff00, 
        visible: false 
    });
    player = new THREE.Mesh(playerGeometry, playerMaterial);
    player.position.copy(camera.position);
    scene.add(player);

    // Controles de teclado
    setupControls();

    // Pointer lock
    setupPointerLock();

    // Chat
    setupChat();

    // Resize
    window.addEventListener('resize', onWindowResize);

    // Iniciar animação
    animate();
}

function createSofia() {
    // Grupo para Sofia
    sofia = new THREE.Group();
    
    // Corpo (cilindro)
    const bodyGeometry = new THREE.CylinderGeometry(0.3, 0.25, 1.2, 16);
    const bodyMaterial = new THREE.MeshPhongMaterial({ color: 0x9966ff }); // Roxo
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0.6;
    body.castShadow = true;
    sofia.add(body);

    // Cabeça
    const headGeometry = new THREE.SphereGeometry(0.25, 16, 16);
    const headMaterial = new THREE.MeshPhongMaterial({ color: 0xffdbac }); // Tom de pele
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 1.4;
    head.castShadow = true;
    sofia.add(head);

    // Cabelo
    const hairGeometry = new THREE.SphereGeometry(0.27, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    const hairMaterial = new THREE.MeshPhongMaterial({ color: 0x4a2c2a }); // Marrom escuro
    const hair = new THREE.Mesh(hairGeometry, hairMaterial);
    hair.position.y = 1.5;
    hair.castShadow = true;
    sofia.add(hair);

    // Olhos
    const eyeGeometry = new THREE.SphereGeometry(0.05, 8, 8);
    const eyeMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
    
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.1, 1.45, 0.2);
    sofia.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.1, 1.45, 0.2);
    sofia.add(rightEye);

    // Braços
    const armGeometry = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 8);
    const armMaterial = new THREE.MeshPhongMaterial({ color: 0xffdbac });
    
    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
    leftArm.position.set(-0.4, 0.6, 0);
    leftArm.castShadow = true;
    sofia.add(leftArm);
    
    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
    rightArm.position.set(0.4, 0.6, 0);
    rightArm.castShadow = true;
    sofia.add(rightArm);

    // Pernas
    const legGeometry = new THREE.CylinderGeometry(0.1, 0.1, 0.9, 8);
    const legMaterial = new THREE.MeshPhongMaterial({ color: 0x4444ff });
    
    const leftLeg = new THREE.Mesh(legGeometry, legMaterial);
    leftLeg.position.set(-0.15, -0.45, 0);
    leftLeg.castShadow = true;
    sofia.add(leftLeg);
    
    const rightLeg = new THREE.Mesh(legGeometry, legMaterial);
    rightLeg.position.set(0.15, -0.45, 0);
    rightLeg.castShadow = true;
    sofia.add(rightLeg);

    // Nome acima da cabeça
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    context.fillStyle = 'rgba(0, 0, 0, 0.7)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = 'white';
    context.font = 'Bold 32px Arial';
    context.textAlign = 'center';
    context.fillText('Sofia 🌸', canvas.width / 2, 42);
    
    const texture = new THREE.CanvasTexture(canvas);
    const nameMaterial = new THREE.SpriteMaterial({ map: texture });
    const nameSprite = new THREE.Sprite(nameMaterial);
    nameSprite.position.y = 2.2;
    nameSprite.scale.set(2, 0.5, 1);
    sofia.add(nameSprite);

    // Posicionar Sofia no mundo
    sofia.position.set(0, 0, -5);
    
    scene.add(sofia);
}

function createEnvironment() {
    // Criar algumas árvores
    for (let i = 0; i < 10; i++) {
        const tree = createTree();
        const angle = (i / 10) * Math.PI * 2;
        const radius = 15 + Math.random() * 30;
        tree.position.set(
            Math.cos(angle) * radius,
            0,
            Math.sin(angle) * radius
        );
        scene.add(tree);
    }

    // Criar pedras
    for (let i = 0; i < 15; i++) {
        const rock = createRock();
        rock.position.set(
            (Math.random() - 0.5) * 100,
            0,
            (Math.random() - 0.5) * 100
        );
        scene.add(rock);
    }

    // Sol
    const sunGeometry = new THREE.SphereGeometry(5, 16, 16);
    const sunMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 });
    const sun = new THREE.Mesh(sunGeometry, sunMaterial);
    sun.position.set(50, 80, 50);
    scene.add(sun);
}

function createTree() {
    const tree = new THREE.Group();
    
    // Tronco
    const trunkGeometry = new THREE.CylinderGeometry(0.3, 0.4, 3, 8);
    const trunkMaterial = new THREE.MeshLambertMaterial({ color: 0x8b4513 });
    const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
    trunk.position.y = 1.5;
    trunk.castShadow = true;
    tree.add(trunk);
    
    // Copa
    const leavesGeometry = new THREE.SphereGeometry(1.5, 8, 8);
    const leavesMaterial = new THREE.MeshLambertMaterial({ color: 0x228b22 });
    const leaves = new THREE.Mesh(leavesGeometry, leavesMaterial);
    leaves.position.y = 3.5;
    leaves.castShadow = true;
    tree.add(leaves);
    
    return tree;
}

function createRock() {
    const geometry = new THREE.DodecahedronGeometry(0.5 + Math.random() * 0.5, 0);
    const material = new THREE.MeshLambertMaterial({ color: 0x808080 });
    const rock = new THREE.Mesh(geometry, material);
    rock.castShadow = true;
    rock.receiveShadow = true;
    return rock;
}

function setupControls() {
    document.addEventListener('keydown', (event) => {
        switch (event.code) {
            case 'KeyW': moveForward = true; break;
            case 'KeyS': moveBackward = true; break;
            case 'KeyA': moveLeft = true; break;
            case 'KeyD': moveRight = true; break;
            case 'Space': if (canJump) velocity.y += 7; canJump = false; break;
            case 'ShiftLeft': isRunning = true; break;
            case 'KeyE': interactWithSofia(); break;
        }
    });

    document.addEventListener('keyup', (event) => {
        switch (event.code) {
            case 'KeyW': moveForward = false; break;
            case 'KeyS': moveBackward = false; break;
            case 'KeyA': moveLeft = false; break;
            case 'KeyD': moveRight = false; break;
            case 'ShiftLeft': isRunning = false; break;
        }
    });
}

function setupPointerLock() {
    const container = renderer.domElement;

    container.addEventListener('click', () => {
        if (!isPointerLocked) {
            container.requestPointerLock();
        }
    });

    document.addEventListener('pointerlockchange', () => {
        isPointerLocked = document.pointerLockElement === container;
    });

    document.addEventListener('mousemove', (event) => {
        if (!isPointerLocked) return;

        const movementX = event.movementX || 0;
        const movementY = event.movementY || 0;

        camera.rotation.y -= movementX * 0.002;
        camera.rotation.x -= movementY * 0.002;

        // Limitar rotação vertical
        camera.rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, camera.rotation.x));
    });
}

function setupChat() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    
    sendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Adicionar mensagem do usuário
    addChatMessage('user', message);
    input.value = '';
    
    // Enviar para API
    fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensagem: message })
    })
    .then(res => res.json())
    .then(data => {
        addChatMessage('sofia', data.resposta);
        // Animar Sofia falando
        animateSofiaTalking();
    })
    .catch(err => {
        console.error('Erro ao enviar mensagem:', err);
        addChatMessage('sofia', 'Desculpe, ocorreu um erro ao processar sua mensagem.');
    });
}

function addChatMessage(sender, text) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function animateSofiaTalking() {
    // Animar cabeça de Sofia
    let count = 0;
    const interval = setInterval(() => {
        if (sofia) {
            sofia.children[1].rotation.y = Math.sin(count * 0.5) * 0.1;
            count++;
            if (count > 20) clearInterval(interval);
        }
    }, 50);
}

function interactWithSofia() {
    const distance = camera.position.distanceTo(sofia.position);
    
    if (distance < 5) {
        // Abrir chat
        const chatPanel = document.getElementById('chat-panel');
        chatPanel.style.display = chatPanel.style.display === 'none' ? 'block' : 'none';
        
        if (chatPanel.style.display === 'block') {
            document.getElementById('chat-input').focus();
        }
    }
}

function updatePlayerPosition(delta) {
    velocity.x -= velocity.x * 10.0 * delta;
    velocity.z -= velocity.z * 10.0 * delta;
    velocity.y -= 9.8 * 5 * delta; // Gravidade

    direction.z = Number(moveForward) - Number(moveBackward);
    direction.x = Number(moveRight) - Number(moveLeft);
    direction.normalize();

    const speed = isRunning ? 15 : 7;

    if (moveForward || moveBackward) velocity.z -= direction.z * speed * delta;
    if (moveLeft || moveRight) velocity.x -= direction.x * speed * delta;

    // Aplicar movimento
    const moveX = velocity.x * delta;
    const moveZ = velocity.z * delta;
    
    camera.position.x += Math.sin(camera.rotation.y) * moveZ;
    camera.position.z += Math.cos(camera.rotation.y) * moveZ;
    camera.position.x -= Math.cos(camera.rotation.y) * moveX;
    camera.position.z += Math.sin(camera.rotation.y) * moveX;

    // Chão
    if (camera.position.y < 1.6) {
        velocity.y = 0;
        camera.position.y = 1.6;
        canJump = true;
    }

    camera.position.y += velocity.y * delta;

    // Atualizar UI
    const pos = camera.position;
    document.getElementById('position').textContent = 
        `Posição: (${pos.x.toFixed(1)}, ${pos.y.toFixed(1)}, ${pos.z.toFixed(1)})`;
    
    // Distância de Sofia
    const distanceToSofia = camera.position.distanceTo(sofia.position);
    document.getElementById('distance').textContent = 
        `Distância de Sofia: ${distanceToSofia.toFixed(1)}m`;
    
    // Mostrar indicador de proximidade
    const proximityIndicator = document.getElementById('proximity-indicator');
    if (distanceToSofia < 5) {
        proximityIndicator.style.display = 'block';
    } else {
        proximityIndicator.style.display = 'none';
    }
}

function animate() {
    requestAnimationFrame(animate);

    const time = performance.now();
    const delta = (time - prevTime) / 1000;

    updatePlayerPosition(delta);

    // Sofia sempre olha para o player
    if (sofia) {
        sofia.lookAt(camera.position);
        // Apenas rotação Y (não inclinar)
        sofia.rotation.x = 0;
        sofia.rotation.z = 0;
    }

    renderer.render(scene, camera);
    prevTime = time;
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}
