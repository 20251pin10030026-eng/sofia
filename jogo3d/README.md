# 🎮 Mundo 3D de Sofia

Jogo 3D em primeira pessoa onde você pode explorar o quarto da Sofia e interagir com ela.

## 🚀 Como Executar

### Opção 1: Servidor Local Simples (Python)

1. Abra o terminal na pasta `jogo3d`
2. Execute:
```bash
python -m http.server 8080
```
3. Abra o navegador em: `http://localhost:8080`

### Opção 2: Live Server (VS Code)

1. Instale a extensão "Live Server" no VS Code
2. Clique com botão direito em `index.html`
3. Selecione "Open with Live Server"

### Opção 3: Qualquer servidor web

Basta servir os arquivos da pasta `jogo3d` em qualquer servidor web.

## 🎮 Controles

- **W A S D** - Mover pelo quarto
- **Mouse** - Olhar ao redor (arraste o mouse)
- **Shift** - Correr
- **E** - Interagir com Sofia (quando estiver perto)
- **ESC** - Pausar/Liberar mouse

## 🌟 Recursos Implementados

### Ambiente 3D
- ✅ Quarto completo com paredes, chão e teto
- ✅ Sistema de colisão (não atravessa paredes)
- ✅ Iluminação realista (luz hemisférica + direcional)
- ✅ Física e gravidade

### Móveis
- ✅ Cama com cabeceira (roxa - cor da Sofia)
- ✅ Mesa com 4 pernas
- ✅ Cadeira com encosto
- ✅ Armário

### Personagens
- ✅ **Sofia** - Personagem humanóide feminina
  - Corpo roxo
  - Cabeça com tom de pele
  - Cabelo marrom
  - Olhos pretos
  - Braços e pernas
  - Nome flutuante "Sofia 🌸"
  - Olha para você quando se aproxima

- ✅ **Você (Player)** - Representação inicial
  - Corpo azul
  - Design humanóide similar
  - Nome "Você" flutuante
  - Visível apenas no spawn

### Interação
- ✅ Sistema de proximidade (< 3 metros)
- ✅ Indicador visual "Pressione E para interagir"
- ✅ Sofia olha para você quando está perto
- ✅ Diálogo ao pressionar E

### Controles
- ✅ Movimento WASD primeira pessoa
- ✅ Mouse look (arrastar para olhar)
- ✅ Corrida com Shift
- ✅ Sistema de colisão completo
- ✅ Câmera em altura realista (1.6m - altura dos olhos)

## 📦 Tecnologias Utilizadas

- **Babylon.js 5.x** - Engine 3D (via CDN)
- **HTML5 Canvas** - Renderização
- **JavaScript ES6** - Lógica do jogo
- **CSS3** - Interface e HUD

## 🎨 Estrutura do Projeto

```
jogo3d/
├── index.html          # Página principal
├── css/
│   └── style.css       # Estilos e HUD
└── js/
    └── game.js         # Lógica do jogo
```

## 🔧 Próximas Melhorias Possíveis

- [ ] Mais cômodos (sala, cozinha, banheiro)
- [ ] Sistema de diálogo completo com IA
- [ ] Animações de caminhada para Sofia
- [ ] Mais objetos interativos
- [ ] Sistema de inventário
- [ ] Música e sons ambiente
- [ ] Texturas mais detalhadas
- [ ] Dia/noite
- [ ] Porta para sair do quarto

## 💡 Notas

- O jogo roda 100% no navegador
- Não precisa instalar nada (usa CDN do Babylon.js)
- Funciona em qualquer navegador moderno
- Requer WebGL (todos os navegadores atuais suportam)

## 🐛 Troubleshooting

**Mouse não funciona?**
- Clique no canvas para ativar o pointer lock
- Pressione ESC para liberar

**Jogo não carrega?**
- Verifique se está usando um servidor web (não abra o HTML direto)
- Verifique conexão com internet (usa CDN)

**Performance ruim?**
- Feche outras abas do navegador
- Atualize os drivers da placa de vídeo
