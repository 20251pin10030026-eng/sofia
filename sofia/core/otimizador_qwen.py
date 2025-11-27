# otimizador_qwen.py
import os
import json
import textwrap
import requests
from typing import List

# Endpoint do Ollama (ajuste se precisar)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_QWEN = "qwen3-coder-30b-cpu"  # o que criamos só CPU

BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs_execucao")
QUANTICO_PATH = os.path.join(BASE_DIR, "quantico_v2.py")


def _ler_logs(funcao: str, max_linhas: int = 50) -> List[dict]:
    path = os.path.join(LOG_DIR, f"{funcao}_log.jsonl")
    if not os.path.exists(path):
        return []

    registros = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_linhas:
                break
            try:
                registros.append(json.loads(line))
            except Exception:
                continue
    return registros


def _extrair_trecho_codigo(path: str, marcador: str) -> str:
    """
    Extrai um trecho do arquivo em torno de uma string 'marcador'
    (por exemplo, 'def simular_trq_floquet_v2').
    """
    with open(path, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    idx = None
    for i, linha in enumerate(linhas):
        if marcador in linha:
            idx = i
            break

    if idx is None:
        return ""

    inicio = max(0, idx - 5)
    fim = min(len(linhas), idx + 80)
    return "".join(linhas[inicio:fim])


def analisar_e_otimizar(funcao: str = "simular_trq_floquet_v2") -> str:
    logs = _ler_logs(funcao)
    trecho = _extrair_trecho_codigo(QUANTICO_PATH, f"def {funcao}")

    if not trecho:
        return "Não encontrei a função no quantico_v2.py."

    prompt = textwrap.dedent(f"""
    Você é um especialista em otimização numérica, física computacional e Python.

    A seguir está um trecho de código usado na simulação TRQ/Floquet de NQCs:

    ```python
    {trecho}
    ```

    Abaixo estão alguns registros reais de execução desta função,
    incluindo tempo de execução, tipos de argumentos e se houve erro:

    ```json
    {json.dumps(logs, ensure_ascii=False, indent=2)}
    ```

    TAREFA:

    1. Analise a COMPLEXIDADE e os gargalos de desempenho.
    2. Proponha otimizações CONCRETAS, incluindo:
       - uso mais inteligente de NumPy ou QuTiP,
       - remoção de loops redundantes,
       - reaproveitamento de operadores/hamiltonianos,
       - possíveis aproximações físicas que reduzam custo computacional
         sem destruir o sentido físico da TRQ (pode citar ideias).
    3. Forneça uma VERSÃO OTIMIZADA do código da função,
       com comentários explicando cada melhoria.
    4. Mantenha a assinatura da função e a intenção física original.

    Responda apenas com explicação curta + novo código.
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
    return resp.json()["response"]
