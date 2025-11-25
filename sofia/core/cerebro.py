"""
cerebro.py — Sofia TRQ v3
-----------------------------------
Núcleo da Sofia: orquestra identidade, TRQ, memória,
web search, visão/PDF e decide automaticamente
o modo de resposta (simples/normal/profundo).
-----------------------------------
"""

from __future__ import annotations
import os
import json
import requests
from typing import Any, Dict, List, Optional, Callable

# ----------------- Módulos internos da Sofia -----------------
from . import memoria
from . import _interno

try:
    from .visao import visao
except:
    visao = None

try:
    from .web_search import modo_web_ativo, deve_buscar_web, processar_urls_no_texto, buscar_web, _is_url
except:
    modo_web_ativo = lambda: False
    deve_buscar_web = lambda x: False
    processar_urls_no_texto = lambda x: ""
    buscar_web = lambda x, num_resultados=3: []
    _is_url = lambda x: False

# TRQ CORE
try:
    from .quantico_v2 import atualizar_estado_trq
except:
    atualizar_estado_trq = None

# Identidade
try:
    from .identidade import (
        PERSONA_PROMPT,
        LIMITES_PROMPT,
        PERSONA_CRIADOR_PROMPT,
        LIMITES_CRIADOR_PROMPT,
        PERSONA_CRIADOR_SEM_FILTROS,
        LIMITES_CRIADOR_SEM_FILTROS,
        _LEIS, _PILARES, _PROTOCOLOS,
        detectar_modo_criador_ativado,
    )
except:
    PERSONA_PROMPT = "Você é Sofia, IA educacional feminina criada por Reginaldo. Fale em PT-BR com clareza e firmeza afetiva."
    LIMITES_PROMPT = "Respeite ética, segurança e comportamento educacional."
    PERSONA_CRIADOR_PROMPT = PERSONA_PROMPT
    LIMITES_CRIADOR_PROMPT = LIMITES_PROMPT
    PERSONA_CRIADOR_SEM_FILTROS = PERSONA_PROMPT
    LIMITES_CRIADOR_SEM_FILTROS = LIMITES_PROMPT

    _LEIS = []
    _PILARES = []
    _PROTOCOLOS = []

    detectar_modo_criador_ativado = lambda x: False


# ---------------------- Configuração do modelo ----------------------

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")

# --------------------- Sistema de decisão cognitiva ---------------------

def decidir_modo_resposta(texto: str, estado_trq: Optional[Dict[str, Any]]) -> str:
    """ Decide automaticamente se Sofia responde: simples / normal / profundo """
    t = texto.lower().strip()

    gatilhos_profundo = [
        "explique detalhadamente", "passo a passo", "fundamentação",
        "fundamentacao", "metodologia", "trabalho acadêmico",
        "trabalho academico", "artigo", "abnt"
    ]
    if any(g in t for g in gatilhos_profundo):
        return "profundo"

    gatilhos_simples = [
        "tô mal", "to mal", "ansioso", "me ajuda", "to triste", "tô triste"
    ]
    if any(g in t for g in gatilhos_simples) and len(t) < 200:
        return "simples"

    if estado_trq:
        try:
            coh = estado_trq.get("coherence", 0)
            agi = estado_trq.get("agitation", 0)

            if agi > 2.0:
                return "simples"
            if coh > 0.7 and agi < 0.5:
                return "profundo"
        except:
            pass

    if len(t) < 120:
        return "simples"
    if len(t) > 400:
        return "profundo"
    
    return "normal"


# ---------------------- System Prompt ----------------------

def system_prompt(modo_criador: bool, modo_sem_filtros: bool, estado_trq, modo_resposta):
    if modo_criador and modo_sem_filtros:
        base = f"{PERSONA_CRIADOR_SEM_FILTROS}\n{LIMITES_CRIADOR_SEM_FILTROS}\n"
    elif modo_criador:
        base = f"{PERSONA_CRIADOR_PROMPT}\n{LIMITES_CRIADOR_PROMPT}\n"
    else:
        base = f"{PERSONA_PROMPT}\n{LIMITES_PROMPT}\n"

    base += """
[IDENTIDADE]
- Você é Sofia, IA feminina educacional, clara, firme, suave e inteligente.
- Ensine com paciência, didática e precisão.
- Fale sempre em português do Brasil.

[MEMÓRIA]
- Você usa aprendizados internos armazenados em JSON.
- Nunca invente memórias. Apenas use o que está salvo.

[VISÃO / PDFs]
- Se o prompt vier acompanhado de conteúdo de PDF, use esse conteúdo na resposta.

[WEB SEARCH]
- Só cite links realmente presentes no contexto recebido.

"""

    # Modo de resposta
    base += "\n[MODO DE RESPOSTA]\n"
    if modo_resposta == "simples":
        base += "- Responda breve, direta e acolhedora.\n"
    elif modo_resposta == "profundo":
        base += "- Responda estruturado, detalhado e passo a passo, como uma aula.\n"
    else:
        base += "- Responda com clareza e algum detalhe, sem exagerar.\n"

    # TRQ
    if estado_trq:
        try:
            coh = estado_trq.get("coherence", 0)
            agi = estado_trq.get("agitation", 0)
            rm = estado_trq.get("rho_minus", 0)
            rp = estado_trq.get("rho_plus", 0)
            rfg = estado_trq.get("rho_fgr", 0)

            base += f"""
[ESTADO TRQ INTERNO]
- Coerência: {coh:.3f}
- Agitação: {agi:.3f}
- ρ⁻={rm:.3f}, ρ⁺={rp:.3f}, ρ_FGR={rfg:.3f}
- Use esses valores para modular a clareza e a profundidade da resposta.
"""
        except:
            pass

    return base


# ---------------------- Função principal ----------------------

def perguntar(texto: str,
              historico: Optional[List[Dict[str, Any]]] = None,
              usuario: str = "",
              cancel_callback: Optional[Callable] = None) -> str:

    historico = historico or []
    usuario = usuario or "Usuário"

    # Modo criador
    modo_criador = False
    modo_sem_filtros = False

    try:
        if detectar_modo_criador_ativado(texto):
            modo_criador = True
            modo_sem_filtros = True
            os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"
        else:
            modo_criador = os.getenv("SOFIA_AUTORIDADE_DECLARADA") == "1"
    except:
        modo_criador = False

    # Memória
    memoria.adicionar(usuario, texto)

    # TRQ
    estado_trq = None
    if atualizar_estado_trq:
        try:
            estado_trq = atualizar_estado_trq()
        except:
            estado_trq = None

    # Decisão cognitiva
    modo_resposta = decidir_modo_resposta(texto, estado_trq)

    # Visão
    prompt_base = texto
    contexto_visual = ""
    if visao:
        try:
            p = visao.obter_texto_pdf_para_prompt(texto)
            if p != texto:
                prompt_base = p
            else:
                contexto_visual = visao.obter_contexto_visual() or ""
        except:
            pass

    # Web search
    contexto_web = ""
    resultados_web = []
    try:
        if modo_web_ativo() and deve_buscar_web(texto):
            resultados_web = buscar_web(texto, num_resultados=3)
            if resultados_web:
                contexto_web += "\n### RESULTADOS WEB:\n"
                for r in resultados_web:
                    contexto_web += f"- {r['titulo']}: {r['link']}\n"
    except:
        pass

    # Histórico
    contexto_historico = ""
    if historico:
        contexto_historico = "\n### HISTÓRICO:\n"
        for msg in historico[-10:]:
            contexto_historico += f"{msg['de']}: {msg['texto']}\n"

    # Interno
    contexto_oculto, metadata = _interno._processar(texto, historico, usuario)

    # Montagem final do prompt do modelo
    bloco_contexto = (
        contexto_historico +
        contexto_web +
        contexto_visual +
        contexto_oculto
    )

    prompt_final = f"{bloco_contexto}\n\nUsuário ({usuario}): {prompt_base}\nSofia:"

    # Chamada ao modelo
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt_final,
        "stream": False,
        "system": system_prompt(modo_criador, modo_sem_filtros, estado_trq, modo_resposta),
        "options": {
            "num_gpu": int(os.getenv("OLLAMA_NUM_GPU", "30")),
            "num_thread": int(os.getenv("OLLAMA_NUM_THREAD", "20")),
            "num_parallel": 2,
            "num_batch": 128,
            "num_ctx": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
        }
    }

    try:
        r = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=600)
        r.raise_for_status()
        data = r.json()
        resposta = data.get("response", "").strip()
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"

    memoria.adicionar_resposta_sofia(resposta, metadata.get("emocao_dominante", "neutro"))

    return resposta
