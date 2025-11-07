# 🎮 Configuração de GPU para Sofia

## Visão Geral

A Sofia agora está configurada para usar **aceleração por GPU** (NVIDIA GeForce GTX 1650) junto com a CPU para gerar respostas mais rápidas e eficientes.

## 🚀 Configuração Rápida

### 1. Verificar GPU Disponível

```powershell
# Ver GPU no Gerenciador de Tarefas
# Pressione: Ctrl + Shift + Esc
# Vá em: Desempenho > GPU

# Ou use o script Python
python verificar_gpu.py
```

### 2. Aplicar Configurações de GPU

```powershell
# Execute o script de configuração
.\setup_gpu.ps1

# Ou defina manualmente:
$env:OLLAMA_GPU_LAYERS = "999"
$env:OLLAMA_NUM_PARALLEL = "4"
```

### 3. Reiniciar Ollama

```powershell
# Parar Ollama (se estiver rodando)
Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue

# Iniciar novamente
ollama serve
```

### 4. Verificar se GPU está sendo usada

```powershell
python verificar_gpu.py
```

## ⚙️ Configurações Aplicadas

A Sofia foi configurada com:

```json
{
  "num_gpu": 999,        // Usa TODAS as camadas na GPU
  "num_thread": 8,       // 8 threads da CPU para paralelismo
  "num_ctx": 4096,       // Contexto de 4K tokens
  "temperature": 0.7,    // Criatividade moderada
  "top_p": 0.9          // Diversidade nas respostas
}
```

### Localização no Código

Arquivo: `sofia/core/cerebro.py` (linhas ~220-236)

## 📊 Performance Esperada

### Com CPU apenas:
- Velocidade: ~5-15 tokens/segundo
- Tempo de resposta: Lento (30-60s para respostas longas)
- Uso de memória: Alto

### Com GPU GTX 1650:
- Velocidade: ~30-60 tokens/segundo
- Tempo de resposta: Rápido (5-15s para respostas longas)
- Uso de memória: Otimizado (compartilhado GPU/CPU)

### Monitoramento

**Gerenciador de Tarefas do Windows:**
1. Abra com `Ctrl + Shift + Esc`
2. Vá em "Desempenho"
3. Selecione "GPU"
4. Durante uso da Sofia, você deve ver:
   - **GPU 3D**: 10-80% (processamento)
   - **Copy**: ~14% (transferência de dados)
   - **Memória dedicada**: 3.4-4.0 GB usados
   - **Temperatura**: ~48°C (normal)

## 🔧 Solução de Problemas

### GPU não está sendo usada?

**1. Verificar drivers NVIDIA:**
```powershell
nvidia-smi
```
Se não funcionar, atualize os drivers em: https://www.nvidia.com/download/index.aspx

**2. Reinstalar Ollama com suporte CUDA:**
```powershell
# Desinstalar versão atual
ollama uninstall

# Baixar e instalar versão com CUDA
# https://ollama.ai/download
```

**3. Verificar variáveis de ambiente:**
```powershell
Get-ChildItem Env: | Where-Object { $_.Name -like "*OLLAMA*" }
```

Deve mostrar:
- `OLLAMA_GPU_LAYERS = 999`
- `OLLAMA_NUM_PARALLEL = 4`

**4. Testar modelo específico:**
```bash
ollama run mistral "teste de gpu"
```

### Performance ainda lenta?

**1. Usar modelo quantizado:**
```bash
# Modelos menores = mais rápidos
ollama pull mistral:7b-q4_0  # 4-bit quantizado
ollama pull mistral:7b-q5_0  # 5-bit (mais preciso)
```

**2. Ajustar contexto:**
Reduza `num_ctx` se tiver pouca VRAM:
```python
"num_ctx": 2048  # Em vez de 4096
```

**3. Limitar GPU layers:**
Se VRAM insuficiente:
```python
"num_gpu": 32  # Em vez de 999
```

## 📈 Comparação de Modelos

| Modelo | Tamanho | VRAM Necessária | Velocidade (GTX 1650) |
|--------|---------|-----------------|----------------------|
| mistral:7b | ~4.1 GB | ~4 GB | ⭐⭐⭐⭐ (rápido) |
| mistral:7b-q4 | ~3.8 GB | ~3.5 GB | ⭐⭐⭐⭐⭐ (muito rápido) |
| llama2:7b | ~3.8 GB | ~3.5 GB | ⭐⭐⭐⭐ (rápido) |
| llama2:13b | ~7.4 GB | ~8 GB | ⭐ (lento/overflow) |

**Recomendação para GTX 1650 (4GB):** 
- ✅ `mistral:7b-q4_0` (melhor balance)
- ✅ `mistral:7b` (qualidade máxima)
- ❌ Modelos 13b+ (VRAM insuficiente)

## 🎯 Otimizações Avançadas

### 1. Pré-carregar modelo na GPU
```bash
# Mantém modelo carregado
ollama run mistral ""
# Deixe rodando em background
```

### 2. Ajustar prioridade do processo
```powershell
# No Gerenciador de Tarefas
# Detalhes > ollama.exe > Botão direito > Definir prioridade > Alta
```

### 3. Configurar afinidade de CPU
```powershell
# Usar cores específicos (0-7)
$process = Get-Process ollama
$process.ProcessorAffinity = 0xFF  # Todos os 8 cores
```

## 📝 Scripts Úteis

### verificar_gpu.py
Testa se GPU está sendo usada:
```bash
python verificar_gpu.py
```

### setup_gpu.ps1
Aplica configurações otimizadas:
```bash
.\setup_gpu.ps1
```

### reiniciar_sofia.ps1
Reinicia servidor com configurações:
```bash
.\reiniciar_sofia.ps1
```

## 🔍 Logs e Debug

### Ver logs do Ollama:
```powershell
# Habilitar debug
$env:OLLAMA_DEBUG = "1"
ollama serve
```

### Monitorar uso de GPU em tempo real:
```powershell
# Atualiza a cada 1 segundo
while ($true) { 
    Clear-Host
    nvidia-smi
    Start-Sleep -Seconds 1
}
```

## 📚 Referências

- [Ollama GPU Documentation](https://github.com/ollama/ollama/blob/main/docs/gpu.md)
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)

## ✅ Checklist de Verificação

- [ ] Drivers NVIDIA atualizados
- [ ] Ollama instalado com suporte CUDA
- [ ] Variáveis de ambiente configuradas (`setup_gpu.ps1`)
- [ ] Modelo compatível baixado (`mistral:7b-q4_0`)
- [ ] GPU aparece no Gerenciador de Tarefas
- [ ] Script `verificar_gpu.py` mostra >30 tokens/s
- [ ] Sofia responde mais rápido que antes

---

**Atualizado em**: 7 de novembro de 2025
**Hardware**: NVIDIA GeForce GTX 1650 (4GB VRAM)
**Status**: ✅ Configurado e otimizado
