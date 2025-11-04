// =====================================================
// Metaverso JS — Mundo Livre (Babylon.js)
// Autor: Reginaldo + Luzia 💙 — versão metaverso com exploração e NPCs
// =====================================================

// DOM
const canvas = document.getElementById('renderCanvas');
const startScreen = document.getElementById('start-screen');
const loadingScreen = document.getElementById('loading-screen');
const startButton = document.getElementById('start-button');
const interactionPrompt = document.getElementById('interaction-prompt');
const dialogBox = document.getElementById('dialog-box');
const missionTracker = document.getElementById('mission-tracker');

// Estado
let engine, scene, camera, player, shadowGen;
let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false, isRunning = false;
let currentInteractable = null, canInteract = false, gameStarted = false;
let npcs = [], missions = [], activeMission = null;
let ws = null; // multiplayer (stub)

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
      '🌸 Sofia: Olá viajante! Eu cuido do jardim desse mundo. Já viu as luzes da praça?\nDiga: "Oi, Sofia" se quiser que eu te acompanhe.',
      '🌸 Sofia: Sinto que há algo mágico perto das ruínas cristalinas.',
      '🌸 Sofia: Se encontrar a Ana, avise-a que tenho novas flores!'
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
      '🔧 Bruno: Há um portal antigo a oeste. Ele leva a memórias guardadas.',
      '🔧 Bruno: Se quiser ajudar, procure cristais brilhantes perto do lago.'
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
      '📚 Ana: Dizem que um cometa cruzará o céu virtual esta noite.',
      '📚 Ana: Se conversar com Sofia, pergunte sobre o projeto das flores luminescentes.'
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
      '🧭 Kai: Eu mapeio cada canto desse lugar. Quer uma missão? Procure o cristal azul e traga a mim.',
      '🧭 Kai: Existem túneis secretos sob a praça. Talvez um dia te mostre.',
      '🧭 Kai: Continue caminhando, o mundo responde a exploradores curiosos.'
    ]
  }
];

const SPAWN_POINT = new BABYLON.Vector3(0, 0, 10);

// -----------------------------------------------------
// Boot
// -----------------------------------------------------
startButton.addEventListener('click', async () => {
  startButton.disabled = true;
  startScreen.style.display = 'none';
  loadingScreen.style.display = 'flex';
  await initGame();
});

async function initGame() {
  if (gameStarted) return;
  gameStarted = true;

  engine = new BABYLON.Engine(canvas, true, { preserveDrawingBuffer: true, stencil: true, antialias: true });
  engine.displayLoadingUI();

  scene = await createScene();

  await scene.whenReadyAsync();
  engine.hideLoadingUI();
  setTimeout(() => { loadingScreen.style.display = 'none'; }, 300);

  engine.runRenderLoop(() => scene.render());
  window.addEventListener('resize', () => engine.resize());

  // connectWS("wss://SEU_ENDPOINT_AQUI");
}

// -----------------------------------------------------
// Cena
// -----------------------------------------------------
async function createScene() {
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
    env.ground.isPickable = false;
    env.ground.material.diffuseColor = new BABYLON.Color3(0.3, 0.5, 0.3);
  }

  scene.gravity = new BABYLON.Vector3(0, -0.45, 0);
  scene.collisionsEnabled = true;

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
  enablePointerLock();

  const hemi = new BABYLON.HemisphericLight('hemi', new BABYLON.Vector3(0, 1, 0), scene);
  hemi.intensity = 0.7;

  const dirLight = new BABYLON.DirectionalLight('sun', new BABYLON.Vector3(-1, -1.5, -0.75), scene);
  dirLight.position = new BABYLON.Vector3(20, 35, 20);
  dirLight.intensity = 1.1;

  shadowGen = new BABYLON.ShadowGenerator(2048, dirLight);
  shadowGen.useExponentialShadowMap = true;

  createWorld(scene);
  createLandmarks(scene);

  const characterData = createCharacters(scene);
  npcs = characterData.npcs;
  player = characterData.player;

  setupMissions();
  setupControls(scene);
  createUI(scene);

  let lastTime = Date.now();
  scene.registerBeforeRender(() => {
    const now = Date.now();
    const deltaSec = (now - lastTime) / 1000;
    lastTime = now;
    updateMovement();
    updatePlayerRepresentation();
    updateNPCs(deltaSec);
    checkInteraction();
  });

  return scene;
}

// -----------------------------------------------------
// Mundo
// -----------------------------------------------------
function createWorld(scene) {
  const groundMat = new BABYLON.StandardMaterial('groundMain', scene);
  groundMat.diffuseColor = new BABYLON.Color3(0.32, 0.55, 0.32);
  groundMat.specularColor = BABYLON.Color3.Black();

  const plaza = BABYLON.MeshBuilder.CreateGround('centralPlaza', { width: 30, height: 30 }, scene);
  plaza.position = new BABYLON.Vector3(0, 0.01, 0);
  const plazaMat = new BABYLON.StandardMaterial('plazaMat', scene);
  plazaMat.diffuseColor = new BABYLON.Color3(0.7, 0.65, 0.6);
  plaza.material = plazaMat;
  plaza.receiveShadows = true;

  const pathMat = new BABYLON.StandardMaterial('pathMat', scene);
  pathMat.diffuseColor = new BABYLON.Color3(0.6, 0.55, 0.5);

  const paths = [
    { name: 'pathNorth', position: new BABYLON.Vector3(0, 0.02, -20), width: 8, depth: 30 },
    { name: 'pathSouth', position: new BABYLON.Vector3(0, 0.02, 20), width: 8, depth: 30 },
    { name: 'pathEast', position: new BABYLON.Vector3(20, 0.02, 0), width: 30, depth: 8 },
    { name: 'pathWest', position: new BABYLON.Vector3(-20, 0.02, 0), width: 30, depth: 8 }
  ];

  paths.forEach(({ name, position, width, depth }) => {
    const strip = BABYLON.MeshBuilder.CreateGround(name, { width, height: depth }, scene);
    strip.position = position;
    strip.material = pathMat;
    strip.receiveShadows = true;
  });

  const water = BABYLON.MeshBuilder.CreateGround('lake', { width: 18, height: 12 }, scene);
  water.position = new BABYLON.Vector3(18, -0.05, -12);
  const waterMat = new BABYLON.StandardMaterial('waterMat', scene);
  waterMat.diffuseColor = new BABYLON.Color3(0.2, 0.5, 0.8);
  waterMat.alpha = 0.8;
  water.material = waterMat;
  water.isPickable = false;

  for (let i = 0; i < 30; i++) {
    const tree = BABYLON.MeshBuilder.CreateCylinder(`treeTrunk${i}`, { diameter: 0.6, height: 4 }, scene);
    const angle = Math.random() * Math.PI * 2;
    const radius = 25 + Math.random() * 20;
    tree.position = new BABYLON.Vector3(Math.cos(angle) * radius, 2, Math.sin(angle) * radius);
    const trunkMat = new BABYLON.StandardMaterial(`trunkMat${i}`, scene);
    trunkMat.diffuseColor = new BABYLON.Color3(0.36, 0.23, 0.1);
    tree.material = trunkMat;
    tree.checkCollisions = true;
    tree.receiveShadows = true;
    shadowGen.addShadowCaster(tree);

    const leaves = BABYLON.MeshBuilder.CreateSphere(`treeLeaves${i}`, { diameter: 3.8 }, scene);
    leaves.position = tree.position.add(new BABYLON.Vector3(0, 2.4, 0));
    const leafMat = new BABYLON.StandardMaterial(`leafMat${i}`, scene);
    leafMat.diffuseColor = new BABYLON.Color3(0.12 + Math.random() * 0.2, 0.4 + Math.random() * 0.3, 0.12 + Math.random() * 0.2);
    leafMat.specularColor = BABYLON.Color3.Black();
    leaves.material = leafMat;
    leaves.receiveShadows = true;
    shadowGen.addShadowCaster(leaves);
  }

  const crystalsMat = new BABYLON.StandardMaterial('crystalMat', scene);
  crystalsMat.emissiveColor = new BABYLON.Color3(0.2, 0.6, 1.0);
  crystalsMat.diffuseColor = new BABYLON.Color3(0.3, 0.4, 0.6);

  for (let i = 0; i < 6; i++) {
    const crystal = BABYLON.MeshBuilder.CreatePolyhedron(`crystal${i}`, { type: 8, size: 0.7 + Math.random() * 0.4 }, scene);
    const angle = i / 6 * Math.PI * 2;
    const radius = 6 + Math.random() * 3;
    crystal.position = new BABYLON.Vector3(Math.cos(angle) * radius, 0.7, Math.sin(angle) * radius);
    crystal.material = crystalsMat;
    crystal.receiveShadows = true;
    shadowGen.addShadowCaster(crystal);
    crystal.isPickable = false;
  }
}

function createLandmarks(scene) {
  const monument = BABYLON.MeshBuilder.CreateCylinder('monument', { diameterTop: 1.2, diameterBottom: 2.4, height: 6 }, scene);
  monument.position = new BABYLON.Vector3(0, 3, 0);
  const monumentMat = new BABYLON.StandardMaterial('monumentMat', scene);
  monumentMat.diffuseColor = new BABYLON.Color3(0.85, 0.82, 0.75);
  monument.material = monumentMat;
  monument.checkCollisions = true;
  monument.receiveShadows = true;
  shadowGen.addShadowCaster(monument);

  const portal = BABYLON.MeshBuilder.CreateTorus('portal', { diameter: 5, thickness: 0.5 }, scene);
  portal.position = new BABYLON.Vector3(-15, 2.5, -15);
  const portalMat = new BABYLON.StandardMaterial('portalMat', scene);
  portalMat.emissiveColor = new BABYLON.Color3(0.6, 0.2, 1.0);
  portal.material = portalMat;
  portal.rotation.x = Math.PI / 2;
  portal.isPickable = false;

  const particleSystem = new BABYLON.ParticleSystem('portalParticles', 2000, scene);
  particleSystem.particleTexture = new BABYLON.Texture('https://assets.babylonjs.com/textures/flare.png', scene);
  particleSystem.emitter = new BABYLON.Vector3(-15, 1.5, -15);
  particleSystem.minEmitBox = new BABYLON.Vector3(-0.2, 0, -0.2);
  particleSystem.maxEmitBox = new BABYLON.Vector3(0.2, 2, 0.2);
  particleSystem.color1 = new BABYLON.Color4(0.6, 0.2, 1.0, 1.0);
  particleSystem.color2 = new BABYLON.Color4(0.3, 0.6, 1.0, 1.0);
  particleSystem.minSize = 0.2;
  particleSystem.maxSize = 0.6;
  particleSystem.minLifeTime = 0.4;
  particleSystem.maxLifeTime = 1.5;
  particleSystem.emitRate = 300;
  particleSystem.blendMode = BABYLON.ParticleSystem.BLENDMODE_STANDARD;
  particleSystem.gravity = new BABYLON.Vector3(0, 0.1, 0);
  particleSystem.direction1 = new BABYLON.Vector3(-1, 3, -1);
  particleSystem.direction2 = new BABYLON.Vector3(1, 3, 1);
  particleSystem.minEmitPower = 0.5;
  particleSystem.maxEmitPower = 1.5;
  particleSystem.start();
}

// -----------------------------------------------------
// Personagens
// -----------------------------------------------------
function createCharacters(scene) {
  const npcsCreated = NPC_DEFINITIONS.map(def => createNPC(scene, def));
  const playerAvatar = createPlayerRepresentation(scene);
  playerAvatar.position.copyFrom(SPAWN_POINT);
  return { npcs: npcsCreated, player: playerAvatar };
}

function createNPC(scene, def) {
  const root = new BABYLON.TransformNode(`${def.id}Root`, scene);
  root.position.copyFrom(def.anchor);

  const body = BABYLON.MeshBuilder.CreateCylinder(`${def.id}Body`, { height: 1.1, diameter: 0.45 }, scene);
  body.position = new BABYLON.Vector3(0, 0.55, 0);
  const bodyMat = new BABYLON.StandardMaterial(`${def.id}BodyMat`, scene);
  bodyMat.diffuseColor = def.tint;
  body.material = bodyMat;
  body.parent = root;
  body.receiveShadows = true;
  shadowGen.addShadowCaster(body);

  const head = BABYLON.MeshBuilder.CreateSphere(`${def.id}Head`, { diameter: 0.42 }, scene);
  head.position = new BABYLON.Vector3(0, 1.25, 0);
  const headMat = new BABYLON.StandardMaterial(`${def.id}HeadMat`, scene);
  headMat.diffuseColor = new BABYLON.Color3(1, 0.85, 0.7);
  head.material = headMat;
  head.parent = root;
  head.receiveShadows = true;
  shadowGen.addShadowCaster(head);

  const hair = BABYLON.MeshBuilder.CreateSphere(`${def.id}Hair`, { diameter: 0.48, slice: 0.6 }, scene);
  hair.position = new BABYLON.Vector3(0, 1.38, -0.05);
  const hairMat = new BABYLON.StandardMaterial(`${def.id}HairMat`, scene);
  hairMat.diffuseColor = def.hair;
  hair.material = hairMat;
  hair.parent = root;
  hair.receiveShadows = true;
  shadowGen.addShadowCaster(hair);

  const leftEye = BABYLON.MeshBuilder.CreateSphere(`${def.id}LeftEye`, { diameter: 0.08 }, scene);
  leftEye.position = new BABYLON.Vector3(-0.1, 1.25, 0.18);
  const rightEye = BABYLON.MeshBuilder.CreateSphere(`${def.id}RightEye`, { diameter: 0.08 }, scene);
  rightEye.position = new BABYLON.Vector3(0.1, 1.25, 0.18);
  const eyeMat = new BABYLON.StandardMaterial(`${def.id}EyeMat`, scene);
  eyeMat.diffuseColor = new BABYLON.Color3(0, 0, 0);
  leftEye.material = rightEye.material = eyeMat;
  leftEye.parent = rightEye.parent = root;

  const arms = ['Left', 'Right'];
  arms.forEach(side => {
    const arm = BABYLON.MeshBuilder.CreateCylinder(`${def.id}${side}Arm`, { height: 0.75, diameter: 0.12 }, scene);
    arm.parent = root;
    arm.position = new BABYLON.Vector3(side === 'Left' ? -0.32 : 0.32, 0.65, 0);
    arm.rotation.z = side === 'Left' ? 0.1 : -0.1;
    arm.material = headMat;
    arm.receiveShadows = true;
    shadowGen.addShadowCaster(arm);
  });

  const legs = ['Left', 'Right'];
  legs.forEach((side, idx) => {
    const leg = BABYLON.MeshBuilder.CreateCylinder(`${def.id}${side}Leg`, { height: 0.8, diameter: 0.15 }, scene);
    leg.parent = root;
    leg.position = new BABYLON.Vector3(idx === 0 ? -0.14 : 0.14, -0.45, 0);
    const legMat = new BABYLON.StandardMaterial(`${def.id}LegMat`, scene);
    legMat.diffuseColor = def.outfit;
    leg.material = legMat;
    leg.receiveShadows = true;
    shadowGen.addShadowCaster(leg);
  });

  const collider = BABYLON.MeshBuilder.CreateCylinder(`${def.id}Collider`, { height: 1.7, diameter: 0.6 }, scene);
  collider.position.y = 0.85;
  collider.isVisible = false;
  collider.checkCollisions = true;
  collider.parent = root;

  const nameTag = createNameTag(root, def.name, scene);

  return {
    id: def.id,
    def,
    root,
    collider,
    nameTag,
    dialogIndex: 0,
    state: {
      target: def.anchor.clone(),
      waitTimer: 2 + Math.random() * 3
    }
  };
}

function createPlayerRepresentation(scene) {
  const playerNode = new BABYLON.TransformNode('playerAvatar', scene);

  const body = BABYLON.MeshBuilder.CreateCylinder('playerBody', { height: 1.05, diameter: 0.4 }, scene);
  body.position.y = 0.5;
  const bodyMat = new BABYLON.StandardMaterial('playerBodyMat', scene);
  bodyMat.diffuseColor = new BABYLON.Color3(0.2, 0.55, 0.85);
  body.material = bodyMat;
  body.parent = playerNode;

  const head = BABYLON.MeshBuilder.CreateSphere('playerHead', { diameter: 0.4 }, scene);
  head.position.y = 1.2;
  const headMat = new BABYLON.StandardMaterial('playerHeadMat', scene);
  headMat.diffuseColor = new BABYLON.Color3(1, 0.85, 0.7);
  head.material = headMat;
  head.parent = playerNode;

  createNameTag(playerNode, 'Você', scene);
  return playerNode;
}

function createNameTag(parent, text, scene) {
  const plane = BABYLON.MeshBuilder.CreatePlane(`${parent.name}NameTag`, { width: 1.4, height: 0.36 }, scene);
  plane.position.y = 2.1;
  plane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
  plane.parent = parent;

  const dynamicTexture = new BABYLON.DynamicTexture(`${parent.name}NameTexture`, { width: 512, height: 128 }, scene, false);
  dynamicTexture.hasAlpha = true;
  const ctx = dynamicTexture.getContext();
  ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
  ctx.fillRect(0, 0, 512, 128);
  dynamicTexture.drawText(text, null, 90, 'bold 64px Arial', 'white', 'transparent', true);

  const mat = new BABYLON.StandardMaterial(`${parent.name}NameMat`, scene);
  mat.diffuseTexture = dynamicTexture;
  mat.emissiveColor = new BABYLON.Color3(1, 1, 1);
  mat.backFaceCulling = false;
  plane.material = mat;
  return plane;
}

// -----------------------------------------------------
// UI e Missões
// -----------------------------------------------------
function createUI(scene) {
  interactionPrompt.style.display = 'none';
  dialogBox.style.display = 'none';
  missionTracker.innerHTML = '';
}

function showDialog(text, timeoutMs = 4000) {
  dialogBox.innerText = text;
  dialogBox.style.display = 'block';
  clearTimeout(showDialog._t);
  showDialog._t = setTimeout(() => dialogBox.style.display = 'none', timeoutMs);
}

function setupMissions() {
  missions = [
    {
      id: 'findCrystal',
      title: 'Cristal Brilhante',
      description: 'Encontre o cristal azul próximo ao lago e converse com Kai 🧭.',
      completed: false,
      checkCompletion: (npcId) => npcId === 'kai'
    },
    {
      id: 'talkToAna',
      title: 'Histórias com Ana',
      description: 'Compartilhe uma história com Ana 📚 e receba uma nova lenda.',
      completed: false,
      checkCompletion: (npcId) => npcId === 'ana'
    }
  ];

  activeMission = missions[0];
  renderMissionTracker();
}

function renderMissionTracker() {
  if (!activeMission) {
    missionTracker.innerHTML = '<strong>Todas as missões concluídas! 🚀</strong>';
    return;
  }
  missionTracker.innerHTML = `
    <h3>Missão Atual</h3>
    <strong>${activeMission.title}</strong>
    <p>${activeMission.description}</p>
  `;
}

function completeMission(npc) {
  if (!activeMission || activeMission.completed) return;
  if (!activeMission.checkCompletion(npc.id)) return;

  activeMission.completed = true;
  showDialog(`🎉 Missão concluída: ${activeMission.title}! ${npc.def.name} agradece.`);

  const remaining = missions.find(m => !m.completed);
  activeMission = remaining || null;
  renderMissionTracker();
}

// -----------------------------------------------------
// Input / Movimento
// -----------------------------------------------------
function setupControls(scene) {
  scene.onKeyboardObservable.add((kb) => {
    const down = kb.type === BABYLON.KeyboardEventTypes.KEYDOWN;
    const key = kb.event.key.toLowerCase();
    switch (key) {
      case 'w': moveForward = down; break;
      case 's': moveBackward = down; break;
      case 'a': moveLeft = down; break;
      case 'd': moveRight = down; break;
      case 'shift': isRunning = down; break;
      case 'e':
        if (down && canInteract && currentInteractable) interactWithNPC(currentInteractable);
        break;
    }
  });
}

function updateMovement() {
  if (!camera) return;
  camera.speed = isRunning ? 0.36 : 0.24;
}

function updatePlayerRepresentation() {
  if (!player || !camera) return;
  const playerPos = camera.position.clone();
  playerPos.y = 0;
  player.position.copyFrom(playerPos);
  const forward = camera.getDirection(BABYLON.Vector3.Forward());
  player.rotation.y = Math.atan2(forward.x, forward.z);
}

// -----------------------------------------------------
// NPCs e Interação
// -----------------------------------------------------
function updateNPCs(deltaSec) {
  if (!deltaSec) return;
  npcs.forEach(npc => {
    const { state, def, root } = npc;
    if (state.waitTimer > 0) {
      state.waitTimer -= deltaSec;
      return;
    }

    const target = state.target;
    const direction = target.subtract(root.position);
    const distance = direction.length();
    if (distance < 0.1) {
      const angle = Math.random() * Math.PI * 2;
      const radius = Math.random() * def.roamRadius;
      state.target = def.anchor.add(new BABYLON.Vector3(Math.cos(angle) * radius, 0, Math.sin(angle) * radius));
      state.waitTimer = 2 + Math.random() * 3;
      return;
    }

    direction.normalize();
    const moveStep = direction.scale(def.walkSpeed * deltaSec);
    root.position.addInPlace(moveStep);
    root.rotation.y = Math.atan2(direction.x, direction.z);
  });
}

function checkInteraction() {
  if (!camera) return;
  const forward = camera.getDirection(BABYLON.Vector3.Forward());
  const origin = camera.position.add(new BABYLON.Vector3(0, 0.5, 0));
  const ray = new BABYLON.Ray(origin, forward, 4.0);

  let bestNpc = null;
  let bestScore = Infinity;

  npcs.forEach(npc => {
    const distance = BABYLON.Vector3.Distance(camera.position, npc.root.position);
    if (distance > 4) return;
    const pick = scene.pickWithRay(ray, m => m && (m.parent === npc.root || m === npc.root));
    if (!pick || !pick.hit) return;
    if (distance < bestScore) {
      bestScore = distance;
      bestNpc = npc;
    }
  });

  if (bestNpc) {
    canInteract = true;
    currentInteractable = bestNpc;
    interactionPrompt.innerText = `Pressione [E] para conversar com ${bestNpc.def.name}`;
    interactionPrompt.style.display = 'block';
    bestNpc.root.lookAt(new BABYLON.Vector3(camera.position.x, bestNpc.root.position.y + 1, camera.position.z));
    bestNpc.root.rotation.x = 0;
    bestNpc.root.rotation.z = 0;
  } else {
    canInteract = false;
    currentInteractable = null;
    interactionPrompt.style.display = 'none';
  }
}

function interactWithNPC(npc) {
  const line = npc.def.lines[npc.dialogIndex % npc.def.lines.length];
  npc.dialogIndex++;
  showDialog(line);
  completeMission(npc);

  // Gancho IA opcional
  // fetch('/ai/observe', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ event: 'interact', actor: 'player', target: npc.id }) });
}

// -----------------------------------------------------
// QoL
// -----------------------------------------------------
function enablePointerLock() {
  canvas.addEventListener('click', () => {
    if (document.pointerLockElement !== canvas) {
      const requestPointerLock = canvas.requestPointerLock || canvas.mozRequestPointerLock || canvas.webkitRequestPointerLock;
      requestPointerLock && requestPointerLock.call(canvas);
    }
  });
}

// -----------------------------------------------------
// Multiplayer (stub WebSocket)
// -----------------------------------------------------
function connectWS(url) {
  ws = new WebSocket(url);
  ws.onopen = () => console.log('[WS] conectado');
  ws.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      console.log('[WS] evento recebido', msg);
    } catch (e) { /* ignore */ }
  };
  ws.onclose = () => console.log('[WS] desconectado');
}
