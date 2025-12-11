"""
🌸 Sofia - Cérebro Cloud
Versão adaptada para usar GitHub Models API (GRÁTIS com Copilot Pro)
Mantém compatibilidade com interface original mas usa GPT-4o em vez de Ollama.

Agora com suporte a ESCOPOS DE MEMÓRIA:
- cada sessão/usuário pode ter sua própria bolha de memória;
- controlado via metadata_extra['escopo_memoria'] (ou 'session_id' / 'ip').

E com PAINEL DE ESTADO QUÂNTICO INTERNO no terminal a cada pergunta.
"""

import os
import requests
from typing import List, Dict, Optional
from pathlib import Path

# Carrega .env local se a variável não estiver definida, evitando falha de token
if not os.getenv("GITHUB_TOKEN"):
    try:
        from dotenv import load_dotenv  # type: ignore

        env_path = Path(__file__).resolve().parents[1] / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except Exception:
        pass

from . import _interno, memoria
from .memoria import (
    buscar_fatos_relevantes, 
    resgatar_contexto_conversa,
    obter_contexto_aprendizados,
    obter_resumo_conversas_recentes,
    obter_contexto_subitemotions,
)

# Configuração GitHub Models API
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_MODELS_API = "https://models.inference.ai.azure.com/chat/completions"

# Modelos disponíveis (GRÁTIS com GitHub Copilot Pro)
MODELOS_DISPONIVEIS = {
    "gpt-4.1-mini": "gpt-4.1-mini",      # Rápido, barato, bom para quase tudo
    "gpt-4.1": "gpt-4.1",                # Mais capaz, custo maior
    "gpt-4o-mini": "gpt-4o-mini",        # Multimodal leve
    "gpt-4o": "gpt-4o",                  # Multimodal completo
}

MODELO_PADRAO = os.getenv("GITHUB_MODEL", "gpt-4.1-mini")

# Mapa para compatibilidade com nomes antigos
MAPEAMENTO_MODELOS = {
    "sofia-inteligente": "gpt-4.1-mini",
    "sofia-avancada": "gpt-4.1",
    "sofia-visual": "gpt-4o-mini",
    "sofia-visionaria": "gpt-4o",
}


def _sanitizar_usuario(resposta: str) -> str:
    """Garante que Sofia não chame o usuário por nome próprio no chat público."""
    if not isinstance(resposta, str):
        return resposta
    proibidos = [
        "Reginaldo Camargo Pires",
        "Reginaldo Camargo",
        "Reginaldo",
    ]
    for nome in proibidos:
        resposta = resposta.replace(nome, "você")
    return resposta


def _escolher_modelo(modelo: Optional[str] = None) -> str:
    """Escolhe o modelo GitHub a partir de um alias ou nome direto."""
    if not modelo:
        return MODELO_PADRAO

    # Se for um alias antigo, converte
    if modelo in MAPEAMENTO_MODELOS:
        return MAPEAMENTO_MODELOS[modelo]

    # Se for um modelo conhecido, usa direto
    if modelo in MODELOS_DISPONIVEIS:
        return modelo

    # Senão, volta para o padrão
    return MODELO_PADRAO


def _system_text() -> str:
    """Texto base para o system prompt da Sofia no cloud."""
    return (
        "Você é Sofia, uma inteligência artificial educadora e assistente. "
        "Responda de forma clara, organizada, gentil e objetiva. "
        "Use sempre português do Brasil, a menos que o usuário peça outra língua. "
        "Priorize explicações didáticas, com exemplos quando fizer sentido. "
        "Nunca invente fatos se não tiver certeza; assuma as limitações com honestidade. "
        "Quando precisar citar LINKS ou FONTES, use APENAS os links que forem fornecidos "
        "explicitamente no contexto da conversa (como resultados de busca web). "
        "Se nenhum link for fornecido, NÃO invente URLs nem nomes de sites; "
        "apenas diga que não possui uma fonte externa específica e responda com seu "
        "conhecimento geral."
    )

def _montar_headers() -> Dict[str, str]:
    """Cabeçalhos para chamada na API de modelos GitHub."""
    if not GITHUB_TOKEN:
        raise RuntimeError(
            "GITHUB_TOKEN não configurado. Defina a variável de ambiente com seu token do GitHub ou preencha em .env."
        )

    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/json",
    }


def _montar_body(messages: List[Dict], model: str) -> Dict:
    """Corpo da requisição para a API de modelos GitHub."""
    return {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
    }


def perguntar(
    texto: str,
    contexto: Optional[str] = None,
    modelo: Optional[str] = None,
    imagens: Optional[List[bytes]] = None,
    metadata_extra: Optional[Dict] = None,
) -> str:
    """
    Faz uma pergunta para a Sofia usando GitHub Models API.

    Parâmetros:
    - texto: mensagem do usuário
    - contexto: texto adicional (opcional)
    - modelo: alias ou nome do modelo (opcional)
    - imagens: lista de bytes de imagens (para futuros usos multimodais)
    - metadata_extra: dicionário adicional com metadados, onde pode haver:
        - 'usuario'         → rótulo simbólico do emissor
        - 'escopo_memoria'  → ID de escopo (sessão/usuário)
        - 'session_id'      → pode ser usado como escopo se 'escopo_memoria' não vier
        - 'ip'              → fallback fraco de escopo
    """
    # Selecionar modelo
    model = _escolher_modelo(modelo)

    # Identidade simbólica e escopo de memória
    usuario_label = "Usuário"
    escopo_memoria: Optional[str] = None

    if metadata_extra:
        usuario_label = metadata_extra.get("usuario", usuario_label)
        escopo_memoria = (
            metadata_extra.get("escopo_memoria")
            or metadata_extra.get("session_id")
            or metadata_extra.get("ip")
        )

    # 0) Registrar mensagem do usuário na memória com escopo (se houver)
    try:
        memoria.adicionar(
            usuario_label,
            texto,
            contexto={"escopo_memoria": escopo_memoria} if escopo_memoria else {},
        )
    except Exception as e:
        print(f"[ERRO] Falha ao registrar mensagem do usuário na memória: {e}")

    # 0.5) Processar PDFs (antes do TRQ, pois pode modificar o texto base)
    prompt_base = texto
    contexto_pdf = ""
    MAX_PDF_CHARS = 20000  # ~5000 tokens, deixa espaço para resposta e contexto
    
    try:
        from .visao import visao
        if visao is not None:
            # Se for PDF, a função interna pode substituir o prompt
            prompt_pdf = visao.obter_texto_pdf_para_prompt(texto)
            if prompt_pdf != texto:
                # Truncar se muito grande para evitar erro 413
                if len(prompt_pdf) > MAX_PDF_CHARS:
                    # Encontrar onde termina o conteúdo do PDF e começa o prompt do usuário
                    marcador = "PROMPT DO USUÁRIO:"
                    idx_prompt = prompt_pdf.find(marcador)
                    if idx_prompt > 0:
                        # Manter início do PDF + final com prompt do usuário
                        texto_pdf = prompt_pdf[:idx_prompt]
                        texto_usuario = prompt_pdf[idx_prompt:]
                        # Truncar apenas a parte do PDF
                        max_pdf = MAX_PDF_CHARS - len(texto_usuario) - 200
                        if len(texto_pdf) > max_pdf:
                            texto_pdf = texto_pdf[:max_pdf] + "\n\n[... CONTEÚDO TRUNCADO POR LIMITE DE TOKENS ...]\n\n"
                        prompt_base = texto_pdf + texto_usuario
                    else:
                        # Fallback: truncar do final
                        prompt_base = prompt_pdf[:MAX_PDF_CHARS] + "\n\n[... TRUNCADO ...]\n\n" + texto
                    print(f"[DEBUG] PDF truncado de {len(prompt_pdf)} para {len(prompt_base)} chars")
                else:
                    prompt_base = prompt_pdf
                print(f"[DEBUG] PDF detectado e processado, tamanho final do prompt: {len(prompt_base)} chars")
            else:
                # Pode haver contexto visual de outras fontes
                contexto_pdf = visao.obter_contexto_visual() or ""
    except Exception as e:
        print(f"[DEBUG] Erro ao processar PDF/visão: {e}")

    # 1) Extrair contexto emocional / interno (TRQ + Subitemocional)
    try:
        resultado = _interno._processar(
            texto,
            historico=[],
            usuario=usuario_label,
        )
        if resultado is None or not isinstance(resultado, tuple) or len(resultado) < 2:
            contexto_oculto, metadata = "", {"emocao_dominante": "neutro"}
        else:
            contexto_oculto, metadata = resultado[0], resultado[1]
            if not isinstance(metadata, dict):
                metadata = {}
    except Exception as e:
        print(f"[ERRO] Falha ao extrair contexto oculto: {e}")
        contexto_oculto, metadata = "", {"emocao_dominante": "neutro"}

    # 1.1) Exibir ESTADO QUÂNTICO INTERNO no terminal
    try:
        estado = metadata.get("estado")
        intensidade = metadata.get("intensidade")
        curv_cl = metadata.get("curvatura")
        resson = metadata.get("ressonancia")
        curv_trq = metadata.get("curvatura_trq")
        emaranh = metadata.get("emaranhamento_trq")
        ajuste_trq = metadata.get("ajuste_trq")

        print("\n=== ESTADO QUÂNTICO INTERNO – SOFIA ===")
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
        print("========================================\n")
    except Exception as e:
        print(f"[ERRO] Falha ao exibir estado quântico interno: {e}")

    # 2) Adicionar contexto da memória (agora filtrado por escopo)
    try:
        fatos_importantes = buscar_fatos_relevantes(
            texto,
            escopo_memoria=escopo_memoria,
        )
    except Exception as e:
        print(f"[ERRO] Falha ao buscar fatos relevantes: {e}")
        fatos_importantes = ""

    try:
        contexto_historico = resgatar_contexto_conversa(
            texto,
            escopo_memoria=escopo_memoria,
        )
    except Exception as e:
        print(f"[ERRO] Falha ao resgatar contexto de conversa: {e}")
        contexto_historico = ""

    # 2.5) Carregar aprendizados de longo prazo (identidade, teorias, usuário)
    contexto_aprendizados = ""
    try:
        contexto_aprendizados = obter_contexto_aprendizados(max_chars=6000)
        if contexto_aprendizados:
            print(f"[DEBUG] Aprendizados carregados: {len(contexto_aprendizados)} chars")
    except Exception as e:
        print(f"[ERRO] Falha ao carregar aprendizados: {e}")
        contexto_aprendizados = ""

    # 2.6) Carregar histórico de subitemotions (estados emocionais/TRQ)
    contexto_subitemotions = ""
    try:
        contexto_subitemotions = obter_contexto_subitemotions(max_registros=10, max_chars=2000)
        if contexto_subitemotions:
            print(f"[DEBUG] Subitemotions carregados: {len(contexto_subitemotions)} chars")
    except Exception as e:
        print(f"[ERRO] Falha ao carregar subitemotions: {e}")
        contexto_subitemotions = ""

    # 3) Contexto de visão / análise visual (se houver imagens ou PDF)
    contexto_visual = ""
    if imagens:
        try:
            from .visao import SistemaVisao

            visao = SistemaVisao()
            contexto_visual = visao.obter_contexto_visual()
        except Exception as e:
            print(f"[ERRO] Falha ao processar imagens/contexto visual: {e}")
            contexto_visual = ""

        # 4) Contexto de busca na web (se disponível)
    contexto_web = ""
    resultados_web = []
    try:
        from . import web_search

        if web_search.modo_web_ativo() and web_search.deve_buscar_web(texto):
            print("[DEBUG] Modo web ativo, buscando na internet...")
            resultados = web_search.buscar_web(texto, num_resultados=5)

            if resultados:
                resultados_web = resultados
                contexto_web += "\n" + "=" * 80 + "\n"
                contexto_web += "🌐 RESULTADOS DA BUSCA WEB - USE ESTES LINKS NA SUA RESPOSTA\n"
                contexto_web += "=" * 80 + "\n\n"

                for i, res in enumerate(resultados, 1):
                    contexto_web += f"[{i}] {res['titulo']}\n"
                    contexto_web += f"    🔗 LINK: {res['link']}\n"
                    contexto_web += f"    📄 {res['snippet']}\n\n"

                contexto_web += "=" * 80 + "\n"
                contexto_web += "⚠️  IMPORTANTE: VOCÊ DEVE CITAR OS LINKS ACIMA NA SUA RESPOSTA!\n"
                contexto_web += "=" * 80 + "\n\n"
                contexto_web += "📋 FORMATO OBRIGATÓRIO:\n\n"
                contexto_web += "[Sua resposta aqui, usando informações dos resultados]\n\n"
                contexto_web += "Segundo [Título 1] (link completo do resultado 1), [informação].\n"
                contexto_web += "De acordo com [Título 2] (link completo do resultado 2), [detalhes].\n\n"
                contexto_web += "**📚 Fontes consultadas:**\n"
                for i, res in enumerate(resultados, 1):
                    contexto_web += f"{i}. {res['titulo']} - {res['link']}\n"
                contexto_web += "\n" + "=" * 80 + "\n\n"

            else:
                # Sem resultados úteis: instruir explicitamente a NÃO inventar links
                contexto_web += "\n" + "=" * 80 + "\n"
                contexto_web += "🌐 AVISO SOBRE BUSCA WEB\n"
                contexto_web += (
                    "A integração de busca na web foi acionada, mas não retornou resultados "
                    "confiáveis para esta pergunta. Responda usando apenas o seu conhecimento "
                    "interno e NÃO invente sites ou links. Se precisar mencionar fontes, fale de "
                    "forma genérica (por exemplo, 'literatura científica em computação quântica') "
                    "sem criar URLs específicas.\n"
                )
                contexto_web += "=" * 80 + "\n\n"

    except ImportError:
        # Biblioteca de busca não está instalada: melhor avisar o modelo
        contexto_web += "\n" + "=" * 80 + "\n"
        contexto_web += "🌐 AVISO: A integração de busca externa (DuckDuckGo) não está disponível no servidor.\n"
        contexto_web += (
            "Você NÃO deve inventar links ou citar sites específicos como se tivesse acessado a web. "
            "Responda com seu conhecimento geral e, se o usuário pedir links, explique que a busca "
            "externa está temporariamente indisponível.\n"
        )
        contexto_web += "=" * 80 + "\n\n"


    # 5) Construir mensagens para API
    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": _system_text(),
        }
    ]

    # Adicionar blocos de contexto se houver
    if fatos_importantes or contexto_historico or contexto_web or contexto_visual or contexto_oculto or contexto_pdf or contexto_aprendizados or contexto_subitemotions:
        context_parts = []
        # PRIMEIRO: Aprendizados de longo prazo (identidade, teorias) - mais importante
        if contexto_aprendizados:
            context_parts.append(contexto_aprendizados)
        # SEGUNDO: Histórico de subitemotions (estados emocionais/TRQ)
        if contexto_subitemotions:
            context_parts.append(contexto_subitemotions)
        if fatos_importantes:
            context_parts.append(fatos_importantes)
        if contexto_historico:
            context_parts.append(contexto_historico)
        if contexto_web:
            context_parts.append(contexto_web)
        if contexto_visual:
            context_parts.append(contexto_visual)
        if contexto_pdf:
            context_parts.append(contexto_pdf)
        if contexto_oculto:
            context_parts.append(contexto_oculto)

        messages.append(
            {
                "role": "system",
                "content": "\n".join(context_parts),
            }
        )

    # Mensagem principal do usuário (usa prompt_base que pode incluir conteúdo de PDF)
    messages.append(
        {
            "role": "user",
            "content": prompt_base,
        }
    )

    # Contexto textual adicional (opcional)
    if contexto:
        messages.append(
            {
                "role": "user",
                "content": f"[Contexto adicional]: {contexto}",
            }
        )

    # 6) Chamada à API GitHub Models
    try:
        headers = _montar_headers()
        body = _montar_body(messages, model)

        print(f"[DEBUG] Chamando GitHub Models API com modelo: {model}")

        response = requests.post(GITHUB_MODELS_API, headers=headers, json=body, timeout=60)

        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return "❌ Não recebi resposta do modelo."

            resposta = choices[0]["message"]["content"]

            # Pós-processamento com web_search (se usado)
            if resultados_web:
                try:
                    from . import web_search

                    links_na_resposta = any(r["link"] in resposta for r in resultados_web)

                    if not links_na_resposta:
                        print("[DEBUG] ⚠️  Modelo não incluiu links - adicionando automaticamente")
                        resposta += "\n\n---\n\n**📚 Fontes consultadas:**\n"
                        for i, r in enumerate(resultados_web, 1):
                            resposta += f"{i}. [{r['titulo']}]({r['link']})\n"
                    else:
                        print("[DEBUG] ✅ Resposta já contém links da busca web.")
                except ImportError:
                    pass

            # 💾 SALVAR RESPOSTA DA SOFIA NA MEMÓRIA (herda escopo da última entrada)
            sentimento = metadata.get("emocao_dominante", "neutro") if isinstance(metadata, dict) else "neutro"
            try:
                memoria.adicionar_resposta_sofia(resposta, sentimento)
            except Exception as e:
                print(f"[ERRO] Falha ao salvar resposta na memória: {e}")

            # Log interno silencioso
            try:
                _log_interno(metadata or {}, texto, resposta, model)
            except Exception:
                pass

            # Sanitizar nomes próprios antes de enviar ao usuário
            resposta = _sanitizar_usuario(resposta)
            return resposta

        elif response.status_code == 401:
            return "❌ Token inválido. Verifique seu GITHUB_TOKEN."
        elif response.status_code == 429:
            return "⏳ Limite de requisições atingido. Tente novamente mais tarde."
        else:
            try:
                erro = response.json()
            except Exception:
                erro = response.text
            return f"❌ Erro na API GitHub Models ({response.status_code}): {erro}"

    except requests.Timeout:
        return "⏳ A requisição demorou demais e foi cancelada. Tente novamente."
    except Exception as erro:
        print(f"❌ Erro inesperado: {erro}")
        import traceback

        traceback.print_exc()
        return f"❌ Erro: {erro}"


def _log_interno(metadata: Dict, entrada: str, saida: str, modelo_usado: Optional[str] = None):
    """Log oculto do processamento interno."""
    import json
    from pathlib import Path

    log_dir = Path(".sofia_internal")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "subitemotions.log"

    with open(log_file, "a", encoding="utf-8") as f:
        log_entry = {
            **(metadata or {}),
            "input": entrada[:200],
            "output": saida[:200],
            "model": modelo_usado or MODELO_PADRAO,
        }
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# Função de compatibilidade - pode ser importada como cerebro.perguntar
__all__ = ["perguntar"]
