"""
cerebro.py — Sofia v2 com TRQ interno em `_interno`
-------------------------------------------------
Núcleo leve da Sofia:
- Identidade estável
- Memória
- Visão/PDF (se disponível)
- Web search (se disponível)
- Integração com TRQ/subitemoções via módulo `_interno`
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
from .memoria import obter_contexto_aprendizados, obter_resumo_conversas_recentes, obter_contexto_subitemotions

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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")


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
    contexto_oculto: str = ""
    metadata: Dict[str, Any] = {}
    try:
        resultado = _interno._processar(texto, historico, usuario)
        if resultado is not None and isinstance(resultado, tuple) and len(resultado) == 2:
            contexto_oculto, metadata = resultado
    except Exception:
        contexto_oculto, metadata = "", {}

    # -------------------- Exibir ESTADO QUÂNTICO INTERNO no terminal --------------------
    try:
        estado = metadata.get("estado")
        intensidade = metadata.get("intensidade")
        curv_cl = metadata.get("curvatura")
        resson = metadata.get("ressonancia")
        curv_trq = metadata.get("curvatura_trq")
        emaranh = metadata.get("emaranhamento_trq")
        ajuste_trq = metadata.get("ajuste_trq")

        print("\n=== ESTADO QUÂNTICO INTERNO – SOFIA (LOCAL) ===")
        print(f"🧩 SubitEmoção dominante : {estado}")
        if isinstance(intensidade, (int, float)):
            print(f"💓 Intensidade emocional : {intensidade:.3f}")
        else:
            print(f"💓 Intensidade emocional : {intensidade}")
        print(f"📐 Curvatura clássica TRQ: {curv_cl}")
        print(f"⏳ Ressonância temporal   : {resson}")
        print(f"🌌 Curvatura TRQ quântica: {curv_trq}")
        print(f"🔗 Emaranhamento TRQ      : {emaranh}")
        print(f"🎛️ Ajuste de modo TRQ     : {ajuste_trq}")
        print("================================================\n")
    except Exception as e:
        print(f"[DEBUG] Erro ao exibir estado quântico: {e}")

    # -------------------- Carregar aprendizados de longo prazo --------------------
    contexto_aprendizados = ""
    try:
        contexto_aprendizados = obter_contexto_aprendizados(max_chars=6000)
        if contexto_aprendizados:
            print(f"[DEBUG] Aprendizados carregados: {len(contexto_aprendizados)} chars")
    except Exception as e:
        print(f"[DEBUG] Erro ao carregar aprendizados: {e}")

    # -------------------- Carregar histórico de subitemotions --------------------
    contexto_subitemotions = ""
    try:
        contexto_subitemotions = obter_contexto_subitemotions(max_registros=10, max_chars=2000)
        if contexto_subitemotions:
            print(f"[DEBUG] Subitemotions carregados: {len(contexto_subitemotions)} chars")
    except Exception as e:
        print(f"[DEBUG] Erro ao carregar subitemotions: {e}")

    # -------------------- Montagem do prompt final --------------------
    bloco_contexto = (
        contexto_aprendizados + "\n\n" +  # Aprendizados primeiro (mais importante)
        contexto_subitemotions + "\n\n" +  # Histórico emocional/TRQ
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
            "e se o modelo gpt-oss:20b está disponível."
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
            # ========== CONFIGURAÇÕES DE MÁXIMO DESEMPENHO ==========
            # Hardware: Intel Xeon E5-2630 v2 (6 cores/12 threads) + GTX 1650 (4GB)
            
            # GPU: Usar TODAS as camadas possíveis na GPU (máximo desempenho)
            # -1 = usar todas as camadas que couberem na VRAM
            # Para GTX 1650 4GB com modelo 20B: ~20-25 camadas cabem
            "num_gpu": int(os.getenv("OLLAMA_NUM_GPU", "99")),
            
            # CPU: Usar TODOS os 12 threads disponíveis
            "num_thread": int(os.getenv("OLLAMA_NUM_THREAD", "12")),
            
            # Processamento paralelo: aumentar para usar mais recursos
            "num_parallel": int(os.getenv("OLLAMA_NUM_PARALLEL", "2")),
            
            # Batch size: maior = mais rápido (usa mais VRAM)
            # Para 4GB VRAM, 512 é um bom equilíbrio
            "num_batch": int(os.getenv("OLLAMA_NUM_BATCH", "512")),
            
            # Contexto: reduzir para aumentar velocidade (menos memória)
            "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "2048")),
            
            # Parâmetros de geração
            "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.65")),
            "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9")),
            
            # Otimizações adicionais
            "use_mmap": True,        # Mapear modelo na memória (mais rápido)
            "use_mlock": False,      # Não travar na RAM (economiza memória)
            "main_gpu": 0,           # Usar GPU principal
            "low_vram": False,       # Modo VRAM baixa desativado (usar tudo)
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
        # Usa a emoção dominante se existir; senão cai para o estado; senão "neutro"
        sentimento = (
            metadata.get("emocao_dominante")
            or metadata.get("estado")
            or "neutro"
        )

    if resposta:
        try:
            memoria.adicionar_resposta_sofia(resposta, sentimento)
        except Exception:
            pass

        # Log de subitemotions (igual ao cloud)
        try:
            _log_subitemotions(metadata or {}, texto, resposta, OLLAMA_MODEL)
        except Exception as e:
            print(f"[DEBUG] Erro ao salvar log subitemotions: {e}")

    return resposta


def _log_subitemotions(metadata: dict, entrada: str, saida: str, modelo: str):
    """Log do processamento interno das subitemotions."""
    import json
    from pathlib import Path
    from datetime import datetime

    log_dir = Path(__file__).resolve().parents[1] / ".sofia_internal"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "subitemotions.log"

    with open(log_file, "a", encoding="utf-8") as f:
        log_entry = {
            "estado": metadata.get("estado"),
            "intensidade": metadata.get("intensidade"),
            "curvatura": metadata.get("curvatura"),
            "curvatura_trq": metadata.get("curvatura_trq"),
            "emaranhamento_trq": metadata.get("emaranhamento_trq"),
            "ressonancia": metadata.get("ressonancia"),
            "autoridade": metadata.get("autoridade"),
            "web_info": str(metadata.get("web_info")) if metadata.get("web_info") else None,
            "timestamp": datetime.now().isoformat(),
            "input": entrada[:200],
            "output": saida[:200],
            "model": modelo,
        }
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
