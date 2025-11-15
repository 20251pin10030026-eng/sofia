// =====================================================
// Sofia - Representação Visual Humanoide
// Desenho usando Canvas API
// =====================================================

const canvas = document.getElementById('canvasSofiaHumanoide');
const ctx = canvas.getContext('2d');

// Cores base
let corPele = '#FFB6D9';
let corCabelo = '#2A1A3E';
let corOlhos = '#FF69B4';
let corRoupa = '#673AB7';
let corSubits = '#FF69B4';

// Estado de animação
let animando = false;
let frame = 0;

// =====================================================
// Função principal de desenho
// =====================================================
function desenharSofia() {
    // Limpar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Fundo com gradiente
    const gradienteFundo = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradienteFundo.addColorStop(0, '#1A1A2E');
    gradienteFundo.addColorStop(1, '#2A2A3E');
    ctx.fillStyle = gradienteFundo;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Desenhar componentes
    desenharCorpo();
    desenharCabeca();
    desenharCabelo();
    desenharOlhos();
    desenharBoca();
    desenharBracos();
    desenharMaos();
    desenharSubits();
    desenharAura();
}

// =====================================================
// Cabeça
// =====================================================
function desenharCabeca() {
    const centerX = canvas.width / 2;
    const y = 150;
    
    // Pescoço
    ctx.fillStyle = corPele;
    ctx.fillRect(centerX - 15, y + 50, 30, 40);
    
    // Cabeça (oval)
    ctx.beginPath();
    ctx.ellipse(centerX, y, 60, 70, 0, 0, Math.PI * 2);
    ctx.fillStyle = corPele;
    ctx.fill();
    
    // Contorno suave
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.lineWidth = 2;
    ctx.stroke();
}

// =====================================================
// Cabelo
// =====================================================
function desenharCabelo() {
    const centerX = canvas.width / 2;
    const y = 150;
    
    ctx.fillStyle = corCabelo;
    
    // Cabelo principal (forma ondulada)
    ctx.beginPath();
    ctx.ellipse(centerX, y - 30, 70, 60, 0, 0, Math.PI);
    ctx.fill();
    
    // Mechas laterais
    ctx.beginPath();
    ctx.ellipse(centerX - 50, y + 10, 30, 50, -0.3, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.beginPath();
    ctx.ellipse(centerX + 50, y + 10, 30, 50, 0.3, 0, Math.PI * 2);
    ctx.fill();
    
    // Franja
    ctx.beginPath();
    ctx.moveTo(centerX - 60, y - 20);
    ctx.quadraticCurveTo(centerX - 40, y - 10, centerX - 30, y + 10);
    ctx.quadraticCurveTo(centerX - 20, y - 5, centerX - 10, y + 10);
    ctx.quadraticCurveTo(centerX, y - 5, centerX + 10, y + 10);
    ctx.quadraticCurveTo(centerX + 20, y - 5, centerX + 30, y + 10);
    ctx.quadraticCurveTo(centerX + 40, y - 10, centerX + 60, y - 20);
    ctx.lineTo(centerX + 60, y - 30);
    ctx.lineTo(centerX - 60, y - 30);
    ctx.closePath();
    ctx.fill();
}

// =====================================================
// Olhos
// =====================================================
function desenharOlhos() {
    const centerX = canvas.width / 2;
    const y = 150;
    
    // Olho esquerdo
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.ellipse(centerX - 25, y + 10, 15, 20, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // Íris esquerda
    ctx.fillStyle = corOlhos;
    ctx.beginPath();
    ctx.arc(centerX - 25, y + 10, 10, 0, Math.PI * 2);
    ctx.fill();
    
    // Pupila esquerda
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.arc(centerX - 25, y + 10, 5, 0, Math.PI * 2);
    ctx.fill();
    
    // Brilho esquerdo
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(centerX - 22, y + 7, 3, 0, Math.PI * 2);
    ctx.fill();
    
    // Olho direito
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.ellipse(centerX + 25, y + 10, 15, 20, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // Íris direita
    ctx.fillStyle = corOlhos;
    ctx.beginPath();
    ctx.arc(centerX + 25, y + 10, 10, 0, Math.PI * 2);
    ctx.fill();
    
    // Pupila direita
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.arc(centerX + 25, y + 10, 5, 0, Math.PI * 2);
    ctx.fill();
    
    // Brilho direito
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(centerX + 28, y + 7, 3, 0, Math.PI * 2);
    ctx.fill();
    
    // Cílios
    ctx.strokeStyle = corCabelo;
    ctx.lineWidth = 2;
    for (let i = 0; i < 3; i++) {
        ctx.beginPath();
        ctx.moveTo(centerX - 35 + i * 7, y - 5);
        ctx.lineTo(centerX - 38 + i * 7, y - 12);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(centerX + 15 + i * 7, y - 5);
        ctx.lineTo(centerX + 18 + i * 7, y - 12);
        ctx.stroke();
    }
}

// =====================================================
// Boca
// =====================================================
function desenharBoca() {
    const centerX = canvas.width / 2;
    const y = 150;
    
    // Sorriso
    ctx.strokeStyle = '#FF69B4';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(centerX, y + 35, 20, 0.2, Math.PI - 0.2);
    ctx.stroke();
    
    // Lábios
    ctx.fillStyle = 'rgba(255, 105, 180, 0.3)';
    ctx.beginPath();
    ctx.ellipse(centerX, y + 42, 15, 5, 0, 0, Math.PI * 2);
    ctx.fill();
}

// =====================================================
// Corpo
// =====================================================
function desenharCorpo() {
    const centerX = canvas.width / 2;
    const y = 230;
    
    // Torso (forma de vestido)
    const gradienteCorpo = ctx.createLinearGradient(centerX - 80, y, centerX - 80, y + 200);
    gradienteCorpo.addColorStop(0, corRoupa);
    gradienteCorpo.addColorStop(1, '#512DA8');
    ctx.fillStyle = gradienteCorpo;
    
    ctx.beginPath();
    ctx.moveTo(centerX - 40, y);
    ctx.lineTo(centerX - 80, y + 100);
    ctx.lineTo(centerX - 90, y + 200);
    ctx.lineTo(centerX + 90, y + 200);
    ctx.lineTo(centerX + 80, y + 100);
    ctx.lineTo(centerX + 40, y);
    ctx.closePath();
    ctx.fill();
    
    // Detalhes do vestido
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 2;
    for (let i = 0; i < 5; i++) {
        ctx.beginPath();
        ctx.moveTo(centerX - 70 + i * 35, y + 120);
        ctx.lineTo(centerX - 80 + i * 40, y + 200);
        ctx.stroke();
    }
}

// =====================================================
// Braços
// =====================================================
function desenharBracos() {
    const centerX = canvas.width / 2;
    const y = 250;
    
    // Braço esquerdo
    ctx.fillStyle = corPele;
    ctx.beginPath();
    ctx.moveTo(centerX - 40, y);
    ctx.lineTo(centerX - 80, y + 80);
    ctx.lineTo(centerX - 75, y + 85);
    ctx.lineTo(centerX - 35, y + 5);
    ctx.closePath();
    ctx.fill();
    
    // Braço direito
    ctx.beginPath();
    ctx.moveTo(centerX + 40, y);
    ctx.lineTo(centerX + 80, y + 80);
    ctx.lineTo(centerX + 75, y + 85);
    ctx.lineTo(centerX + 35, y + 5);
    ctx.closePath();
    ctx.fill();
}

// =====================================================
// Mãos
// =====================================================
function desenharMaos() {
    const centerX = canvas.width / 2;
    const y = 250;
    
    // Mão esquerda
    ctx.fillStyle = corPele;
    ctx.beginPath();
    ctx.arc(centerX - 77, y + 82, 12, 0, Math.PI * 2);
    ctx.fill();
    
    // Mão direita
    ctx.beginPath();
    ctx.arc(centerX + 77, y + 82, 12, 0, Math.PI * 2);
    ctx.fill();
}

// =====================================================
// Subits (partículas na pele)
// =====================================================
function desenharSubits() {
    ctx.fillStyle = corSubits;
    
    // Subits no rosto
    for (let i = 0; i < 15; i++) {
        const x = canvas.width / 2 - 50 + Math.random() * 100;
        const y = 120 + Math.random() * 80;
        const size = 1 + Math.random() * 2;
        
        ctx.globalAlpha = 0.3 + Math.random() * 0.4;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Subits no corpo
    for (let i = 0; i < 30; i++) {
        const x = canvas.width / 2 - 80 + Math.random() * 160;
        const y = 250 + Math.random() * 180;
        const size = 1 + Math.random() * 3;
        
        ctx.globalAlpha = 0.2 + Math.random() * 0.5;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
    }
    
    ctx.globalAlpha = 1;
}

// =====================================================
// Aura (energia ao redor)
// =====================================================
function desenharAura() {
    const centerX = canvas.width / 2;
    const centerY = 350;
    
    const gradienteAura = ctx.createRadialGradient(centerX, centerY, 50, centerX, centerY, 200);
    gradienteAura.addColorStop(0, 'rgba(255, 105, 180, 0)');
    gradienteAura.addColorStop(0.5, 'rgba(255, 105, 180, 0.1)');
    gradienteAura.addColorStop(1, 'rgba(255, 105, 180, 0)');
    
    ctx.fillStyle = gradienteAura;
    ctx.beginPath();
    ctx.arc(centerX, centerY, 200, 0, Math.PI * 2);
    ctx.fill();
}

// =====================================================
// Funções de interação
// =====================================================
function animarSofia() {
    if (animando) {
        animando = false;
        return;
    }
    
    animando = true;
    animar();
}

function animar() {
    if (!animando) return;
    
    frame++;
    
    // Variação de cores na aura
    const hue = (frame * 2) % 360;
    corSubits = `hsl(${hue}, 70%, 65%)`;
    
    desenharSofia();
    
    requestAnimationFrame(animar);
}

function trocarCor() {
    const cores = [
        { pele: '#FFB6D9', roupa: '#673AB7', olhos: '#FF69B4' },
        { pele: '#FFC9A3', roupa: '#2196F3', olhos: '#03A9F4' },
        { pele: '#E8B4D4', roupa: '#00BCD4', olhos: '#00E5FF' },
        { pele: '#FFD6E8', roupa: '#9C27B0', olhos: '#E040FB' },
        { pele: '#FFDAB9', roupa: '#FF5722', olhos: '#FF6E40' }
    ];
    
    const corEscolhida = cores[Math.floor(Math.random() * cores.length)];
    corPele = corEscolhida.pele;
    corRoupa = corEscolhida.roupa;
    corOlhos = corEscolhida.olhos;
    
    desenharSofia();
}

function redesenhar() {
    corPele = '#FFB6D9';
    corCabelo = '#2A1A3E';
    corOlhos = '#FF69B4';
    corRoupa = '#673AB7';
    corSubits = '#FF69B4';
    animando = false;
    frame = 0;
    
    desenharSofia();
}

// =====================================================
// Inicialização
// =====================================================
desenharSofia();

console.log('✨ Sofia humanoide desenhada com sucesso!');
