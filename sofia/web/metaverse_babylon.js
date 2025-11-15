// =====================================================
// Metaverso 3D - Sofia (Babylon.js + NPCs + Chat)
// Integração completa: jogo3d + Sofia WebSocket
// Autor: Reginaldo + Luzia 💙
// =====================================================

let engine, scene, camera, player, shadowGen;
let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false, isRunning = false;
let currentInteractable = null, canInteract = false, gameStarted = false;
let npcs = [], missions = [], activeMission = null;
let dayNightCycle = null;
let helpVisible = true;

// Configurações de NPCs
const NPC_DEFINITIONS = [
  {
    id: 'sofia',
    name: 'Sofia 🌸',
    anchor: new BABYLON.Vector3(-6, 0, 4),
    tint: new BABYLON.Color3(0.6, 0.3, 0.8),
    outfit: new BABYLON.Color3(0.2, 0.2, 0.6),
    hair: new BABYLON.Color3(0.2, 0.1, 0.1),
    roamRadius: 2.5,
    walkSpeed: 0.75,
    lines: [
      '🌸 Sofia: Olá! Eu sou a assistente virtual desse metaverso. Posso responder suas perguntas!',
      '🌸 Sofia: Use o chat para conversar comigo. Estou aqui para ajudar!',
      '🌸 Sofia: Explore o mundo e conheça outros NPCs!'
    ]
  },
  {
    id: 'bruno',
    name: 'Bruno 🔧',
    anchor: new BABYLON.Vector3(5, 0, -3),
    tint: new BABYLON.Color3(0.25, 0.5, 0.85),
    outfit: new BABYLON.Color3(0.15, 0.35, 0.55),
    hair: new BABYLON.Color3(0.05, 0.05, 0.05),
    roamRadius: 3.5,
    walkSpeed: 0.9,
    lines: [
      '🔧 Bruno: Estou construindo drones exploradores. Preciso de cristais para calibrá-los.',
      '🔧 Bruno: Há um portal antigo a oeste. Ele leva a memórias guardadas.'
    ]
  },
  {
    id: 'ana',
    name: 'Ana 📚',
    anchor: new BABYLON.Vector3(-2, 0, -8),
    tint: new BABYLON.Color3(0.85, 0.35, 0.35),
    outfit: new BABYLON.Color3(0.45, 0.15, 0.2),
    hair: new BABYLON.Color3(0.3, 0.12, 0.12),
    roamRadius: 4,
    walkSpeed: 0.65,
    lines: [
      '📚 Ana: Coleciono histórias desse metaverso. Pode me contar algo que aprendeu hoje?',
      '📚 Ana: Se conversar com Sofia, pergunte sobre programação!'
    ]
  },
  {
    id: 'kai',
    name: 'Kai 🧭',
    anchor: new BABYLON.Vector3(9, 0, 6),
    tint: new BABYLON.Color3(0.2, 0.8, 0.6),
    outfit: new BABYLON.Color3(0.1, 0.45, 0.35),
    hair: new BABYLON.Color3(0.1, 0.2, 0.15),
    roamRadius: 5,
    walkSpeed: 1.0,
    lines: [
      '🧭 Kai: Eu mapeio cada canto desse lugar.',
      '🧭 Kai: Continue caminhando, o mundo responde a exploradores curiosos.'
    ]
  }
];

const SPAWN_POINT = new BABYLON.Vector3(0, 0, 10);

// =====================================================
// INICIALIZAÇÃO
// =====================================================
function initMetaverse() {
    const modal = document.getElementById('metaverse-modal');
    const container = document.getElementById('metaverse-container');
    
    if (!modal || !container) {
        console.error('❌ Modal ou container não encontrado');
        return;
    }

    // Criar canvas se não existir
    let canvas = container.querySelector('#renderCanvas');
    if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = 'renderCanvas';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.display = 'block';
        canvas.style.touchAction = 'none';
        container.appendChild(canvas);
    }

    // Inicializar painéis móveis
    initializeDraggablePanels();

    gameStarted = true;

    engine = new BABYLON.Engine(canvas, true, { 
        preserveDrawingBuffer: true, 
        stencil: true, 
        antialias: true 
    });

    createScene(canvas).then(createdScene => {
        scene = createdScene;
        
        engine.runRenderLoop(() => {
            if (scene) {
                scene.render();
            }
        });

        window.addEventListener('resize', () => {
            engine.resize();
        });

        console.log('✅ Metaverso Babylon.js inicializado');
    });
}

// =====================================================
// PAINÉIS MÓVEIS (Drag and Drop)
// =====================================================
function initializeDraggablePanels() {
    const panels = document.querySelectorAll('.metaverse-panel');
    
    panels.forEach(panel => {
        const header = panel.querySelector('.panel-header');
        const minimizeBtn = panel.querySelector('.panel-btn.minimize');
        const closeBtn = panel.querySelector('.panel-btn.close');
        
        let isDragging = false;
        let currentX, currentY, initialX, initialY;
        let xOffset = 0, yOffset = 0;

        // Drag functionality
        header.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        // Touch support
        header.addEventListener('touchstart', dragStart);
        document.addEventListener('touchmove', drag);
        document.addEventListener('touchend', dragEnd);

        function dragStart(e) {
            // Não arrastar se clicar nos botões
            if (e.target.classList.contains('panel-btn')) return;
            
            if (e.type === "touchstart") {
                initialX = e.touches[0].clientX - xOffset;
                initialY = e.touches[0].clientY - yOffset;
            } else {
                initialX = e.clientX - xOffset;
                initialY = e.clientY - yOffset;
            }

            if (e.target === header || header.contains(e.target)) {
                isDragging = true;
                panel.style.zIndex = 1000; // Trazer para frente
            }
        }

        function drag(e) {
            if (isDragging) {
                e.preventDefault();
                
                if (e.type === "touchmove") {
                    currentX = e.touches[0].clientX - initialX;
                    currentY = e.touches[0].clientY - initialY;
                } else {
                    currentX = e.clientX - initialX;
                    currentY = e.clientY - initialY;
                }

                xOffset = currentX;
                yOffset = currentY;

                setTranslate(currentX, currentY, panel);
            }
        }

        function dragEnd() {
            if (isDragging) {
                initialX = currentX;
                initialY = currentY;
                isDragging = false;
                panel.style.zIndex = 4; // Voltar ao z-index normal
            }
        }

        function setTranslate(xPos, yPos, el) {
            el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
        }

        // Minimize functionality
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                panel.classList.toggle('minimized');
                minimizeBtn.textContent = panel.classList.contains('minimized') ? '+' : '−';
            });
        }

        // Close functionality
        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                panel.style.display = 'none';
                
                // Adicionar botão para reabrir (opcional)
                showReopenButton(panel);
            });
        }
    });
}

function showReopenButton(panel) {
    // Criar botão flutuante para reabrir painel
    const reopenBtn = document.createElement('button');
    reopenBtn.className = 'reopen-panel-btn';
    reopenBtn.innerHTML = `📋 ${panel.querySelector('.panel-title').textContent}`;
    reopenBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(44, 182, 125, 0.9);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        z-index: 1000;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
    `;
    
    reopenBtn.addEventListener('mouseenter', () => {
        reopenBtn.style.transform = 'scale(1.05)';
    });
    
    reopenBtn.addEventListener('mouseleave', () => {
        reopenBtn.style.transform = 'scale(1)';
    });
    
    reopenBtn.addEventListener('click', () => {
        panel.style.display = 'block';
        reopenBtn.remove();
    });
    
    document.body.appendChild(reopenBtn);
}

// =====================================================
// CRIAÇÃO DA CENA
// =====================================================
async function createScene(canvas) {
    const scene = new BABYLON.Scene(engine);
    scene.clearColor = new BABYLON.Color4(0.55, 0.7, 0.9, 1);

    const env = scene.createDefaultEnvironment({
        createSkybox: true,
        skyboxSize: 200,
        enableGroundShadow: true,
        groundSize: 120,
        skyboxColor: new BABYLON.Color3(0.3, 0.45, 0.65)
    });
    
    if (env && env.ground) {
        env.ground.checkCollisions = true;
        env.ground.receiveShadows = true;
    }

    scene.gravity = new BABYLON.Vector3(0, -0.45, 0);
    scene.collisionsEnabled = true;

    // Câmera
    camera = new BABYLON.UniversalCamera('camera', SPAWN_POINT.add(new BABYLON.Vector3(0, 1.7, 0)), scene);
    camera.setTarget(SPAWN_POINT);
    camera.attachControl(canvas, true);
    camera.applyGravity = true;
    camera.checkCollisions = true;
    camera.ellipsoid = new BABYLON.Vector3(0.4, 0.95, 0.4);
    camera.ellipsoidOffset = new BABYLON.Vector3(0, 0.45, 0);
    camera.minZ = 0.05;
    camera.speed = 0.22;
    camera.angularSensibility = 1400;

    // Iluminação
    const hemi = new BABYLON.HemisphericLight('hemi', new BABYLON.Vector3(0, 1, 0), scene);
    hemi.intensity = 0.7;

    const dirLight = new BABYLON.DirectionalLight('sun', new BABYLON.Vector3(-1, -1.5, -0.75), scene);
    dirLight.position = new BABYLON.Vector3(20, 35, 20);
    dirLight.intensity = 1.1;

    shadowGen = new BABYLON.ShadowGenerator(2048, dirLight);
    shadowGen.useExponentialShadowMap = true;

    // Criar mundo
    createWorld(scene);
    createLandmarks(scene);

    const characterData = createCharacters(scene);
    npcs = characterData.npcs;
    player = characterData.player;

    setupMissions();
    setupControls(scene);
    createUI(scene);

    scene.registerBeforeRender(() => {
        const deltaSec = engine.getDeltaTime() / 1000;
        updatePlayerRepresentation();
        updateNPCs(deltaSec);
        checkInteraction();
    });

    return scene;
}

// =====================================================
// MUNDO
// =====================================================
function createWorld(scene) {
    const groundMat = new BABYLON.StandardMaterial('groundMain', scene);
    groundMat.diffuseColor = new BABYLON.Color3(0.32, 0.55, 0.32);
    groundMat.specularColor = BABYLON.Color3.Black();

    const meadow = BABYLON.MeshBuilder.CreateGround('meadow', { width: 90, height: 90 }, scene);
    meadow.position.y = 0.005;
    meadow.material = groundMat;
    meadow.receiveShadows = true;
    meadow.isPickable = false;

    const plaza = BABYLON.MeshBuilder.CreateGround('centralPlaza', { width: 30, height: 30 }, scene);
    plaza.position = new BABYLON.Vector3(0, 0.01, 0);
    const plazaMat = new BABYLON.StandardMaterial('plazaMat', scene);
    plazaMat.diffuseColor = new BABYLON.Color3(0.7, 0.65, 0.6);
    plaza.material = plazaMat;
    plaza.receiveShadows = true;

    // Árvores decorativas
    const trunkMat = new BABYLON.StandardMaterial('treeTrunkMat', scene);
    trunkMat.diffuseColor = new BABYLON.Color3(0.36, 0.23, 0.1);

    const leafMat = new BABYLON.StandardMaterial('leafMat', scene);
    leafMat.diffuseColor = new BABYLON.Color3(0.18, 0.45, 0.2);

    for (let i = 0; i < 15; i++) {
        const angle = (i / 15) * Math.PI * 2;
        const radius = 25 + Math.random() * 15;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;

        const trunk = BABYLON.MeshBuilder.CreateCylinder(`trunk${i}`, {
            height: 3,
            diameter: 0.5
        }, scene);
        trunk.position = new BABYLON.Vector3(x, 1.5, z);
        trunk.material = trunkMat;
        trunk.checkCollisions = true;

        const leaves = BABYLON.MeshBuilder.CreateSphere(`leaves${i}`, {
            diameter: 4
        }, scene);
        leaves.position = new BABYLON.Vector3(x, 4, z);
        leaves.material = leafMat;
        leaves.checkCollisions = false;

        if (shadowGen) {
            shadowGen.addShadowCaster(trunk);
        }
    }
}

function createLandmarks(scene) {
    // Cristal central
    const crystalMat = new BABYLON.StandardMaterial('crystalMat', scene);
    crystalMat.diffuseColor = new BABYLON.Color3(0.3, 0.8, 0.9);
    crystalMat.emissiveColor = new BABYLON.Color3(0.1, 0.3, 0.4);
    crystalMat.alpha = 0.8;

    const crystal = BABYLON.MeshBuilder.CreateCylinder('crystal', {
        height: 4,
        diameterTop: 0.2,
        diameterBottom: 1
    }, scene);
    crystal.position = new BABYLON.Vector3(0, 2, 0);
    crystal.material = crystalMat;
    crystal.checkCollisions = true;

    // Plataformas flutuantes
    const platformMat = new BABYLON.StandardMaterial('platformMat', scene);
    platformMat.diffuseColor = new BABYLON.Color3(0.5, 0.4, 0.6);

    for (let i = 0; i < 5; i++) {
        const platform = BABYLON.MeshBuilder.CreateBox(`platform${i}`, {
            width: 3,
            height: 0.3,
            depth: 3
        }, scene);
        
        const angle = (i / 5) * Math.PI * 2;
        platform.position = new BABYLON.Vector3(
            Math.cos(angle) * 12,
            2 + Math.sin(i) * 1.5,
            Math.sin(angle) * 12
        );
        platform.material = platformMat;
        platform.checkCollisions = true;

        if (shadowGen) {
            shadowGen.addShadowCaster(platform);
        }
    }
}

// =====================================================
// PERSONAGENS
// =====================================================
function createCharacters(scene) {
    const npcArray = NPC_DEFINITIONS.map(def => createNPC(scene, def));
    const playerRep = createPlayerRepresentation(scene);
    return { npcs: npcArray, player: playerRep };
}

function createNPC(scene, def) {
    // Container principal
    const npcRoot = new BABYLON.TransformNode(`${def.id}_root`, scene);
    npcRoot.position = def.anchor.clone();

    // Materiais
    const skinMat = new BABYLON.StandardMaterial(`${def.id}_skinMat`, scene);
    skinMat.diffuseColor = def.tint;
    skinMat.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2);

    const outfitMat = new BABYLON.StandardMaterial(`${def.id}_outfitMat`, scene);
    outfitMat.diffuseColor = def.outfit;

    const hairMat = new BABYLON.StandardMaterial(`${def.id}_hairMat`, scene);
    hairMat.diffuseColor = def.hair;

    // CORPO HUMANOIDE DETALHADO

    // Torso
    const torso = BABYLON.MeshBuilder.CreateCylinder(`${def.id}_torso`, {
        height: 0.8,
        diameterTop: 0.4,
        diameterBottom: 0.45
    }, scene);
    torso.position.y = 1.2;
    torso.material = outfitMat;
    torso.parent = npcRoot;

    // Cabeça
    const head = BABYLON.MeshBuilder.CreateSphere(`${def.id}_head`, {
        diameter: 0.35,
        segments: 16
    }, scene);
    head.position.y = 1.75;
    head.material = skinMat;
    head.parent = npcRoot;

    // Cabelo (elipse)
    const hair = BABYLON.MeshBuilder.CreateSphere(`${def.id}_hair`, {
        diameterX: 0.38,
        diameterY: 0.3,
        diameterZ: 0.38,
        segments: 12
    }, scene);
    hair.position.y = 1.9;
    hair.material = hairMat;
    hair.parent = npcRoot;

    // Olhos
    const eyeMat = new BABYLON.StandardMaterial(`${def.id}_eyeMat`, scene);
    eyeMat.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.1);
    eyeMat.emissiveColor = new BABYLON.Color3(0.3, 0.3, 0.3);

    const leftEye = BABYLON.MeshBuilder.CreateSphere(`${def.id}_leftEye`, {
        diameter: 0.06
    }, scene);
    leftEye.position = new BABYLON.Vector3(-0.08, 1.77, 0.15);
    leftEye.material = eyeMat;
    leftEye.parent = npcRoot;

    const rightEye = BABYLON.MeshBuilder.CreateSphere(`${def.id}_rightEye`, {
        diameter: 0.06
    }, scene);
    rightEye.position = new BABYLON.Vector3(0.08, 1.77, 0.15);
    rightEye.material = eyeMat;
    rightEye.parent = npcRoot;

    // Braços
    const leftArm = BABYLON.MeshBuilder.CreateCylinder(`${def.id}_leftArm`, {
        height: 0.7,
        diameter: 0.12
    }, scene);
    leftArm.position = new BABYLON.Vector3(-0.3, 1.15, 0);
    leftArm.rotation.z = Math.PI / 8;
    leftArm.material = outfitMat;
    leftArm.parent = npcRoot;

    const rightArm = BABYLON.MeshBuilder.CreateCylinder(`${def.id}_rightArm`, {
        height: 0.7,
        diameter: 0.12
    }, scene);
    rightArm.position = new BABYLON.Vector3(0.3, 1.15, 0);
    rightArm.rotation.z = -Math.PI / 8;
    rightArm.material = outfitMat;
    rightArm.parent = npcRoot;

    // Mãos
    const leftHand = BABYLON.MeshBuilder.CreateSphere(`${def.id}_leftHand`, {
        diameter: 0.1
    }, scene);
    leftHand.position = new BABYLON.Vector3(-0.35, 0.75, 0);
    leftHand.material = skinMat;
    leftHand.parent = npcRoot;

    const rightHand = BABYLON.MeshBuilder.CreateSphere(`${def.id}_rightHand`, {
        diameter: 0.1
    }, scene);
    rightHand.position = new BABYLON.Vector3(0.35, 0.75, 0);
    rightHand.material = skinMat;
    rightHand.parent = npcRoot;

    // Pernas
    const leftLeg = BABYLON.MeshBuilder.CreateCylinder(`${def.id}_leftLeg`, {
        height: 0.8,
        diameter: 0.15
    }, scene);
    leftLeg.position = new BABYLON.Vector3(-0.12, 0.4, 0);
    leftLeg.material = outfitMat;
    leftLeg.parent = npcRoot;

    const rightLeg = BABYLON.MeshBuilder.CreateCylinder(`${def.id}_rightLeg`, {
        height: 0.8,
        diameter: 0.15
    }, scene);
    rightLeg.position = new BABYLON.Vector3(0.12, 0.4, 0);
    rightLeg.material = outfitMat;
    rightLeg.parent = npcRoot;

    // Pés
    const leftFoot = BABYLON.MeshBuilder.CreateBox(`${def.id}_leftFoot`, {
        width: 0.12,
        height: 0.08,
        depth: 0.2
    }, scene);
    leftFoot.position = new BABYLON.Vector3(-0.12, 0.04, 0.05);
    leftFoot.material = hairMat;
    leftFoot.parent = npcRoot;

    const rightFoot = BABYLON.MeshBuilder.CreateBox(`${def.id}_rightFoot`, {
        width: 0.12,
        height: 0.08,
        depth: 0.2
    }, scene);
    rightFoot.position = new BABYLON.Vector3(0.12, 0.04, 0.05);
    rightFoot.material = hairMat;
    rightFoot.parent = npcRoot;

    // Nome tag
    createNameTag(npcRoot, def.name, scene);

    // Adicionar sombras
    if (shadowGen) {
        shadowGen.addShadowCaster(torso);
        shadowGen.addShadowCaster(head);
        shadowGen.addShadowCaster(leftArm);
        shadowGen.addShadowCaster(rightArm);
        shadowGen.addShadowCaster(leftLeg);
        shadowGen.addShadowCaster(rightLeg);
    }

    // Colisão no torso
    torso.checkCollisions = true;

    return {
        id: def.id,
        name: def.name,
        mesh: npcRoot,
        head: head,
        leftArm: leftArm,
        rightArm: rightArm,
        leftLeg: leftLeg,
        rightLeg: rightLeg,
        anchor: def.anchor,
        roamRadius: def.roamRadius,
        walkSpeed: def.walkSpeed,
        lines: def.lines,
        currentLine: 0,
        moveTimer: 0,
        targetPos: null
    };
}

function createPlayerRepresentation(scene) {
    const playerMat = new BABYLON.StandardMaterial('playerMat', scene);
    playerMat.diffuseColor = new BABYLON.Color3(0.2, 0.8, 0.6);

    const playerBody = BABYLON.MeshBuilder.CreateCylinder('playerBody', {
        height: 1.4,
        diameter: 0.5
    }, scene);
    playerBody.position = SPAWN_POINT.clone();
    playerBody.position.y = 0.7;
    playerBody.material = playerMat;
    playerBody.isVisible = false; // Invisível (primeira pessoa)

    return playerBody;
}

function createNameTag(parent, text, scene) {
    const plane = BABYLON.MeshBuilder.CreatePlane(`nameTag_${text}`, {
        width: 2,
        height: 0.5
    }, scene);
    plane.position.y = 1.2;
    plane.parent = parent;
    plane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;

    const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateForMesh(plane);
    const label = new BABYLON.GUI.TextBlock();
    label.text = text;
    label.color = 'white';
    label.fontSize = 48;
    label.outlineColor = 'black';
    label.outlineWidth = 4;
    advancedTexture.addControl(label);
}

// =====================================================
// CONTROLES
// =====================================================
function setupControls(scene) {
    // Controles de teclado
    const keyState = {
        w: false,
        s: false,
        a: false,
        d: false,
        shift: false
    };

    scene.onKeyboardObservable.add((kbInfo) => {
        const key = kbInfo.event.key.toLowerCase();
        const pressed = (kbInfo.type === BABYLON.KeyboardEventTypes.KEYDOWN);

        switch (key) {
            case 'w': 
                keyState.w = pressed;
                moveForward = pressed;
                break;
            case 's': 
                keyState.s = pressed;
                moveBackward = pressed;
                break;
            case 'a': 
                keyState.a = pressed;
                moveLeft = pressed;
                break;
            case 'd': 
                keyState.d = pressed;
                moveRight = pressed;
                break;
            case 'shift': 
                keyState.shift = pressed;
                isRunning = pressed;
                break;
            case 'e':
                if (pressed && currentInteractable) {
                    interactWithNPC(currentInteractable);
                }
                break;
        }
    });

    // Atualizar movimento a cada frame
    scene.onBeforeRenderObservable.add(() => {
        updateMovement(keyState);
    });
}

function updateMovement(keyState) {
    if (!camera) return;

    const speed = isRunning ? 0.5 : 0.25;
    const moveVector = new BABYLON.Vector3(0, 0, 0);

    // Calcular direção baseado na rotação da câmera
    if (keyState.w) {
        moveVector.z += speed;
    }
    if (keyState.s) {
        moveVector.z -= speed;
    }
    if (keyState.a) {
        moveVector.x -= speed;
    }
    if (keyState.d) {
        moveVector.x += speed;
    }

    // Aplicar movimento relativo à direção da câmera
    if (moveVector.length() > 0) {
        const forward = camera.getDirection(BABYLON.Axis.Z);
        const right = camera.getDirection(BABYLON.Axis.X);
        
        forward.y = 0;
        right.y = 0;
        forward.normalize();
        right.normalize();

        const movement = forward.scale(moveVector.z).add(right.scale(moveVector.x));
        camera.position.addInPlace(movement);
    }
}

function updatePlayerRepresentation() {
    if (!player || !camera) return;
    player.position.x = camera.position.x;
    player.position.z = camera.position.z;
}

// =====================================================
// NPCs
// =====================================================
function updateNPCs(deltaSec) {
    npcs.forEach(npc => {
        if (!npc.mesh) return;

        npc.moveTimer += deltaSec;

        if (npc.moveTimer > 3) {
            npc.moveTimer = 0;
            const angle = Math.random() * Math.PI * 2;
            const dist = Math.random() * npc.roamRadius;
            npc.targetPos = new BABYLON.Vector3(
                npc.anchor.x + Math.cos(angle) * dist,
                0,
                npc.anchor.z + Math.sin(angle) * dist
            );
        }

        if (npc.targetPos) {
            const dir = npc.targetPos.subtract(npc.mesh.position);
            dir.y = 0;
            const distance = dir.length();

            if (distance > 0.1) {
                dir.normalize();
                const moveAmount = npc.walkSpeed * deltaSec;
                npc.mesh.position.addInPlace(dir.scale(moveAmount));
                
                // Rotacionar para olhar na direção do movimento
                const targetRotation = Math.atan2(dir.x, dir.z);
                npc.mesh.rotation.y = targetRotation;

                // Animação de caminhada (balançar braços e pernas)
                if (npc.leftArm && npc.rightArm && npc.leftLeg && npc.rightLeg) {
                    const walkCycle = Math.sin(Date.now() / 200) * 0.3;
                    npc.leftArm.rotation.x = walkCycle;
                    npc.rightArm.rotation.x = -walkCycle;
                    npc.leftLeg.rotation.x = -walkCycle;
                    npc.rightLeg.rotation.x = walkCycle;
                }
            } else {
                npc.targetPos = null;
                
                // Reset das posições dos membros
                if (npc.leftArm && npc.rightArm && npc.leftLeg && npc.rightLeg) {
                    npc.leftArm.rotation.x = 0;
                    npc.rightArm.rotation.x = 0;
                    npc.leftLeg.rotation.x = 0;
                    npc.rightLeg.rotation.x = 0;
                }
            }
        }

        // Fazer a cabeça olhar para o jogador se estiver próximo
        if (camera && npc.head) {
            const distToPlayer = BABYLON.Vector3.Distance(camera.position, npc.mesh.position);
            if (distToPlayer < 5) {
                const lookDir = camera.position.subtract(npc.mesh.position);
                lookDir.y = 0;
                lookDir.normalize();
                const lookAngle = Math.atan2(lookDir.x, lookDir.z);
                npc.head.rotation.y = lookAngle - npc.mesh.rotation.y;
            } else {
                npc.head.rotation.y = 0;
            }
        }
    });
}

function checkInteraction() {
    if (!camera) return;

    let closestNPC = null;
    let minDist = 3;

    npcs.forEach(npc => {
        if (!npc.mesh) return;
        const dist = BABYLON.Vector3.Distance(camera.position, npc.mesh.position);
        if (dist < minDist) {
            minDist = dist;
            closestNPC = npc;
        }
    });

    const prompt = document.getElementById('interaction-prompt');
    const promptText = document.getElementById('interaction-prompt-text');
    if (closestNPC) {
        currentInteractable = closestNPC;
        canInteract = true;
        if (prompt && promptText) {
            promptText.innerHTML = `<p>Pressione <kbd>E</kbd> para falar com ${closestNPC.name}</p>`;
            prompt.style.display = 'block';
            prompt.classList.add('interaction-active');
        }
    } else {
        currentInteractable = null;
        canInteract = false;
        if (prompt) {
            prompt.style.display = 'none';
            prompt.classList.remove('interaction-active');
        }
    }
}

function interactWithNPC(npc) {
    const dialog = document.getElementById('dialog-box');
    const dialogText = document.getElementById('dialog-box-text');
    if (!dialog || !dialogText) return;

    const line = npc.lines[npc.currentLine];
    dialogText.innerHTML = `<p>${line}</p>`;
    dialog.style.display = 'block';

    npc.currentLine = (npc.currentLine + 1) % npc.lines.length;

    // Auto-fechar após 6 segundos (aumentado para dar tempo de ler)
    setTimeout(() => {
        if (dialog.style.display === 'block' && !dialog.classList.contains('minimized')) {
            dialog.style.display = 'none';
        }
    }, 6000);

    // Se for Sofia, enviar mensagem pelo chat
    if (npc.id === 'sofia') {
        sendMetaverseMessage(`Olá Sofia! ${line}`);
    }
}

// =====================================================
// UI E MISSÕES
// =====================================================
function createUI(scene) {
    const missionTracker = document.getElementById('mission-tracker');
    const controlsHelp = document.getElementById('controls-help');

    if (missionTracker) {
        renderMissionTracker();
    }

    if (controlsHelp) {
        controlsHelp.innerHTML = `
            <h3>🎮 Controles</h3>
            <p><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> - Mover</p>
            <p><kbd>Mouse</kbd> - Olhar</p>
            <p><kbd>Shift</kbd> - Correr</p>
            <p><kbd>E</kbd> - Interagir</p>
            <p><kbd>ESC</kbd> - Menu</p>
        `;
    }
}

function setupMissions() {
    missions = [
        {
            id: 'meet_sofia',
            title: 'Conhecer Sofia',
            description: 'Fale com a Sofia no jardim',
            completed: false,
            npcId: 'sofia'
        },
        {
            id: 'explore',
            title: 'Explorar',
            description: 'Visite 3 NPCs diferentes',
            completed: false
        }
    ];
    activeMission = missions[0];
}

function renderMissionTracker() {
    const tracker = document.getElementById('mission-tracker');
    if (!tracker || !activeMission) return;

    tracker.innerHTML = `
        <h3>📋 Missão Ativa</h3>
        <p><strong>${activeMission.title}</strong></p>
        <p>${activeMission.description}</p>
    `;
}

// =====================================================
// CHAT INTEGRADO COM WEBSOCKET
// =====================================================
function sendMetaverseMessage(message) {
    if (!message || !message.trim()) return;

    const messagesContainer = document.getElementById('metaverse-messages');
    if (!messagesContainer) return;

    // Adicionar mensagem do usuário
    const userMsg = document.createElement('div');
    userMsg.className = 'metaverse-message user';
    userMsg.textContent = '👤 ' + message;
    messagesContainer.appendChild(userMsg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Mostrar status
    const statusDiv = document.getElementById('metaverse-status');
    const statusText = document.getElementById('metaverse-status-text');
    if (statusDiv && statusText) {
        statusText.innerHTML = '<p style="color: #FFB84D; margin: 0;">🤔 Sofia está pensando...</p>';
        statusDiv.style.display = 'block';
        statusDiv.classList.add('active');
    }

    // Enviar via WebSocket (se existir conexão global)
    if (typeof ws !== 'undefined' && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'message',
            content: message,
            user_name: 'Usuário',
            metaverse: true
        }));

        // Mensagem temporária
        setTimeout(() => {
            const sofiaMsg = document.createElement('div');
            sofiaMsg.className = 'metaverse-message sofia';
            sofiaMsg.textContent = '🌸 Sofia está pensando...';
            sofiaMsg.id = 'temp-processing-msg';
            messagesContainer.appendChild(sofiaMsg);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 300);
    } else {
        // Fallback: resposta simulada
        setTimeout(() => {
            const statusDiv = document.getElementById('metaverse-status');
            const statusText = document.getElementById('metaverse-status-text');
            if (statusDiv && statusText) {
                statusText.innerHTML = '<p style="color: #2cb67d; margin: 0;">✨ Sofia está online</p>';
                statusDiv.classList.remove('active');
            }
            const sofiaMsg = document.createElement('div');
            sofiaMsg.className = 'metaverse-message sofia';
            sofiaMsg.textContent = '🌸 Sofia: Olá! Estou aqui para ajudar. Explore o metaverso!';
            messagesContainer.appendChild(sofiaMsg);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 1500);
    }
}

// =====================================================
// LIMPEZA
// =====================================================
function closeMetaverse() {
    if (engine) {
        engine.stopRenderLoop();
        engine.dispose();
    }
    gameStarted = false;
    console.log('✅ Metaverso Babylon.js fechado');
}

// Exportar para uso global
window.initMetaverse = initMetaverse;
window.closeMetaverse = closeMetaverse;
window.sendMetaverseMessage = sendMetaverseMessage;
