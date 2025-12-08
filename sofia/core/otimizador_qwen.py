# otimizador_qwen.py
import os
import json
import textwrap
import requests
from datetime import datetime
from typing import Dict, Any

# Endpoint do Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_QWEN = "qwen3-coder-30b-cpu"

BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs_execucao")
LOG_FILE = os.path.join(LOG_DIR, "qwen_execucoes.log")
QUANTICO_PATH = os.path.join(BASE_DIR, "quantico_v2.py")


def _garantir_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def _ler_codigo_quantico() -> str:
    try:
        with open(QUANTICO_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"# ERRO ao ler quantico_v2.py: {e}"


def _registrar_execucao(entry: Dict[str, Any]) -> None:
    _garantir_log_dir()
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **entry,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def obter_telemetria(max_linhas: int = 20) -> Dict[str, str]:
    """
    Lê o arquivo de log e devolve:
    - execucoes: últimas N linhas em texto
    - sugestao: última sugestão do Qwen (se existir)
    """
    if not os.path.exists(LOG_FILE):
        return {
            "execucoes": "Nenhum dado ainda.",
            "sugestao": ""
        }

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    ultimas = linhas[-max_linhas:]
    execucoes_texto = "\n".join(l.strip() for l in ultimas)

    # tenta pegar a última sugestão
    sugestao = ""
    for linha in reversed(ultimas):
        try:
            data = json.loads(linha)
            if "sugestao" in data:
                sugestao = data["sugestao"]
                break
        except Exception:
            continue

    return {
        "execucoes": execucoes_texto or "Nenhum dado ainda.",
        "sugestao": sugestao,
    }


def rodar_qwen_otimizador() -> Dict[str, str]:
    """
    Chama o Qwen via Ollama para analisar o quantico_v2.py
    e registrar em log.
    """
    codigo = _ler_codigo_quantico()

    prompt = textwrap.dedent(f"""
    Você é um especialista em Python, física teórica e otimização de código.
    Analise o seguinte arquivo quantico_v2.py, usado em uma teoria
    chamada TRQ (Teoria da Regionalidade Quântica).

    Objetivos:
    1. Identificar possíveis bugs, gargalos de desempenho e pontos frágeis.
    2. Sugerir melhorias claras.
    3. Propor uma versão otimizada dos trechos mais importantes.

    Código atual (quantico_v2.py):
    ```python
    {codigo}
    ```

    Responda em português, no formato:
    - Diagnóstico curto (máx. 6 linhas)
    - Sugestões de melhoria
    - Bloco de código sugerido (apenas o que for essencial)
    """)

    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO_QWEN,
            "prompt": prompt,
            "stream": False,
        },
        timeout=1800,
    )
    resp.raise_for_status()
    resposta_texto = resp.json().get("response", "").strip()

    # registra no log
    _registrar_execucao({
        "acao": "rodar_qwen",
        "sugestao": resposta_texto,
    })

    return {
        "sugestao": resposta_texto,
    }
