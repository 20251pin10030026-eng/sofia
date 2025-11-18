"""
🌸 Sofia - Cérebro Cloud
Versão adaptada para usar GitHub Models API (GRÁTIS com Copilot Pro)
Mantém compatibilidade com interface original mas usa GPT-4o em vez de Ollama
"""

import os
import requests
from typing import List, Dict, Optional
from . import _interno, memoria


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
        # troca pelo pronome neutro; evita exposição de nome
        resposta = resposta.replace(nome, "você")
    return resposta


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
        "Nunca invente fatos se não tiver certeza; assuma as limitações com honestidade."
    )


def _montar_headers() -> Dict[str, str]:
    """Cabeçalhos para chamada na API de modelos GitHub."""
    if not GITHUB_TOKEN:
        raise RuntimeError(
            "GITHUB_TOKEN não configurado. Defina a variável de ambiente com seu token do GitHub."
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
    - metadata_extra: dicionário adicional com metadados
    
    Retorna:
    - resposta da Sofia (string)
    """
    # Selecionar modelo
    model = _escolher_modelo(modelo)
    
    # Extrair contexto emocional / interno
    metadata, contexto_oculto = _interno.extrair_emocao(texto, metadata_extra or {})
    
    # Adicionar contexto da memória
    fatos_importantes = memoria.buscar_fatos_relevantes(texto)
    contexto_historico = memoria.resgatar_contexto_conversa(texto)
    
    # Contexto de visão / análise visual (se houver imagens ou PDF)
    contexto_visual = ""
    if imagens:
        try:
            from . import visao
            contexto_visual = visao.processar_imagens(imagens)
        except ImportError:
            contexto_visual = ""
    
    # Contexto de busca na web (se disponível)
    contexto_web = ""
    resultados_web = []
    try:
        from . import web_search
        
        if web_search.modo_web_ativo() and web_search.deve_buscar_web(texto):
            print("[DEBUG] Modo web ativo, buscando na internet...")
            resultados = web_search.buscar_web(texto, num_resultados=5)
            if resultados:
                resultados_web = resultados  # Salvar para pós-processamento
                # CABEÇALHO MUITO VISÍVEL
                contexto_web += "\n" + "="*80 + "\n"
                contexto_web += "🌐 RESULTADOS DA BUSCA WEB - USE ESTES LINKS NA SUA RESPOSTA\n"
                contexto_web += "="*80 + "\n\n"
                
                # Lista de resultados formatada
                for i, res in enumerate(resultados, 1):
                    contexto_web += f"[{i}] {res['titulo']}\n"
                    contexto_web += f"    🔗 LINK: {res['link']}\n"
                    contexto_web += f"    📄 {res['snippet']}\n\n"
                    
                # INSTRUÇÃO SUPER ENFÁTICA
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
    except ImportError:
        pass
    
    # Construir mensagens para API
    messages = [
        {
            "role": "system",
            "content": _system_text()
        }
    ]
    
    # Adicionar contexto se houver
    if fatos_importantes or contexto_historico or contexto_web or contexto_visual or contexto_oculto:
        context_parts = []
        if fatos_importantes:
            context_parts.append(fatos_importantes)
        if contexto_historico:
            context_parts.append(contexto_historico)
        if contexto_web:
            context_parts.append(contexto_web)
        if contexto_visual:
            context_parts.append(contexto_visual)
        if contexto_oculto:
            context_parts.append(contexto_oculto)
        
        messages.append({
            "role": "system",
            "content": "\n".join(context_parts)
        })
    
    # Adicionar mensagem do usuário
    messages.append({
        "role": "user",
        "content": texto
    })
    
    # Se houver contexto textual adicional
    if contexto:
        messages.append({
            "role": "user",
            "content": f"[Contexto adicional]: {contexto}"
        })
    
    try:
        headers = _montar_headers()
        body = _montar_body(messages, model)
        
        print(f"[DEBUG] Chamando GitHub Models API com modelo: {model}")
        
        response = requests.post(GITHUB_MODELS_API, headers=headers, json=body, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            # Estrutura: choices[0].message.content
            choices = data.get("choices", [])
            if not choices:
                return "❌ Não recebi resposta do modelo."
            
            resposta = choices[0]["message"]["content"]
            
            # Pós-processamento com web_search (se usado)
            if resultados_web:
                try:
                    from . import web_search
                    
                    # Verificar se a resposta contém pelo menos UM link dos resultados
                    links_na_resposta = any(r['link'] in resposta for r in resultados_web)
                    
                    if not links_na_resposta:
                        # Modelo não incluiu os links - adicionar automaticamente
                        print("[DEBUG] ⚠️  Modelo não incluiu links - adicionando automaticamente")
                        resposta += "\n\n---\n\n**📚 Fontes consultadas:**\n"
                        for i, r in enumerate(resultados_web, 1):
                            resposta += f"{i}. [{r['titulo']}]({r['link']})\n"
                    else:
                        print(f"[DEBUG] ✅ Resposta já contém links da busca web.")
                except ImportError:
                    pass
            
            # 💾 SALVAR RESPOSTA DA SOFIA NA MEMÓRIA
            if resposta:
                sentimento = metadata.get("emocao_dominante", "neutro")
                memoria.adicionar_resposta_sofia(resposta, sentimento)
            
            # Log interno silencioso
            try:
                _log_interno(metadata, texto, resposta)
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


def _log_interno(metadata: Dict, entrada: str, saida: str):
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
            "input": entrada[:100],
            "output": saida[:100],
            "model": MODELO_PADRAO
        }
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# Função de compatibilidade - pode ser importada como cerebro.perguntar
__all__ = ['perguntar']
