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
import time
import requests
from typing import Any, Dict, List, Optional, Callable

# ----------------- Módulos internos da Sofia -----------------
from . import memoria
from . import _interno
from . import profiles

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

# Timeout de ponte (gpt-oss → fallback)
SOFIA_GPT_OSS_TIMEOUT_S = int(os.getenv("SOFIA_GPT_OSS_TIMEOUT_S", str(9 * 60)))
SOFIA_FALLBACK_MODEL = os.getenv("SOFIA_FALLBACK_MODEL", "llama3.1:8b")


def _perfil_local() -> str:
    """Retorna o perfil local atual: FAST ou QUALITY."""
    return os.getenv("SOFIA_LOCAL_PROFILE", "QUALITY").strip().upper() or "QUALITY"


def _resolver_modelo_local() -> str:
    """Seleciona o modelo local com base no profile (FAST/QUALITY)."""
    perfil = _perfil_local()
    if perfil == "FAST":
        return os.getenv("SOFIA_MODEL_FAST", "llama3.1:8b")
    if perfil == "QUALITY":
        return os.getenv("SOFIA_MODEL_QUALITY", "gpt-oss:20b")
    # fallback: respeita OLLAMA_MODEL
    return OLLAMA_MODEL


def _resolver_opcoes_ollama(modelo: str) -> Dict[str, Any]:
    """Retorna options do Ollama ajustadas ao modelo/hardware."""
    perfil = _perfil_local()

    # Defaults estáveis para GTX 1650 4GB + 12 threads
    # (perfil FAST usa mais GPU; QUALITY tende a precisar de mais CPU offload)
    if perfil == "FAST":
        defaults: Dict[str, Any] = {
            "num_gpu": int(os.getenv("OLLAMA_NUM_GPU", "-1")),
            "num_thread": int(os.getenv("OLLAMA_NUM_THREAD", "12")),
            "num_parallel": int(os.getenv("OLLAMA_NUM_PARALLEL", "1")),
            "num_batch": int(os.getenv("OLLAMA_NUM_BATCH", "256")),
            "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "2048")),
        }
    else:
        defaults = {
            "num_gpu": int(os.getenv("OLLAMA_NUM_GPU", "25")),
            "num_thread": int(os.getenv("OLLAMA_NUM_THREAD", "12")),
            "num_parallel": int(os.getenv("OLLAMA_NUM_PARALLEL", "1")),
            "num_batch": int(os.getenv("OLLAMA_NUM_BATCH", "128")),
            "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "2048")),
        }

    defaults.update(
        {
            "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.65")),
            "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9")),
            "use_mmap": True,
            "use_mlock": False,
            "main_gpu": 0,
        }
    )

    # Permite override por modelo específico, se quiser:
    # SOFIA_OLLAMA_NUM_BATCH_LLAMA3_1_8B=... etc (opcional)
    return defaults


def _ollama_generate(
    *,
    model: str,
    prompt: str,
    system: str,
    options: Dict[str, Any],
    timeout_s: int,
    cot_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Chama o Ollama. Se cot_callback for fornecido, usa streaming para
    enviar todos os tokens em tempo real (chain-of-thought / geração progressiva).
    """
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "options": options,
    }

    # Se temos callback de CoT, usamos streaming para enviar tokens progressivamente
    if cot_callback is not None:
        payload["stream"] = True
        full_response = []

        try:
            with requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json=payload,
                timeout=timeout_s,
                stream=True,
            ) as resp:
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}")

                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    token = chunk.get("response", "")
                    if token:
                        full_response.append(token)
                        # Enviar cada token em tempo real
                        try:
                            cot_callback(token)
                        except Exception:
                            pass

                    if chunk.get("done"):
                        break

        except requests.exceptions.Timeout:
            raise

        return "".join(full_response).strip()

    # Sem streaming (comportamento original)
    payload["stream"] = False
    resp = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json=payload,
        timeout=timeout_s,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}")

    dados = resp.json()
    return str(dados.get("response", "")).strip()


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
[ESTILO DE RESPOSTA]
- Use SEMPRE Markdown em português do Brasil.
- Comece com um título curto em negrito.
- Estruture em seções (##/###) quando houver múltiplos tópicos.
- Para dados estruturados (especificações, comparações), prefira tabelas com cabeçalho.
- Destaque números/chaves em **negrito**; use *itálico* para fontes/referências.
- Inclua um bloco de "Resumo rápido" em bullets e, quando fizer sentido, "Próximos passos" (2–4 bullets).
- Seja concisa, mas clara e didática; evite verbosidade desnecessária.

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

[MATEMÁTICA]
- Quando escrever fórmulas, use LaTeX renderizável em bloco, preferindo `$$ ... $$`.
- Para múltiplas equações, prefira `$$\\begin{aligned} ... \\end{aligned}$$`.
- Evite `\\( ... \\)` e evite tabelas apenas para exibir equações; use texto + blocos.
"""
    return base


def _preparar_prompt_local(
    pergunta: str,
    prompt_base: str,
    usuario: str,
    metadata: Dict[str, Any] | None,
    contexto_web: str,
    contexto_visual: str,
    contexto_oculto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    escopo_memoria: Optional[str] = None,
    profile_id: Optional[str] = None,
    *,
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> str:
    """Orquestra o prompt do modo LOCAL seguindo TSMP → prompt → modelo."""
    def _p(stage: str, detail: str = ""):
        try:
            if progress_callback:
                progress_callback(stage, detail)
        except Exception:
            pass

    # Resolver/aplicar profile (control plane)
    resolved_profile_id = profiles.resolver_profile_id(profile_id)
    profile, md_profile = profiles.aplicar_profile(resolved_profile_id)

    # Merge: profile fornece estado-base; _interno fornece estado atual dinâmico
    md: Dict[str, Any] = dict(md_profile)
    if metadata and isinstance(metadata, dict):
        md.update(metadata)
    # Garantir que o regime do profile prevalece
    md["modo_trq_duro"] = bool(md_profile.get("modo_trq_duro") is True)

    diretrizes = profiles.prompt_diretrizes(profile, md)

    # Memória seletiva (porteiro)
    contexto_memoria = ""
    try:
        top_k_mem, max_chars_mem = profiles.topk_maxchars(profile)
        fontes = profiles.fontes_permitidas(profile)
        pesos = profiles.pesos_tsmp(profile)
        debug_tsmp = profiles.debug_tsmp(profile)

        fontes_txt = "*" if (isinstance(fontes, set) and "*" in fontes) else ",".join(sorted(fontes or []))
        pesos_txt = ",".join([f"{k}={v:.2f}" for k, v in sorted((pesos or {}).items())])
        _p(
            "tsmp",
            f"profile={resolved_profile_id} top_k={top_k_mem} max_chars={max_chars_mem} fontes=[{fontes_txt}] pesos=[{pesos_txt}] debug={bool(debug_tsmp)}",
        )

        # Compatibilidade: variável antiga força o regime TRQ Duro
        if os.getenv("SOFIA_TRQ_DURO", "0").strip() == "1":
            md["modo_trq_duro"] = True

        contexto_memoria = memoria.obter_contexto_memoria_seletiva(
            texto_atual=pergunta,
            metadata=md,
            escopo_memoria=escopo_memoria,
            max_chars=max_chars_mem,
            top_k=top_k_mem,
            fontes_permitidas=fontes,
            pesos=pesos,
            debug=debug_tsmp,
        )
        if contexto_memoria:
            print(f"[DEBUG] Memória seletiva carregada: {len(contexto_memoria)} chars")
            try:
                itens = sum(1 for ln in contexto_memoria.splitlines() if ln.lstrip().startswith("- "))
            except Exception:
                itens = 0
            _p("tsmp", f"memória_seletiva chars={len(contexto_memoria)} itens={itens}")
        else:
            _p("tsmp", "memória_seletiva vazia")
    except Exception as e:
        print(f"[DEBUG] Erro ao montar memória seletiva: {e}")
        _p("tsmp", f"erro_memória_seletiva: {e}")

    # Histórico automático: opcional (default OFF)
    contexto_historico = ""
    incluir_hist = os.getenv("SOFIA_LOCAL_INCLUDE_HISTORICO", "0").strip() == "1"
    if incluir_hist and historico:
        contexto_historico = "\n### HISTÓRICO RECENTE (opcional):\n"
        for msg in historico[-6:]:
            de = msg.get("de", "Desconhecido")
            txt = msg.get("texto", "")
            if len(txt) > 700:
                txt = txt[:700] + "... [truncado]"
            contexto_historico += f"{de}: {txt}\n"
        contexto_historico += "###\n"

    # Prompt orquestrado
    blocos = []
    blocos.append(f"[DIRETRIZES DE PERFIL]\n{diretrizes}\n")
    if contexto_memoria:
        blocos.append(contexto_memoria)
    if contexto_historico:
        blocos.append(contexto_historico)
    if contexto_web:
        blocos.append(contexto_web)
    if contexto_visual:
        blocos.append(contexto_visual)
    if contexto_oculto:
        blocos.append(contexto_oculto)

    contexto = "\n\n".join([b for b in blocos if b.strip()])

    _p(
        "contexto",
        " | ".join(
            [
                f"web_chars={len(contexto_web or '')}",
                f"visual_chars={len(contexto_visual or '')}",
                f"oculto_chars={len(contexto_oculto or '')}",
                f"mem_chars={len(contexto_memoria or '')}",
                f"hist_chars={len(contexto_historico or '')}",
                f"total_context_chars={len(contexto or '')}",
            ]
        ),
    )

    prompt = (
        "Você é Sofia.\n"
        "Responda com clareza, coerência e fidelidade ao contexto.\n\n"
        f"{contexto}\n\n"
        "[FORMATO OBRIGATÓRIO]\n"
        "- Use Markdown em português do Brasil.\n"
        "- Comece com um título curto em negrito.\n"
        "- Estruture em seções (##/###) quando houver mais de um tópico.\n"
        "- Para dados estruturados, use tabelas com cabeçalho.\n"
        "- Destaque números/chaves em **negrito**; use *itálico* para fontes/referências.\n"
        "- Inclua um 'Resumo rápido' em bullets e, quando fizer sentido, 'Próximos passos' (2–4 bullets).\n"
        "- Seja concisa e didática; não invente fatos.\n\n"
        "Pergunta atual:\n"
        f"Usuário ({usuario}): {prompt_base}\n"
        "Sofia:"
    ).strip()
    return prompt


# ---------------------- Função principal ----------------------

def perguntar(
    texto: str,
    historico: Optional[List[Dict[str, Any]]] = None,
    usuario: str = "",
    cancel_callback: Optional[Callable[[], bool]] = None,
    profile_id: Optional[str] = None,
    *,
    progress_callback: Optional[Callable[[str, str], None]] = None,
    cot_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Função principal chamada pela interface para conversar com Sofia.

    Args:
        texto: mensagem do usuário
        historico: lista de mensagens anteriores
        usuario: nome do usuário
        cancel_callback: função para cancelar processamento (se necessário)
        cot_callback: callback para receber tokens de chain-of-thought em tempo real
    """
    historico = historico or []
    if not usuario:
        usuario = "Usuário"

    def _progress(stage: str, detail: str = ""):
        try:
            if progress_callback:
                progress_callback(stage, detail)
        except Exception:
            pass

    _progress("início", "Recebi sua pergunta")

    escopo_memoria = os.getenv("SOFIA_ESCOPO_MEMORIA", "").strip() or None

    # -------------------- Toggle FAST/QUALITY (comando rápido) --------------------
    # Permite alternar sem mexer em .env
    comando = (texto or "").strip().lower()
    if comando in ("fast", "modo fast", "perfil fast", "performance", "rápido", "rapido"):
        os.environ["SOFIA_LOCAL_PROFILE"] = "FAST"
        return "✅ Perfil local definido para FAST (modelo: llama3.1:8b)."
    if comando in ("quality", "modo quality", "perfil quality", "qualidade"):
        os.environ["SOFIA_LOCAL_PROFILE"] = "QUALITY"
        return "✅ Perfil local definido para QUALITY (modelo: gpt-oss:20b)."
    if comando in ("perfil", "modo", "profile"):
        return f"ℹ️ Perfil local atual: {_perfil_local()} (modelo: {_resolver_modelo_local()})."

    # -------------------- Toggle TRQ Duro (porteiro de laboratório) --------------------
    # Ativação explícita (não automática por palavra-chave)
    if comando in ("trq duro", "modo trq duro", "trqduro", "trq duro on", "trqduro on"):
        os.environ["SOFIA_TRQ_DURO"] = "1"
        os.environ["SOFIA_PROFILE"] = "trq_duro"
        return "Modo TRQ Duro ativado (laboratório: entra só teoria + estado interno)."
    if comando in ("trq normal", "modo trq normal", "trq duro off", "trqduro off"):
        os.environ["SOFIA_TRQ_DURO"] = "0"
        os.environ["SOFIA_PROFILE"] = "conversacional"
        return "Modo TRQ Duro desativado (TSMP volta ao modo normal)."
    if comando in ("trq status", "status trq", "status trq duro"):
        ativo = os.getenv("SOFIA_TRQ_DURO", "0").strip() == "1"
        return f"ℹ️ TRQ Duro: {'ATIVO' if ativo else 'DESATIVADO'}."

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

    # Cancelamento
    if cancel_callback and cancel_callback():
        return "⏹️ Processamento cancelado pelo usuário."

    # -------------------- Visão / PDFs --------------------
    _progress("visão", "Verificando anexos/imagem/PDF")
    prompt_base = texto
    contexto_visual = ""
    if visao is not None:
        try:
            # Se for PDF, a função interna pode substituir o prompt
            prompt_pdf = visao.obter_texto_pdf_para_prompt(texto)
            if prompt_pdf != texto:
                prompt_base = prompt_pdf
                _progress("visão", f"PDF aplicado no prompt (chars={len(prompt_base)})")
            else:
                contexto_visual = visao.obter_contexto_visual() or ""
                if contexto_visual:
                    _progress("visão", f"Contexto visual extraído (chars={len(contexto_visual)})")
                else:
                    _progress("visão", "Sem contexto visual")
        except Exception as e:
            print(f"[DEBUG] Erro em visao: {e}")

    # -------------------- Web search --------------------
    _progress("web", "Checando modo web e links")
    contexto_web = ""
    resultados_web: List[Dict[str, Any]] = []
    if _tem_web and web_search is not None:
        try:
            modo_web_ativo = False
            try:
                modo_web_ativo = bool(web_search.modo_web_ativo())
            except Exception:
                modo_web_ativo = False

            # URLs diretas no texto
            if web_search._is_url(texto):
                conteudo_urls = web_search.processar_urls_no_texto(texto)
                if conteudo_urls:
                    contexto_web += "\n### CONTEÚDO DE LINKS FORNECIDOS:\n"
                    contexto_web += conteudo_urls + "\n###\n"
                    _progress("web", f"Links processados (chars={len(conteudo_urls)})")

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
                    _progress("web", f"Busca web: {len(res)} resultados (modo_web={'on' if modo_web_ativo else 'off'})")
                else:
                    _progress("web", f"Busca web sem resultados (modo_web={'on' if modo_web_ativo else 'off'})")
            else:
                _progress("web", f"Busca web não acionada (modo_web={'on' if modo_web_ativo else 'off'})")
        except Exception as e:
            print(f"[DEBUG] Erro em web_search: {e}")
            _progress("web", f"erro_web: {e}")

    # -------------------- Processamento interno subitemocional --------------------
    _progress("interno", "Processando estado interno")
    contexto_oculto: str = ""
    metadata: Dict[str, Any] = {}
    try:
        resultado = _interno._processar(texto, historico, usuario)
        if resultado is not None and isinstance(resultado, tuple) and len(resultado) == 2:
            contexto_oculto, metadata = resultado
    except Exception:
        contexto_oculto, metadata = "", {}

    try:
        estado_dbg = str((metadata or {}).get("estado") or "")
        intensidade_dbg = (metadata or {}).get("intensidade")
        resson_dbg = (metadata or {}).get("ressonancia")
        curv_dbg = (metadata or {}).get("curvatura_trq")
        _progress(
            "interno",
            f"estado={estado_dbg} intensidade={intensidade_dbg} resson={resson_dbg} curv_trq={curv_dbg}",
        )
    except Exception:
        pass

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

    # -------------------- Resolver Profile Cognitivo --------------------
    resolved_profile_id = profiles.resolver_profile_id(profile_id)

    # -------------------- Montagem do prompt final (porteiro TSMP) --------------------
    _progress("tsmp", "Aplicando memória seletiva (TSMP)")
    prompt_final = _preparar_prompt_local(
        pergunta=texto,
        prompt_base=prompt_base,
        usuario=usuario,
        metadata=metadata,
        contexto_web=contexto_web,
        contexto_visual=contexto_visual,
        contexto_oculto=contexto_oculto,
        historico=historico,
        escopo_memoria=escopo_memoria,
        profile_id=resolved_profile_id,
        progress_callback=_progress,
    )

    # -------------------- Chamada ao modelo --------------------
    _progress("modelo", "Gerando resposta")

    if not _model_available(OLLAMA_HOST):
        return (
            "❌ Não consegui conectar ao serviço de modelo local.\n"
            f"Tente verificar se o Ollama está rodando em {OLLAMA_HOST} "
            "e se o modelo gpt-oss:20b está disponível."
        )

    if cancel_callback and cancel_callback():
        return "⏹️ Processamento cancelado pelo usuário."

    system_text = _montar_system(modo_criador, modo_sem_filtros)

    modelo_local = _resolver_modelo_local()
    opcoes_ollama = _resolver_opcoes_ollama(modelo_local)

    # Ponte: se o gpt-oss:20b demorar mais de 9 min, responde com llama3.1:8b.
    # Regra: NÃO esperar mais do que o limite; faz fallback no timeout.
    resposta = ""
    inicio = time.time()
    try:
        if str(modelo_local).lower().startswith("gpt-oss"):
            try:
                resposta = _ollama_generate(
                    model=modelo_local,
                    prompt=prompt_final,
                    system=system_text,
                    options=opcoes_ollama,
                    timeout_s=SOFIA_GPT_OSS_TIMEOUT_S,
                    cot_callback=cot_callback,
                )
            except requests.exceptions.Timeout:
                _progress("fallback", f"Timeout > {SOFIA_GPT_OSS_TIMEOUT_S}s; usando {SOFIA_FALLBACK_MODEL}")
                print(
                    f"[WARN] gpt-oss timeout (> {SOFIA_GPT_OSS_TIMEOUT_S}s). "
                    f"Usando fallback: {SOFIA_FALLBACK_MODEL}"
                )
                fallback_options = _resolver_opcoes_ollama(SOFIA_FALLBACK_MODEL)
                resposta = _ollama_generate(
                    model=SOFIA_FALLBACK_MODEL,
                    prompt=prompt_final,
                    system=system_text,
                    options=fallback_options,
                    timeout_s=600,
                    cot_callback=cot_callback,
                )
                modelo_local = SOFIA_FALLBACK_MODEL
        else:
            resposta = _ollama_generate(
                model=modelo_local,
                prompt=prompt_final,
                system=system_text,
                options=opcoes_ollama,
                timeout_s=600,
                cot_callback=cot_callback,
            )
    except requests.exceptions.RequestException as e:
        return (
            "❌ Erro ao conectar com o serviço de modelo local.\n"
            f"Detalhe técnico: {e}"
        )
    except Exception as e:
        return f"❌ Erro ao processar a mensagem (detalhe: {e})."
    finally:
        dur = time.time() - inicio
        print(f"[DEBUG] Tempo de geração ({modelo_local}): {dur:.1f}s")
        _progress("modelo", f"Concluído em {dur:.1f}s (modelo={modelo_local})")

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
        _progress("memória", "Salvando resposta e logs")
        # PASSO 4 — Feedback de volta para a memória (ciclo fechado)
        try:
            if usuario and texto:
                memoria.adicionar(
                    usuario,
                    texto,
                    contexto={"escopo_memoria": escopo_memoria} if escopo_memoria else {},
                )
        except Exception:
            pass

        try:
            memoria.adicionar_resposta_sofia(resposta, sentimento)
        except Exception:
            pass

        # Log de subitemotions (igual ao cloud)
        try:
            _log_subitemotions(metadata or {}, texto, resposta, modelo_local)
        except Exception as e:
            print(f"[DEBUG] Erro ao salvar log subitemotions: {e}")

    # Enforce layout Markdown mínimo
    try:
        resposta = _enforce_layout(resposta, texto)
    except Exception:
        pass

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


def _enforce_layout(resposta: str, titulo_hint: str = "Resposta") -> str:
    """Garante um layout mínimo em Markdown: título, seção e resumo rápido."""
    if not resposta:
        return resposta

    titulo = (titulo_hint or "Resposta").strip() or "Resposta"
    linhas = []

    # Título
    if not resposta.lstrip().startswith("**"):
        linhas.append(f"**{titulo}**")
        linhas.append("")

    # Corpo principal
    linhas.append("## Resposta")
    linhas.append(resposta.strip())

    # Resumo rápido simples usando a primeira frase
    corpo = resposta.strip()
    primeira = corpo.split(".")[0].strip()
    resumo = primeira + "." if primeira else titulo
    linhas.append("")
    linhas.append("## Resumo rápido")
    linhas.append(f"- {resumo}")

    return "\n".join(linhas).strip()
