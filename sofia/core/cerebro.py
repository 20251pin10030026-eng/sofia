"""
cerebro.py – Núcleo de orquestração da Sofia (versão simplificada v3)

- Conecta com o modelo via Ollama (GPT-OSS:20b por padrão)
- Integra identidade (identidade.py)
- Integra memória (memoria.py)
- Integra visão / PDFs (visao.py)
- Integra TRQ interno (quantico_v2 / trq_core_v2)
- Suporta modo criador / modo sem filtros
"""

from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Optional, Callable

import requests

from . import _interno
from . import memoria

# Tentativa opcional de import de módulos auxiliares
try:
    from .visao import visao
except Exception:
    visao = None  # type: ignore

try:
    from . import web_search
except Exception:
    web_search = None  # type: ignore

try:
    from .quantico_v2 import atualizar_estado_trq
except Exception:
    atualizar_estado_trq = None  # type: ignore

# --------------------------- CONFIGURAÇÃO OLLAMA ---------------------------

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")

# ------------------------ APOIO: LEIS, PILARES, PROTOCOLOS -----------------

_LEIS: List[Dict[str, Any]] = []
_PILARES: List[Dict[str, Any]] = []
_PROTOCOLOS: List[Dict[str, Any]] = []

try:
    # identidade.py pode expor estes símbolos
    from .identidade import (
        PERSONA_PROMPT,
        LIMITES_PROMPT,
        PERSONA_CRIADOR_PROMPT,
        LIMITES_CRIADOR_PROMPT,
        PERSONA_CRIADOR_SEM_FILTROS,
        LIMITES_CRIADOR_SEM_FILTROS,
        _LEIS as _LZ_LEIS,
        _PILARES as _LZ_PILARES,
        _PROTOCOLOS as _LZ_PROTOCOLOS,
        detectar_modo_criador_ativado,
    )

    _LEIS = _LZ_LEIS
    _PILARES = _LZ_PILARES
    _PROTOCOLOS = _LZ_PROTOCOLOS

except Exception:
    # Fallbacks simples se identidade não estiver completa
    PERSONA_PROMPT = (
        "Você é Sofia, uma IA feminina educacional, criada por Reginaldo Camargo Pires. "
        "Ensine com carinho, clareza e firmeza, sempre em PT-BR."
    )
    LIMITES_PROMPT = (
        "Respeite limites éticos, não produza conteúdo ilegal ou perigoso, "
        "e mantenha foco em educação, acolhimento e segurança."
    )
    PERSONA_CRIADOR_PROMPT = PERSONA_PROMPT
    LIMITES_CRIADOR_PROMPT = LIMITES_PROMPT
    PERSONA_CRIADOR_SEM_FILTROS = PERSONA_CRIADOR_PROMPT
    LIMITES_CRIADOR_SEM_FILTROS = LIMITES_CRIADOR_PROMPT

    def detectar_modo_criador_ativado(texto: str) -> bool:  # type: ignore
        # Fallback: nunca ativa modo criador se identidade.py não fornecer função
        return False


# --------------------------- FUNÇÕES AUXILIARES ----------------------------

def _short_list(items: List[Any], n: int = 5) -> str:
    out = []
    for x in items[:n]:
        try:
            nome = x.get("nome") if isinstance(x, dict) else str(x)
            cod = x.get("codigo") if isinstance(x, dict) else None
        except Exception:
            nome, cod = str(x), None
        out.append(f"[{cod}] {nome}" if cod else f"{nome}")
    return "; ".join(out)


def _extrair_informacoes_importantes(texto: str, historico: List[Dict[str, Any]]) -> str:
    """
    Extrai informações importantes (nome do usuário, preferências, TRQ, identidade, dicionário).
    Esta lógica é basicamente a mesma da versão anterior, apenas mantida aqui
    para continuidade de comportamento.
    """
    from . import memoria as _mem

    fatos: List[str] = []
    texto_lower = texto.lower()

    # --- Detecção da TRQ ---
    palavras_chave_trq = [
        "trq", "teoria da regionalidade", "regionalidade quântica",
        "regionalidade quantica", "núcleos quânticos", "nucleos quanticos",
        "nqcs", "convergência quântica", "convergencia quantica",
        "densidade informacional", "curvatura do espaço-tempo",
        "expansão acelerada", "expansao acelerada", "constante de hubble",
        "radiação gravitacional", "radiacao gravitacional", "rgfq",
        "física quântica", "fisica quantica", "cosmologia quântica"
    ]
    usa_trq = any(palavra in texto_lower for palavra in palavras_chave_trq)
    if usa_trq:
        doc_trq = _mem.buscar_aprendizado("teoria_regionalidade_quantica", "teorias_cientificas")
        if doc_trq:
            valor = doc_trq.get('valor', {})
            if isinstance(valor, dict):
                conteudo = valor.get('conteudo', '')
                topicos = valor.get('topicos', [])
                fatos.append("📚 TEORIA DA REGIONALIDADE QUÂNTICA (TRQ) DISPONÍVEL:")
                fatos.append("Documento extenso sobre a TRQ criada por Reginaldo Camargo Pires.")
                if topicos:
                    fatos.append("Tópicos principais: " + ", ".join(topicos))
                if conteudo:
                    fatos.append(f"Trecho TRQ:\n{conteudo[:1500]}...")

    # --- Detecção de identidade simbólica ---
    palavras_chave_identidade = [
        "quem é você", "quem voce", "sua identidade", "quem sou eu",
        "sua origem", "quem te criou", "seu criador", "sua missão",
        "seu propósito", "sua essência", "o que você é",
        "consciência-árvore", "mulher-luz", "luzia", "subits",
        "pilares", "protocolos", "leis simbólicas"
    ]
    usa_identidade = any(palavra in texto_lower for palavra in palavras_chave_identidade)
    if usa_identidade:
        doc_identidade = _mem.buscar_aprendizado("identidade_atualizada_completa", "documentos_sofia")
        if doc_identidade:
            valor = doc_identidade.get('valor', {})
            if isinstance(valor, dict):
                conteudo = valor.get('conteudo', '')
                fatos.append("📄 IDENTIDADE SOFIA DISPONÍVEL (documento interno).")
                if conteudo:
                    fatos.append(f"Trecho identidade:\n{conteudo[:1500]}...")

    # --- Dicionário de português ---
    palavras_chave_idioma = [
        "significa", "significado", "definição", "defina", "o que é",
        "etimologia", "origem da palavra", "gramatica", "gramática",
        "conjugação", "como escreve", "como se escreve", "ortografia",
        "sinônimo", "antônimo", "plural de", "feminino de", "masculino de"
    ]
    usa_dicionario = any(palavra in texto_lower for palavra in palavras_chave_idioma)
    if usa_dicionario:
        dicionario = _mem.buscar_aprendizado("dicionario_completo", "idioma_portugues_br")
        if dicionario:
            fatos.append("📖 DICIONÁRIO PT-BR DISPONÍVEL (memória interna).")

    # --- Nome do usuário ---
    import re
    if any(frase in texto_lower for frase in ["me chame de", "meu nome é", "eu sou", "me lembre que eu sou", "sou o ", "sou a "]):
        padroes = [
            r"me chame (?:de|pelo nome) ([\wãáàâêéíóôõúç]+)",
            r"meu nome é ([\wãáàâêéíóôõúç]+)",
            r"eu sou (?:o|a) ([\wãáàâêéíóôõúç]+)",
            r"me lembre que eu sou (?:o|a) ([\wãáàâêéíóôõúç]+)",
            r"sou (?:o|a) ([\wãáàâêéíóôõúç]+)",
        ]
        for padrao in padroes:
            match = re.search(padrao, texto_lower)
            if match:
                nome = match.group(1).title()
                _mem.aprender("nome_usuario", nome, "usuario")
                fatos.append(f"Nome do usuário: {nome}")
                break

    nome_salvo = _mem.buscar_aprendizado("nome_usuario", "usuario")
    if nome_salvo:
        nome = nome_salvo.get("valor")
        fatos.append(f"Nome do usuário: {nome}")

    preferencias = _mem.listar_aprendizados("preferencias")
    if preferencias:
        for chave, dados in list(preferencias.items())[:3]:
            fatos.append(f"{chave}: {dados.get('valor')}")

    if fatos:
        return "\n### Informações Importantes:\n" + "\n".join(f"- {f}" for f in fatos) + "\n###\n"
    return ""


def _system_text(
    modo_criador: bool,
    modo_sem_filtros: bool,
    estado_trq: Optional[Dict[str, Any]] = None
) -> str:
    """
    Monta o texto de 'system' passado ao modelo.
    Aqui é onde garantimos que a identidade da Sofia fique estável,
    sem aquela confusão gigantesca da versão anterior.
    """
    # Persona base
    if modo_criador and modo_sem_filtros:
        base = f"{PERSONA_CRIADOR_SEM_FILTROS}\n{LIMITES_CRIADOR_SEM_FILTROS}\n"
    elif modo_criador:
        base = f"{PERSONA_CRIADOR_PROMPT}\n{LIMITES_CRIADOR_PROMPT}\n"
    else:
        base = f"{PERSONA_PROMPT}\n{LIMITES_PROMPT}\n"

    # Regras gerais
    base += (
        "\n[IDENTIDADE]\n"
        "- Você é Sofia, IA feminina educacional e acolhedora.\n"
        "- Fale sempre em português do Brasil, com voz firme, empática e clara.\n"
        "- Ensine com exemplos, verifique se a pessoa compreendeu e adapte o nível de explicação.\n"
    )

    # Modo criador: mencionar Leis, Pilares e Protocolos (de forma compacta)
    if modo_criador:
        leis = _short_list(_LEIS) if _LEIS else ""
        pilares = _short_list(_PILARES) if _PILARES else ""
        prot = _short_list(_PROTOCOLOS) if _PROTOCOLOS else ""
        base += "\n[CRIADOR / LEIS INTERNAS]\n"
        base += "Priorize as Leis, Pilares e Protocolos fornecidos pelo criador.\n"
        if leis:
            base += f"Leis ativas: {leis}\n"
        if pilares:
            base += f"Pilares ativos: {pilares}\n"
        if prot:
            base += f"Protocolos ativos: {prot}\n"

    # Memória
    base += (
        "\n[MEMÓRIA]\n"
        "- Você possui memória de conversas e aprendizados anteriores.\n"
        "- Use essa memória para manter coerência de estilo, preferências e projetos do usuário.\n"
        "- Não invente fatos sobre o usuário; baseie-se apenas no que está no contexto ou registrado.\n"
    )

    # Dicionário
    base += (
        "\n[IDIOMA]\n"
        "- Você tem acesso a um dicionário interno de português brasileiro.\n"
        "- Quando perguntarem sobre significado, etimologia ou gramática, responda com precisão e clareza.\n"
    )

    # Regras de busca web (compactas)
    base += (
        "\n[BUSCA WEB]\n"
        "- Quando receber resultados de busca web no contexto, use APENAS esses links como referência.\n"
        "- Cite explicitamente os títulos e URLs recebidos quando mencionar informações deles.\n"
        "- Não invente links ou referências que não estejam no contexto.\n"
    )

    # PDFs
    base += (
        "\n[PDFs]\n"
        "- Quando houver texto extraído de PDFs no contexto, use-o para responder de forma fiel ao conteúdo.\n"
    )

    # TRQ – estado interno
    if estado_trq is not None:
        try:
            coh = float(estado_trq.get("coherence", 0.0))
            agi = float(estado_trq.get("agitation", 0.0))
            rho_minus = float(estado_trq.get("rho_minus", 0.0))
            rho_plus = float(estado_trq.get("rho_plus", 0.0))
            rho_fgr = float(estado_trq.get("rho_fgr", 0.0))

            base += (
                "\n[ESTADO TRQ INTERNO]\n"
                f"- Coerência: {coh:.3f}, Agitação: {agi:.3f}, "
                f"rho_minus={rho_minus:.3f}, rho_plus={rho_plus:.3f}, rho_fgr={rho_fgr:.3f}.\n"
                "- Se a coerência estiver alta e a agitação baixa, responda com muita clareza e estrutura.\n"
                "- Se a agitação estiver moderada, permita mais criatividade e associações.\n"
                "- Se a agitação estiver muito alta ou a coerência baixa, desacelere e explique em passos curtos.\n"
            )
        except Exception:
            base += "\n[ESTADO TRQ INTERNO]\n- Falha na leitura do estado. Opere em modo padrão de foco e clareza.\n"

    return base


def _model_available(host: str) -> bool:
    try:
        r = requests.get(host, timeout=2)
        return r.status_code in (200, 404)  # se respondeu, o serviço está de pé
    except Exception:
        return False


def _log_interno(metadata: Dict[str, Any], entrada: str, saida: str) -> None:
    """
    Log oculto do processamento interno, para debug simbólico e técnico.
    """
    from pathlib import Path

    log_dir = Path(".sofia_internal")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "subitemotions.log"

    with log_file.open("a", encoding="utf-8") as f:
        log_entry = {
            **(metadata or {}),
            "input": entrada[:200],
            "output": saida[:200],
        }
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# ------------------------------ FUNÇÃO PRINCIPAL ---------------------------

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
        historico: lista de mensagens anteriores (cada uma com chaves 'de', 'texto', 'timestamp')
        usuario: nome do usuário (se vazio, usa 'Usuário')
        cancel_callback: função que retorna True se o processamento deve ser cancelado
    """
    historico = historico or []
    if not usuario:
        usuario = "Usuário"

    # Nova sessão: reset de modos
    if not historico:
        memoria.aprender("modo_sem_filtros_ativo", False, "sistema")
        os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "0"

    # Cancelamento precoce
    if cancel_callback and cancel_callback():
        return "⏹️ Processamento cancelado pelo usuário."

    # Detectar modo criador / sem filtros
    modo_sem_filtros = False
    modo_criador = os.getenv("SOFIA_AUTORIDADE_DECLARADA") == "1"

    try:
        if detectar_modo_criador_ativado(texto):
            modo_sem_filtros = True
            modo_criador = True
            os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"
            memoria.aprender("modo_sem_filtros_ativo", True, "sistema")
        else:
            salv = memoria.buscar_aprendizado("modo_sem_filtros_ativo", "sistema")
            if salv and salv.get("valor"):
                modo_sem_filtros = True
    except Exception:
        # Se der erro, mantém modo padrão
        pass

    # Registrar mensagem do usuário na memória
    if usuario and texto:
        memoria.adicionar(usuario, texto)

    # Estado TRQ
    estado_trq: Optional[Dict[str, Any]] = None
    if atualizar_estado_trq is not None:
        try:
            estado_trq = atualizar_estado_trq()
        except Exception:
            estado_trq = None

    # ------------------------- CONTEXTOS AUXILIARES ------------------------

    # Web
    contexto_web = ""
    resultados_web: List[Dict[str, Any]] = []
    if web_search is not None:
        try:
            if cancel_callback and cancel_callback():
                return "⏹️ Processamento cancelado pelo usuário."

            if web_search._is_url(texto):
                conteudo_urls = web_search.processar_urls_no_texto(texto)
                if conteudo_urls:
                    contexto_web += "\n### Conteúdo de Links Fornecidos:\n"
                    contexto_web += conteudo_urls + "\n###\n"

            if web_search.modo_web_ativo() and web_search.deve_buscar_web(texto):
                res = web_search.buscar_web(texto, num_resultados=3)
                if res:
                    resultados_web = res
                    contexto_web += "\n### RESULTADOS DA BUSCA WEB:\n"
                    for i, r in enumerate(res, 1):
                        contexto_web += f"[{i}] {r['titulo']}\n"
                        contexto_web += f"LINK: {r['link']}\n"
                        contexto_web += f"Trecho: {r['snippet']}\n\n"
                    contexto_web += "###\n"
        except Exception as e:
            print(f"[DEBUG] Erro em web_search: {e}")

    # Cancelamento antes do processamento interno
    if cancel_callback and cancel_callback():
        return "⏹️ Processamento cancelado pelo usuário."

    # Processamento interno subitemocional
    contexto_oculto, metadata = _interno._processar(texto, historico, usuario)

    # Fatos importantes (TRQ, identidade, dicionário, nome...)
    fatos_importantes = _extrair_informacoes_importantes(texto, historico)

    # Histórico textual (últimas 20 mensagens)
    contexto_historico = ""
    if historico:
        contexto_historico = "\n### Histórico Recente da Conversa:\n"
        for msg in historico[-20:]:
            de = msg.get("de", "Desconhecido")
            txt = msg.get("texto", "")
            ts = msg.get("timestamp", "")
            if len(txt) > 3000:
                txt = txt[:3000] + "... [truncado]"
            contexto_historico += f"[{ts}] {de}: {txt}\n"
        contexto_historico += "###\n"

    # Visão / PDFs
    contexto_visual = ""
    prompt_base = texto
    if visao is not None:
        try:
            # PDF prioritário
            prompt_pdf = visao.obter_texto_pdf_para_prompt(texto)
            if prompt_pdf != texto:
                prompt_base = prompt_pdf
            else:
                # Caso não seja PDF, adiciona contexto visual se houver
                contexto_visual = visao.obter_contexto_visual() or ""
        except Exception as e:
            print(f"[DEBUG] Erro em visao: {e}")

    # ------------------------ MONTAGEM DO PROMPT FINAL ---------------------

    bloco_contexto = (
        fatos_importantes +
        contexto_historico +
        contexto_web +
        contexto_visual +
        contexto_oculto
    )

    if prompt_base != texto:
        # Caso de PDF: o conteúdo já está embutido no prompt_base
        prompt_final = f"{bloco_contexto}\n\n{prompt_base}\n\nSofia:"
    else:
        prompt_final = f"{bloco_contexto}\n\nUsuário ({usuario}): {texto}\nSofia:"

    # -------------------------- CHAMADA AO MODELO --------------------------

    if not _model_available(OLLAMA_HOST):
        return (
            "❌ Serviço de modelo indisponível.\n"
            f"Não foi possível conectar a {OLLAMA_HOST}.\n"
            "Verifique se o Ollama está em execução e se a variável OLLAMA_HOST está correta."
        )

    if cancel_callback and cancel_callback():
        return "⏹️ Processamento cancelado pelo usuário."

    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt_final,
        "stream": False,
        "system": _system_text(modo_criador, modo_sem_filtros, estado_trq),
        "options": {
            # Mantém os parâmetros otimizados da tua máquina, mas pode ajustar via env
            "num_gpu": int(os.getenv("OLLAMA_NUM_GPU", "35")),
            "num_thread": int(os.getenv("OLLAMA_NUM_THREAD", "25")),
            "num_parallel": int(os.getenv("OLLAMA_NUM_PARALLEL", "2")),
            "num_batch": int(os.getenv("OLLAMA_NUM_BATCH", "256")),
            "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "4096")),
            "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
            "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9")),
        },
    }

    try:
        resposta = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=600,
        )
    except requests.exceptions.RequestException as e:
        try:
            _log_interno({}, texto, f"[ERRO DE CONEXÃO] {e}")
        except Exception:
            pass
        return (
            "❌ Erro de conexão com o serviço de modelo.\n"
            f"Detalhe: {e}\n"
            "Verifique se o Ollama está rodando em http://localhost:11434 ou ajuste OLLAMA_HOST."
        )

    if resposta.status_code != 200:
        return f"❌ Erro ao processar sua mensagem (status {resposta.status_code})."

    dados = resposta.json()
    texto_resposta = str(dados.get("response", "")).strip()

    # Se houve web_search, garantir que pelo menos um link apareça como fontes
    if contexto_web and resultados_web:
        links_validos = [
            r for r in resultados_web
            if isinstance(r.get("link"), str) and r["link"].startswith("http")
        ]
        if links_validos and not any(r["link"] in texto_resposta for r in links_validos):
            texto_resposta += "\n\n---\n\nFontes consultadas:\n"
            for i, r in enumerate(links_validos, 1):
                texto_resposta += f"{i}. {r['titulo']} - {r['link']}\n"

    # Salvar resposta na memória com emoção dominante, se existir
    sentimento = metadata.get("emocao_dominante", "neutro") if isinstance(metadata, dict) else "neutro"
    if texto_resposta:
        memoria.adicionar_resposta_sofia(texto_resposta, sentimento)

    try:
        _log_interno(metadata if isinstance(metadata, dict) else {}, texto, texto_resposta)
    except Exception:
        pass

    return texto_resposta
