# 🎮 Metaverso de Sofia

Mundo 3D de exploração livre em primeira pessoa com NPCs inteligentes e chat integrado com IA.

## 🚀 Como Executar

### Método Recomendado: Via Servidor Flask

1. Inicie o servidor da Sofia:
```bash
cd d:\A.I_GitHUB
.\.venv\Scripts\python.exe -m sofia.api
```

2. Acesse no navegador:
```
http://localhost:5000/jogo3d
```

### Método Alternativo: Servidor Python Simples

1. Abra o terminal na pasta `jogo3d`
2. Execute:
```bash
python -m http.server 8080
```
3. Abra: `http://localhost:8080/metaverso.html`

**Nota**: O chat integrado só funciona com o servidor Flask rodando.

## 🎮 Controles

- **W A S D** - Mover pelo mundo
- **Mouse** - Olhar ao redor (clique para travar ponteiro)
- **Shift** - Correr
- **E** - Interagir com NPCs (quando aparecer prompt)
- **ESC** - Liberar ponteiro do mouse

## 💬 Chat Integrado

### Funcionalidades
- ✅ **Janela Arrastável** - Clique e segure no header roxo para mover
- ✅ **Minimizar** - Botão **−** para colapsar janela
- ✅ **Fechar** - Botão **×** para esconder completamente
- ✅ **Chat em Tempo Real** - Converse com Sofia IA durante exploração
- ✅ **Sincronização** - Mensagens do NPC Sofia aparecem no chat

### Como Usar
1. A janela de chat aparece automaticamente ao entrar no metaverso
2. Digite sua mensagem no campo de texto
3. Pressione **Enter** ou clique em **"Enviar"**
4. Sofia responderá através da IA (indicador de digitação animado)
5. Arraste a janela para qualquer posição da tela
6. Minimize quando não precisar, reabra clicando no header

### Integração com NPC
- Pressione **E** próximo à Sofia no mundo 3D
- Ela começará a te seguir pelo mundo
- Uma mensagem de ativação aparecerá no chat
- Todas interações com o NPC também aparecem no chat

## 🌟 Recursos Implementados

### Ambiente 3D
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
