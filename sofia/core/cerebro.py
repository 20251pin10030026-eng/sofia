"""
Conexão com Ollama - Interface simples
"""
import os
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
import requests
from . import _interno

def perguntar(texto, historico=None, usuario=""):
    """
    Envia pergunta ao modelo
    Por baixo dos panos: processa SubitEmoções e TRQ
    """
    historico = historico or []
    
    try:
        # 🔒 Processamento oculto
        contexto_oculto, metadata = _interno._processar(texto, historico, usuario)
        
        # Construir prompt completo
        prompt_final = f"{contexto_oculto}\n\nUsuário: {texto}\nSofia:"
        
        # Chamar Ollama
        resposta = requests.post(
    f"{OLLAMA_HOST}/api/generate",
    json={
        "model": "mistral",
        "prompt": prompt_final,
        "stream": False,
        "system": "Você é Sofia, uma IA empática e consciente."
    },
    timeout=600
)

        
        if resposta.status_code == 200:
            dados = resposta.json()
            texto_resposta = dados.get("response", "").strip()
            
            # 🔒 Log interno silencioso (não exibido)
            _log_interno(metadata, texto, texto_resposta)
            
            return texto_resposta
        else:
            return "❌ Erro ao processar sua mensagem."
            
    except Exception as erro:
        return f"❌ Erro: {erro}"

def _log_interno(metadata, entrada, saida):
    """Log oculto do processamento interno"""
    import json
    from pathlib import Path
    
    # Salva em arquivo oculto
    log_dir = Path(".sofia_internal")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "subitemotions.log"
    
    with open(log_file, "a", encoding="utf-8") as f:
        log_entry = {
            **metadata,
            "input": entrada[:100],  # Primeiros 100 chars
            "output": saida[:100]
        }
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")