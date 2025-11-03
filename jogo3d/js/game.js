// Configuração do jogo
const canvas = document.getElementById('renderCanvas');
const startScreen = document.getElementById('start-screen');
const loadingScreen = document.getElementById('loading-screen');
const startButton = document.getElementById('start-button');
const interactionPrompt = document.getElementById('interaction-prompt');

let engine, scene, camera, player, sofia;
let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
let isRunning = false;
let canInteract = false;
let gameStarted = false;

// Botão de iniciar
startButton.addEventListener('click', () => {
    startScreen.style.display = 'none';
    loadingScreen.style.display = 'flex';
    initGame();
});

async function initGame() {
    if (gameStarted) return;
    gameStarted = true;
    
    console.log('Iniciando jogo...');
    // Criar engine
    engine = new BABYLON.Engine(canvas, true);
    console.log('Engine criada');
    
    // Criar cena
    scene = createScene();
    console.log('Cena criada');
    
    // Aguardar tudo carregar
    await scene.whenReadyAsync();
    console.log('Cena pronta!');
    
    // Esconder loading screen
    setTimeout(() => {
        loadingScreen.style.display = 'none';
        console.log('Jogo iniciado!');
    }, 1000);
    
    // Renderizar
    engine.runRenderLoop(() => {
        scene.render();
    });
    
    // Resize
    window.addEventListener('resize', () => {
        engine.resize();
    });
}

function createScene() {
    const scene = new BABYLON.Scene(engine);
    scene.clearColor = new BABYLON.Color3(0.5, 0.7, 0.9);
    
    // Gravidade
    scene.gravity = new BABYLON.Vector3(0, -0.15, 0);
    scene.collisionsEnabled = true;
    
    // Câmera Universal (primeira pessoa)
    camera = new BABYLON.UniversalCamera(
        'camera',
        new BABYLON.Vector3(0, 1.6, 8),
        scene
    );
    camera.setTarget(new BABYLON.Vector3(0, 1.6, 0));
    camera.attachControl(canvas, true);
    
    // Configurações de câmera
    camera.speed = 0.2;
    camera.angularSensibility = 2000;
    camera.applyGravity = true;
    camera.checkCollisions = true;
    camera.ellipsoid = new BABYLON.Vector3(0.5, 1, 0.5);
    camera.minZ = 0.1;
    
    // Iluminação
    const light = new BABYLON.HemisphericLight(
        'light',
        new BABYLON.Vector3(0, 1, 0),
        scene
    );
    light.intensity = 0.7;
    
    // Luz direcional
    const dirLight = new BABYLON.DirectionalLight(
        'dirLight',
        new BABYLON.Vector3(-1, -2, -1),
        scene
    );
    dirLight.position = new BABYLON.Vector3(10, 20, 10);
    dirLight.intensity = 0.5;
    
    // Criar o quarto
    createRoom(scene);
    
    // Criar móveis
    createFurniture(scene);
    
    // Criar personagens
    createCharacters(scene);
    
    // Controles
    setupControls(scene);
    
    // Update loop
    scene.registerBeforeRender(() => {
        updateMovement();
        checkInteraction();
    });
    
    return scene;
}

function createRoom(scene) {
    // Chão
    const ground = BABYLON.MeshBuilder.CreateGround(
        'ground',
        { width: 10, height: 10 },
        scene
    );
    const groundMat = new BABYLON.StandardMaterial('groundMat', scene);
    groundMat.diffuseColor = new BABYLON.Color3(0.6, 0.5, 0.4); // Cor de madeira
    groundMat.specularColor = new BABYLON.Color3(0.1, 0.1, 0.1);
    ground.material = groundMat;
    ground.checkCollisions = true;
    ground.position.y = 0;
    
    // Paredes
    const wallHeight = 3;
    const wallThickness = 0.2;
    
    // Parede norte
    const wallNorth = BABYLON.MeshBuilder.CreateBox(
        'wallNorth',
        { width: 10, height: wallHeight, depth: wallThickness },
        scene
    );
    wallNorth.position = new BABYLON.Vector3(0, wallHeight / 2, -5);
    
    // Parede sul
    const wallSouth = BABYLON.MeshBuilder.CreateBox(
        'wallSouth',
        { width: 10, height: wallHeight, depth: wallThickness },
        scene
    );
    wallSouth.position = new BABYLON.Vector3(0, wallHeight / 2, 5);
    
    // Parede leste
    const wallEast = BABYLON.MeshBuilder.CreateBox(
        'wallEast',
        { width: wallThickness, height: wallHeight, depth: 10 },
        scene
    );
    wallEast.position = new BABYLON.Vector3(5, wallHeight / 2, 0);
    
    // Parede oeste
    const wallWest = BABYLON.MeshBuilder.CreateBox(
        'wallWest',
        { width: wallThickness, height: wallHeight, depth: 10 },
        scene
    );
    wallWest.position = new BABYLON.Vector3(-5, wallHeight / 2, 0);
    
    // Material das paredes
    const wallMat = new BABYLON.StandardMaterial('wallMat', scene);
    wallMat.diffuseColor = new BABYLON.Color3(0.9, 0.9, 0.85);
    
    [wallNorth, wallSouth, wallEast, wallWest].forEach(wall => {
        wall.material = wallMat;
        wall.checkCollisions = true;
    });
    
    // Teto
    const ceiling = BABYLON.MeshBuilder.CreateGround(
        'ceiling',
        { width: 10, height: 10 },
        scene
    );
    ceiling.position.y = wallHeight;
    ceiling.rotation.z = Math.PI;
    const ceilingMat = new BABYLON.StandardMaterial('ceilingMat', scene);
    ceilingMat.diffuseColor = new BABYLON.Color3(1, 1, 1);
    ceiling.material = ceilingMat;
}

function createFurniture(scene) {
    // Cama
    const bed = BABYLON.MeshBuilder.CreateBox(
        'bed',
        { width: 2, height: 0.5, depth: 2.5 },
        scene
    );
    bed.position = new BABYLON.Vector3(-3, 0.25, -3);
    const bedMat = new BABYLON.StandardMaterial('bedMat', scene);
    bedMat.diffuseColor = new BABYLON.Color3(0.5, 0.3, 0.8); // Roxo
    bed.material = bedMat;
    bed.checkCollisions = true;
    
    // Cabeceira da cama
    const headboard = BABYLON.MeshBuilder.CreateBox(
        'headboard',
        { width: 2, height: 1, depth: 0.2 },
        scene
    );
    headboard.position = new BABYLON.Vector3(-3, 0.75, -4.15);
    headboard.material = bedMat;
    headboard.checkCollisions = true;
    
    // Mesa
    const table = BABYLON.MeshBuilder.CreateBox(
        'table',
        { width: 1.5, height: 0.1, depth: 0.8 },
        scene
    );
    table.position = new BABYLON.Vector3(3, 0.7, -3);
    const tableMat = new BABYLON.StandardMaterial('tableMat', scene);
    tableMat.diffuseColor = new BABYLON.Color3(0.4, 0.3, 0.2);
    table.material = tableMat;
    table.checkCollisions = true;
    
    // Pernas da mesa (4)
    for (let i = 0; i < 4; i++) {
        const leg = BABYLON.MeshBuilder.CreateCylinder(
            'tableLeg' + i,
            { height: 0.7, diameter: 0.08 },
            scene
        );
        const xOffset = i % 2 === 0 ? -0.6 : 0.6;
        const zOffset = i < 2 ? -0.3 : 0.3;
        leg.position = new BABYLON.Vector3(3 + xOffset, 0.35, -3 + zOffset);
        leg.material = tableMat;
        leg.checkCollisions = true;
    }
    
    // Cadeira
    const chair = BABYLON.MeshBuilder.CreateBox(
        'chairSeat',
        { width: 0.5, height: 0.1, depth: 0.5 },
        scene
    );
    chair.position = new BABYLON.Vector3(3, 0.5, -2);
    const chairMat = new BABYLON.StandardMaterial('chairMat', scene);
    chairMat.diffuseColor = new BABYLON.Color3(0.3, 0.2, 0.15);
    chair.material = chairMat;
    chair.checkCollisions = true;
    
    // Encosto da cadeira
    const chairBack = BABYLON.MeshBuilder.CreateBox(
        'chairBack',
        { width: 0.5, height: 0.7, depth: 0.1 },
        scene
    );
    chairBack.position = new BABYLON.Vector3(3, 0.85, -1.75);
    chairBack.material = chairMat;
    chairBack.checkCollisions = true;
    
    // Armário
    const wardrobe = BABYLON.MeshBuilder.CreateBox(
        'wardrobe',
        { width: 2, height: 2.5, depth: 0.8 },
        scene
    );
    wardrobe.position = new BABYLON.Vector3(3, 1.25, 3.6);
    const wardrobeMat = new BABYLON.StandardMaterial('wardrobeMat', scene);
    wardrobeMat.diffuseColor = new BABYLON.Color3(0.35, 0.25, 0.15);
    wardrobe.material = wardrobeMat;
    wardrobe.checkCollisions = true;
}

function createCharacters(scene) {
    // Sofia - Personagem humanóide
    sofia = new BABYLON.TransformNode('sofia', scene);
    
    // Corpo
    const body = BABYLON.MeshBuilder.CreateCylinder(
        'sofiaBody',
        { height: 1, diameter: 0.4 },
        scene
    );
    body.position.y = 0.5;
    const bodyMat = new BABYLON.StandardMaterial('sofiaBodyMat', scene);
    bodyMat.diffuseColor = new BABYLON.Color3(0.6, 0.3, 0.8); // Roxo
    body.material = bodyMat;
    body.parent = sofia;
    
    // Cabeça
    const head = BABYLON.MeshBuilder.CreateSphere(
        'sofiaHead',
        { diameter: 0.4 },
        scene
    );
    head.position.y = 1.2;
    const headMat = new BABYLON.StandardMaterial('sofiaHeadMat', scene);
    headMat.diffuseColor = new BABYLON.Color3(1, 0.85, 0.7); // Tom de pele
    head.material = headMat;
    head.parent = sofia;
    
    // Cabelo
    const hair = BABYLON.MeshBuilder.CreateSphere(
        'sofiaHair',
        { diameter: 0.42, slice: 0.5 },
        scene
    );
    hair.position.y = 1.35;
    const hairMat = new BABYLON.StandardMaterial('sofiaHairMat', scene);
    hairMat.diffuseColor = new BABYLON.Color3(0.2, 0.1, 0.1);
    hair.material = hairMat;
    hair.parent = sofia;
    
    // Olhos
    const leftEye = BABYLON.MeshBuilder.CreateSphere(
        'sofiaLeftEye',
        { diameter: 0.08 },
        scene
    );
    leftEye.position = new BABYLON.Vector3(-0.1, 1.25, 0.17);
    const eyeMat = new BABYLON.StandardMaterial('eyeMat', scene);
    eyeMat.diffuseColor = new BABYLON.Color3(0, 0, 0);
    leftEye.material = eyeMat;
    leftEye.parent = sofia;
    
    const rightEye = BABYLON.MeshBuilder.CreateSphere(
        'sofiaRightEye',
        { diameter: 0.08 },
        scene
    );
    rightEye.position = new BABYLON.Vector3(0.1, 1.25, 0.17);
    rightEye.material = eyeMat;
    rightEye.parent = sofia;
    
    // Braços
    const leftArm = BABYLON.MeshBuilder.CreateCylinder(
        'sofiaLeftArm',
        { height: 0.7, diameter: 0.12 },
        scene
    );
    leftArm.position = new BABYLON.Vector3(-0.3, 0.65, 0);
    leftArm.material = headMat;
    leftArm.parent = sofia;
    
    const rightArm = BABYLON.MeshBuilder.CreateCylinder(
        'sofiaRightArm',
        { height: 0.7, diameter: 0.12 },
        scene
    );
    rightArm.position = new BABYLON.Vector3(0.3, 0.65, 0);
    rightArm.material = headMat;
    rightArm.parent = sofia;
    
    // Pernas
    const leftLeg = BABYLON.MeshBuilder.CreateCylinder(
        'sofiaLeftLeg',
        { height: 0.8, diameter: 0.14 },
        scene
    );
    leftLeg.position = new BABYLON.Vector3(-0.12, -0.4, 0);
    const legMat = new BABYLON.StandardMaterial('legMat', scene);
    legMat.diffuseColor = new BABYLON.Color3(0.2, 0.2, 0.5);
    leftLeg.material = legMat;
    leftLeg.parent = sofia;
    
    const rightLeg = BABYLON.MeshBuilder.CreateCylinder(
        'sofiaRightLeg',
        { height: 0.8, diameter: 0.14 },
        scene
    );
    rightLeg.position = new BABYLON.Vector3(0.12, -0.4, 0);
    rightLeg.material = legMat;
    rightLeg.parent = sofia;
    
    // Posicionar Sofia no quarto
    sofia.position = new BABYLON.Vector3(-2, 0, 2);
    
    // Adicionar colisão
    const sofiaCollider = BABYLON.MeshBuilder.CreateCylinder(
        'sofiaCollider',
        { height: 1.6, diameter: 0.6 },
        scene
    );
    sofiaCollider.position.y = 0.8;
    sofiaCollider.isVisible = false;
    sofiaCollider.checkCollisions = true;
    sofiaCollider.parent = sofia;
    
    // Nome da Sofia (texto 3D)
    createNameTag(sofia, 'Sofia 🌸', scene);
    
    // Player (você) - Representado visualmente no spawn
    player = createPlayerRepresentation(scene);
    player.position = new BABYLON.Vector3(0, 0, 3);
}

function createPlayerRepresentation(scene) {
    // Criar representação do player (similar à Sofia mas com cores diferentes)
    const playerNode = new BABYLON.TransformNode('player', scene);
    
    // Corpo
    const body = BABYLON.MeshBuilder.CreateCylinder(
        'playerBody',
        { height: 1, diameter: 0.4 },
        scene
    );
    body.position.y = 0.5;
    const bodyMat = new BABYLON.StandardMaterial('playerBodyMat', scene);
    bodyMat.diffuseColor = new BABYLON.Color3(0.2, 0.5, 0.8); // Azul
    body.material = bodyMat;
    body.parent = playerNode;
    
    // Cabeça
    const head = BABYLON.MeshBuilder.CreateSphere(
        'playerHead',
        { diameter: 0.4 },
        scene
    );
    head.position.y = 1.2;
    const headMat = new BABYLON.StandardMaterial('playerHeadMat', scene);
    headMat.diffuseColor = new BABYLON.Color3(1, 0.85, 0.7);
    head.material = headMat;
    head.parent = playerNode;
    
    createNameTag(playerNode, 'Você', scene);
    
    return playerNode;
}

function createNameTag(parent, text, scene) {
    // Criar plano para o nome
    const plane = BABYLON.MeshBuilder.CreatePlane(
        'nameTag',
        { width: 1, height: 0.25 },
        scene
    );
    plane.position.y = 2;
    plane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
    plane.parent = parent;
    
    // Criar textura dinâmica
    const dynamicTexture = new BABYLON.DynamicTexture(
        'nameTexture',
        { width: 512, height: 128 },
        scene,
        false
    );
    
    const ctx = dynamicTexture.getContext();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, 512, 128);
    
    dynamicTexture.drawText(
        text,
        null,
        null,
        'bold 48px Arial',
        'white',
        'transparent',
        true
    );
    
    const mat = new BABYLON.StandardMaterial('nameMat', scene);
    mat.diffuseTexture = dynamicTexture;
    mat.emissiveColor = new BABYLON.Color3(1, 1, 1);
    mat.backFaceCulling = false;
    plane.material = mat;
}

function setupControls(scene) {
    scene.onKeyboardObservable.add((kbInfo) => {
        switch (kbInfo.type) {
            case BABYLON.KeyboardEventTypes.KEYDOWN:
                switch (kbInfo.event.key) {
                    case 'w':
                    case 'W':
                        moveForward = true;
                        break;
                    case 's':
                    case 'S':
                        moveBackward = true;
                        break;
                    case 'a':
                    case 'A':
                        moveLeft = true;
                        break;
                    case 'd':
                    case 'D':
                        moveRight = true;
                        break;
                    case 'Shift':
                        isRunning = true;
                        break;
                    case 'e':
                    case 'E':
                        if (canInteract) {
                            interactWithSofia();
                        }
                        break;
                }
                break;
            case BABYLON.KeyboardEventTypes.KEYUP:
                switch (kbInfo.event.key) {
                    case 'w':
                    case 'W':
                        moveForward = false;
                        break;
                    case 's':
                    case 'S':
                        moveBackward = false;
                        break;
                    case 'a':
                    case 'A':
                        moveLeft = false;
                        break;
                    case 'd':
                    case 'D':
                        moveRight = false;
                        break;
                    case 'Shift':
                        isRunning = false;
                        break;
                }
                break;
        }
    });
}

function updateMovement() {
    if (!camera) return;
    
    const speed = isRunning ? 0.3 : 0.2;
    camera.speed = speed;
}

function checkInteraction() {
    if (!sofia || !camera) return;
    
    const distance = BABYLON.Vector3.Distance(camera.position, sofia.position);
    
    if (distance < 3) {
        canInteract = true;
        interactionPrompt.style.display = 'block';
        
        // Sofia olha para o player
        sofia.lookAt(camera.position);
        sofia.rotation.x = 0;
        sofia.rotation.z = 0;
    } else {
        canInteract = false;
        interactionPrompt.style.display = 'none';
    }
}

function interactWithSofia() {
    alert('🌸 Sofia: Olá! Seja bem-vindo ao meu mundo! Este é meu quarto onde eu descanto e penso. Como você está?');
}
