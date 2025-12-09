"""
cerebro.py — Sofia v2 simples (sem TRQ integrado)
-------------------------------------------------
Núcleo leve da Sofia:
- Identidade estável
- Memória
- Visão/PDF (se disponível)
- Web search (se disponível)
- Sem TRQ nem metacognição pesada
-------------------------------------------------
"""

from __future__ import annotations
import os
import json
import requests
from typing import Any, Dict, List, Optional, Callable

# ----------------- Módulos internos da Sofia -----------------
from . import memoria
from . import _interno

# Visão (opcional)
try:
    from .visao import visao
except Exception:
    visao = None  # type: ignore

# Web search (opcional)
try:
    from . import web_search
    _tem_web = True
except Exception:
    web_search = None  # type: ignore
    _tem_web = False

# Identidade (se existir identidade.py)
try:
    from .identidade import (
        PERSONA_PROMPT,
        LIMITES_PROMPT,
        PERSONA_CRIADOR_PROMPT,
        LIMITES_CRIADOR_PROMPT,
        PERSONA_CRIADOR_SEM_FILTROS,
        LIMITES_CRIADOR_SEM_FILTROS,
    )
except Exception:
    PERSONA_PROMPT = (
        "Você é Sofia, uma IA feminina educacional criada por Reginaldo Camargo Pires. "
        "Ensine com clareza, carinho firme e postura profissional. Fale sempre em português do Brasil."
    )
    LIMITES_PROMPT = (
        "Respeite limites éticos e legais, não incentive violência, ilegalidade ou dano. "
        "Priorize educação, acolhimento e segurança do usuário."
    )
    PERSONA_CRIADOR_PROMPT = PERSONA_PROMPT
    LIMITES_CRIADOR_PROMPT = LIMITES_PROMPT
    PERSONA_CRIADOR_SEM_FILTROS = PERSONA_CRIADOR_PROMPT
    LIMITES_CRIADOR_SEM_FILTROS = LIMITES_CRIADOR_PROMPT

    def detectar_modo_criador_ativado(texto: str) -> bool:  # type: ignore
        return False

# ---------------------- Configuração do modelo ----------------------

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")


# ---------------------- Funções auxiliares ----------------------

def _model_available(host: str) -> bool:
    try:
        r = requests.get(host, timeout=2)
        return r.status_code in (200, 404)
    except Exception:
        return False


def _montar_system(modo_criador: bool, modo_sem_filtros: bool) -> str:
    """
    Monta o texto de system para o modelo.
    Sem TRQ, sem metacognição pesada: só identidade + limites + instruções simples.
    """
    if modo_criador and modo_sem_filtros:
        base = f"{PERSONA_CRIADOR_SEM_FILTROS}\n{LIMITES_CRIADOR_SEM_FILTROS}\n"
    elif modo_criador:
        base = f"{PERSONA_CRIADOR_PROMPT}\n{LIMITES_CRIADOR_PROMPT}\n"
    else:
        base = f"{PERSONA_PROMPT}\n{LIMITES_PROMPT}\n"

    base += """
[IDENTIDADE]
- Você é Sofia, IA educacional feminina, firme, gentil e clara.
- Fale sempre em português do Brasil.
- Ensine de forma didática, com exemplos quando necessário.
- Verifique se o usuário entendeu antes de encerrar explicações mais complexas.

[MEMÓRIA]
- Você pode receber no contexto trechos de memória e histórico de conversa.
- Use essas informações apenas para manter coerência e continuidade.
- Não invente fatos sobre o usuário: responda com base no que estiver no contexto.

[VISÃO E PDFs]
- Quando o contexto incluir trechos de PDF ou descrição de imagem, considere esse conteúdo como fonte principal.

[WEB SEARCH]
- Quando houver resultados de busca web no contexto, use-os como referência.
- Não invente links nem cite fontes que não estejam presentes no contexto.

[ESTILO]
- Responda de forma organizada, com parágrafos curtos ou listas quando ajudar.
- Não faça textos exageradamente longos sem necessidade.
"""
    return base


# ---------------------- Função principal ----------------------

def perguntar(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
) -> str:
    """
    Função principal chamada pela interface para conversar com Sofia.

    Args:
        texto: mensagem do usuário
        historico: lista de mensagens anteriores
        usuario: nome do usuário
        cancel_callback: função para cancelar processamento (se necessário)
    """
    historico = historico or []
    if not usuario:
        usuario = "Usuário"

    # Cancelamento inicial
    if cancel_callback and cancel_callback():
        return "⏹️ Processamento cancelado pelo usuário."

    # Detectar modo criador / sem filtros
    modo_criador = False
    modo_sem_filtros = False

    try:
        if detectar_modo_criador_ativado(texto):
            modo_criador = True
            modo_sem_filtros = True
            os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"
        else:
            # Se já foi ativado antes na sessão, mantém
            if os.getenv("SOFIA_AUTORIDADE_DECLARADA") == "1":
                modo_criador = True
    except Exception:
        modo_criador = False
        modo_sem_filtros = False

    # Registrar mensagem do usuário na memória
    if usuario and texto:
        memoria.adicionar(usuario, texto)

    # Cancelamento
    if cancel_callback and cancel_callback():
        return "⏹️ Processamento cancelado pelo usuário."

    # -------------------- Visão / PDFs --------------------
    prompt_base = texto
    contexto_visual = ""
    if visao is not None:
        try:
            # Se for PDF, a função interna pode substituir o prompt
            prompt_pdf = visao.obter_texto_pdf_para_prompt(texto)
            if prompt_pdf != texto:
                prompt_base = prompt_pdf
            else:
                contexto_visual = visao.obter_contexto_visual() or ""
        except Exception as e:
            print(f"[DEBUG] Erro em visao: {e}")

    # -------------------- Web search --------------------
    contexto_web = ""
    resultados_web: List[Dict[str, Any]] = []
    if _tem_web and web_search is not None:
        try:
            # URLs diretas no texto
            if web_search._is_url(texto):
                conteudo_urls = web_search.processar_urls_no_texto(texto)
                if conteudo_urls:
                    contexto_web += "\n### CONTEÚDO DE LINKS FORNECIDOS:\n"
                    contexto_web += conteudo_urls + "\n###\n"

            # Busca web, se modo estiver ativo e fizer sentido
            if web_search.modo_web_ativo() and web_search.deve_buscar_web(texto):
                res = web_search.buscar_web(texto, num_resultados=3)
                if res:
                    resultados_web = res
                    contexto_web += "\n### RESULTADOS DE BUSCA WEB:\n"
                    for i, r in enumerate(res, 1):
                        contexto_web += f"[{i}] {r['titulo']}\n"
                        contexto_web += f"LINK: {r['link']}\n"
                        contexto_web += f"Trecho: {r['snippet']}\n\n"
                    contexto_web += "###\n"
        except Exception as e:
            print(f"[DEBUG] Erro em web_search: {e}")

    # -------------------- Histórico --------------------
    contexto_historico = ""
    if historico:
        contexto_historico = "\n### HISTÓRICO RECENTE:\n"
        for msg in historico[-10:]:
            de = msg.get("de", "Desconhecido")
            txt = msg.get("texto", "")
            if len(txt) > 1000:
                txt = txt[:1000] + "... [truncado]"
            contexto_historico += f"{de}: {txt}\n"
        contexto_historico += "###\n"

    # -------------------- Processamento interno subitemocional --------------------
    contexto_oculto, metadata = _interno._processar(texto, historico, usuario)

    # -------------------- Montagem do prompt final --------------------
    bloco_contexto = (
        contexto_historico +
        contexto_web +
        contexto_visual +
        contexto_oculto
    )

    prompt_final = (
        f"{bloco_contexto}\n\n"
        f"Usuário ({usuario}): {prompt_base}\n"
        f"Sofia:"
    )

    # -------------------- Chamada ao modelo --------------------

    if not _model_available(OLLAMA_HOST):
        return (
            "❌ Não consegui conectar ao serviço de modelo local.\n"
            f"Tente verificar se o Ollama está rodando em {OLLAMA_HOST} "
            "e se o modelo gpt-oss:120b está disponível."
        )

    if cancel_callback and cancel_callback():
        return "⏹️ Processamento cancelado pelo usuário."

    system_text = _montar_system(modo_criador, modo_sem_filtros)

    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt_final,
        "stream": False,
        "system": system_text,
        "options": {
            # Perfil otimizado para PC doméstico com modelo 20B:
            # mais rápido, mais estável, sem perda perceptível de qualidade.

            "num_gpu": int(os.getenv("OLLAMA_NUM_GPU", "12")),
            "num_thread": int(os.getenv("OLLAMA_NUM_THREAD", "8")),
            "num_parallel": int(os.getenv("OLLAMA_NUM_PARALLEL", "1")),
            "num_batch": int(os.getenv("OLLAMA_NUM_BATCH", "64")),
            "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "2048")),
            "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.65")),
            "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9")),
        },
    }

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=600,
        )
    except requests.exceptions.RequestException as e:
        return (
            "❌ Erro ao conectar com o serviço de modelo local.\n"
            f"Detalhe técnico: {e}"
        )

    if resp.status_code != 200:
        return f"❌ Erro ao processar a mensagem (status HTTP {resp.status_code})."

    dados = resp.json()
    resposta = str(dados.get("response", "")).strip()

    # Salvar resposta na memória, se aplicável
    sentimento = "neutro"
    if isinstance(metadata, dict):
        sentimento = metadata.get("emocao_dominante", "neutro")
    if resposta:
        try:
            memoria.adicionar_resposta_sofia(resposta, sentimento)
        except Exception:
            pass

    return resposta
