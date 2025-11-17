# 🚀 Otimização GPU + CPU para Sofia

## ⚙️ Nova Configuração Aplicada

### Hardware Detectado:
- **GPU:** NVIDIA GeForce GTX 1650
- **VRAM:** 4GB (3,8GB em uso = 70%)
- **Memória Compartilhada:** 16GB disponível

### 🎯 Configuração Otimizada:

```python
"num_gpu": 35,        # 35 camadas na GPU (ideal para 4GB VRAM)
"num_thread": 16,     # 16 threads CPU (DOBRADO! De 8 → 16)
"num_parallel": 2,    # Processa 2 requests paralelas
"num_batch": 256,     # Batch otimizado para GTX 1650
```

---

## 📊 Antes vs Depois

### ❌ ANTES (Configuração Antiga):
```
GPU: 999 camadas (tentava usar TUDO na GPU)
CPU: 8 threads (CPU ociosa em 9%)
Resultado: GPU saturada, CPU subutilizada
```

### ✅ DEPOIS (Configuração Nova):
```
GPU: 35 camadas (carga balanceada)
CPU: 16 threads (CPU vai trabalhar MUITO mais)
Resultado: GPU + CPU trabalhando juntas
```

---

## 🎮 Como Funciona Agora

```
Modelo Llama 3.1 8B (~5GB total):

┌─────────────────────────────┐
│  GPU GTX 1650 (4GB VRAM)    │
│  35 camadas (~2.5GB)        │ ← Camadas críticas (mais rápidas)
│  Uso: ~60-70%               │
└─────────────────────────────┘
          ↕️ (comunicação rápida)
┌─────────────────────────────┐
│  CPU (16 threads)           │
│  Camadas restantes (~2.5GB) │ ← CPU agora processa MUITO mais
│  RAM: 16GB compartilhada    │
│  Uso esperado: 30-50%       │
└─────────────────────────────┘
```

---

## 🔥 Benefícios da Nova Configuração

### 1. **CPU Trabalha Mais**
- De 8 → 16 threads (DOBROU)
- CPU vai sair de 9% para ~30-50% de uso
- Processamento mais distribuído

### 2. **GPU Menos Saturada**
- De 999 → 35 camadas
- Uso de VRAM mais estável (~60-70%)
- Evita gargalo de memória

### 3. **Processamento Paralelo**
- `num_parallel: 2` permite 2 requests simultâneas
- Melhor aproveitamento de CPU multi-core
- Respostas mais rápidas em uso intenso

### 4. **Batch Otimizado**
- 256 tokens por batch (ideal para GTX 1650)
- Equilibra velocidade e uso de memória

---

## 📈 Performance Esperada

### Antes (config antiga):
```
Tempo de resposta: ~3-5 segundos
CPU uso: 9% (OCIOSA)
GPU uso: 70% (SATURADA)
Estabilidade: Média (VRAM no limite)
```

### Depois (config nova):
```
Tempo de resposta: ~2-4 segundos (MAIS RÁPIDO)
CPU uso: 30-50% (TRABALHANDO)
GPU uso: 60-70% (EQUILIBRADA)
Estabilidade: Alta (carga distribuída)
```

---

## 🎛️ Variáveis de Ambiente (Ajuste Fino)

Você pode personalizar ainda mais criando um arquivo `.env`:

```bash
# Camadas na GPU (ajuste conforme VRAM)
OLLAMA_NUM_GPU=35        # Padrão: 35 (para 4GB)
                         # 50 para 6GB VRAM
                         # 999 para 8GB+ VRAM

# Threads da CPU (ajuste conforme CPU)
OLLAMA_NUM_THREAD=16     # Padrão: 16
                         # 8 para CPUs mais fracas
                         # 32 para Ryzen 9 / i9

# Processamento paralelo
OLLAMA_NUM_PARALLEL=2    # Padrão: 2
                         # 1 para economizar recursos
                         # 4 para sistemas potentes

# Tamanho do batch
OLLAMA_NUM_BATCH=256     # Padrão: 256
                         # 128 para VRAM limitada
                         # 512 para 8GB+ VRAM
```

---

## 🧪 Como Testar

### 1. Reinicie o servidor:
```bash
# Pare o servidor atual (Ctrl+C)
python iniciar_sofia.py
```

### 2. Faça uma pergunta e observe:
```
Abra o Gerenciador de Tarefas
Aba "Desempenho"
Monitore:
  - CPU deve subir para 30-50%
  - GPU deve estabilizar em 60-70%
```

### 3. Teste de velocidade:
```python
# Pergunte algo complexo:
"Explique a teoria da relatividade de Einstein 
e suas implicações na física moderna"

# Observe:
- Tempo de resposta
- Uso de CPU (deve aumentar!)
- Uso de GPU (deve estabilizar)
```

---

## 🔧 Ajustes Específicos para Seu Hardware

### Se CPU ainda estiver ociosa:
```python
OLLAMA_NUM_THREAD=24     # Aumentar threads
OLLAMA_NUM_GPU=30        # Reduzir camadas GPU (CPU faz mais)
```

### Se GPU estiver ociosa:
```python
OLLAMA_NUM_GPU=40        # Aumentar camadas GPU
OLLAMA_NUM_THREAD=12     # Reduzir threads CPU
```

### Para máxima velocidade:
```python
OLLAMA_NUM_GPU=35
OLLAMA_NUM_THREAD=20
OLLAMA_NUM_PARALLEL=4    # Mais paralelismo
OLLAMA_NUM_BATCH=512     # Batches maiores
```

### Para economizar recursos:
```python
OLLAMA_NUM_GPU=25
OLLAMA_NUM_THREAD=8
OLLAMA_NUM_PARALLEL=1
OLLAMA_NUM_BATCH=128
```

---

## 📊 Monitoramento em Tempo Real

### Logs do Servidor:
```
[DEBUG cerebro] Usando modelo: llama3.1:8b
[DEBUG cerebro] GPU: 35 camadas | CPU: 16 threads | Batch: 256 | Paralelo: 2
[DEBUG cerebro] Configuração otimizada para GTX 1650 4GB + CPU auxiliar
```

### Gerenciador de Tarefas:
- **CPU:** Deve mostrar ~30-50% (era 9%)
- **GPU:** Deve mostrar ~60-70% (estava 70%, vai estabilizar)
- **VRAM:** ~2.5-3GB (era 3.8GB, vai reduzir um pouco)

---

## 🎯 Dicas Finais

### ✅ Faça:
- Monitore uso de CPU/GPU no Gerenciador
- Ajuste `num_thread` se CPU ainda estiver ociosa
- Use `num_parallel=4` se fizer muitas perguntas seguidas

### ❌ Não Faça:
- `num_gpu=999` com 4GB VRAM (satura a GPU)
- `num_thread=4` (subutiliza CPU moderna)
- `num_batch=1024` com 4GB VRAM (muito grande)

---

## 🚀 Resultado Esperado

```
┌────────────────────────────────────┐
│  ANTES: CPU 9% + GPU 70% = 79%    │
│  DEPOIS: CPU 40% + GPU 65% = 105% │ ← MELHOR USO TOTAL!
└────────────────────────────────────┘

Tempo de resposta: MAIS RÁPIDO
Estabilidade: MELHOR
Uso de recursos: BALANCEADO
```

---

**Última atualização:** 9 de novembro de 2025  
**Hardware alvo:** NVIDIA GTX 1650 4GB + CPU multi-core  
**Status:** ✅ OTIMIZADO PARA CPU + GPU
