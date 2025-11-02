# 🌸 Sofia - Assistente Virtual Inteligente

> Uma assistente virtual amigável e empática.

Criada por **Reginaldo** ([@SomBRaRCP](https://github.com/SomBRaRCP))

---

## O que é?

Sofia é uma assistente virtual que usa inteligência artificial para conversar de forma natural e empática.

### Recursos

- ✅ Conversação natural
- ✅ Memória de contexto
- ✅ Respostas adaptativas
- ✅ Interface simples

---

## Instalação

### Pré-requisitos

1. **Python 3.8+**
2. **Ollama** (motor de IA local)

### Passo a Passo

```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral

# 2. Clonar e instalar Sofia
git clone <repo>
cd sofia
chmod +x setup.sh
./setup.sh

# 3. Ativar ambiente e executar
source venv/bin/activate
python -m sofia.main
```

---

## Uso

### Conversa Básica

```
🌸 Olá! Eu sou a Sofia
==================================================

Bem-vindo, SomBRaRCP!
Sou uma assistente virtual criada para conversar.

Digite 'sair' para encerrar.

SomBRaRCP: Olá Sofia!
🌸 Sofia: Olá! Como posso ajudar você hoje?

SomBRaRCP: Como você está?
🌸 Sofia: Estou bem, obrigada por perguntar! 💜
```

### Comandos

- `sair` ou `exit` - Encerra a conversa
- `limpar` - Limpa a memória de conversas
- `historico` - Mostra as últimas mensagens

---

## Estrutura do Projeto

```
sofia/
├── core/
│   ├── __init__.py         # Inicialização do módulo
│   ├── identidade.py       # Identidade e apresentação
│   ├── cerebro.py          # Integração com Ollama
│   ├── memoria.py          # Sistema de memória
│   └── _interno.py         # Motor interno
│
├── main.py                 # Programa principal
├── requirements.txt        # Dependências Python
├── setup.sh                # Script de instalação
└── README.md               # Esta documentação
```

---

## Tecnologias

- **Python 3.8+** - Linguagem principal
- **Ollama** - Motor de IA local (Mistral)
- **Requests** - Comunicação HTTP

---

## Desenvolvimento

### Estrutura de Código

#### `identidade.py`
Gerencia a apresentação e identidade da Sofia.

#### `cerebro.py`
Faz a comunicação com o Ollama e processa respostas.

#### `memoria.py`
Armazena e gerencia o histórico de conversas.

#### `_interno.py`
Motor interno com processamento avançado.

### Extender Funcionalidades

Para adicionar novos comandos, edite `main.py`:

```python
if entrada.lower() == "seu_comando":
    # Sua lógica aqui
    pass
```

---

## Solução de Problemas

### Ollama não responde

```bash
# Verificar se Ollama está rodando
ollama list

# Reiniciar Ollama
ollama serve
```

### Erro de conexão

Verifique se o Ollama está rodando na porta 11434:
```bash
curl http://localhost:11434/api/tags
```

### Ambiente virtual não ativa

```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

---

## Roadmap

### v1.0 ✅ (Atual)
- Conversação básica
- Memória contextual
- Interface CLI

### v2.0 (Planejado)
- Análise de emoções
- Personalidade configurável
- Comandos avançados

### v3.0 (Futuro)
- Interface web
- Análise de imagens
- Leitura de arquivos

---

## Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Add: nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## Licença

Projeto pessoal de Reginaldo (@SomBRaRCP).

---

## Contato

- GitHub: [@SomBRaRCP](https://github.com/SomBRaRCP)
- Projeto: github/copilot-cli

---

<div align="center">
  <strong>🌸 Sofia - Sua assistente virtual 🌸</strong>
</div>