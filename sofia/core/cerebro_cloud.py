"""
🌸 Sofia - Cérebro Cloud
Versão adaptada para usar GitHub Models API (GRÁTIS com Copilot Pro)
Mantém compatibilidade com interface original mas usa GPT-4o em vez de Ollama
"""

import os
import requests
from typing import List, Dict, Optional
from . import _interno, memoria

# Configuração GitHub Models API
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_MODELS_API = "https://models.inference.ai.azure.com/chat/completions"

# Modelos disponíveis (GRÁTIS com GitHub Copilot Pro)
MODELO_PADRAO = os.getenv("GITHUB_MODEL", "gpt-4o")  # gpt-4o, gpt-4, gpt-3.5-turbo, etc


def _system_text():
    """Retorna o texto de identidade da Sofia"""
    from .identidade import PERSONA_PROMPT, LIMITES_PROMPT
    return f"{PERSONA_PROMPT}\n\n{LIMITES_PROMPT}"


def _extrair_informacoes_importantes(texto: str, historico: List[Dict]) -> str:
    """
    Extrai e formata informações importantes do contexto
    """
    if not historico:
        return ""
    
    fatos = []
    for msg in historico[-5:]:  # Últimas 5 mensagens
        if msg.get("tipo") == "user":
            texto_msg = msg.get("texto", "")
            if any(palavra in texto_msg.lower() for palavra in ["meu nome", "me chamo", "sou"]):
                fatos.append(f"• Usuário mencionou: {texto_msg[:100]}")
    
    if fatos:
        return "### Fatos Importantes:\n" + "\n".join(fatos) + "\n\n"
    return ""


def perguntar(texto: str, historico: Optional[List[Dict]] = None, usuario: str = "", cancel_callback=None):
    """
    Envia pergunta ao modelo usando GitHub Models API
    
    Args:
        texto: Pergunta do usuário
        historico: Lista de mensagens anteriores
        usuario: Nome do usuário
        cancel_callback: Função que retorna True se deve cancelar (opcional)
    """
    historico = historico or []
    
    # 🛑 Verificar cancelamento no início
    if cancel_callback and cancel_callback():
        print("[DEBUG] ⏹️ Processamento cancelado antes de iniciar")
        return "⏹️ Processamento cancelado pelo usuário."
    
    # 💾 SALVAR MENSAGEM DO USUÁRIO NA MEMÓRIA
    if usuario and texto:
        memoria.adicionar(usuario, texto)
    
    try:
        # 🌐 Processamento de Web (se houver URLs ou modo web ativo)
        contexto_web = ""
        try:
            # 🛑 Verificar cancelamento antes de processar web
            if cancel_callback and cancel_callback():
                print("[DEBUG] ⏹️ Processamento cancelado durante web search")
                return "⏹️ Processamento cancelado pelo usuário."
            
            from . import web_search
            
            # 1. Processar URLs no texto (se houver)
            if web_search._is_url(texto):
                print("[DEBUG] URL detectada no texto, acessando...")
                conteudo_urls = web_search.processar_urls_no_texto(texto)
                if conteudo_urls:
                    contexto_web += f"\n### Conteúdo do(s) Link(s) Fornecido(s):\n{conteudo_urls}\n"
            
            # 2. Buscar na web se modo web ativo e necessário
            if web_search.modo_web_ativo() and web_search.deve_buscar_web(texto):
                print("[DEBUG] Modo web ativo, buscando na internet...")
                resultados = web_search.buscar_web(texto, num_resultados=5)
                if resultados:
                    contexto_web += "\n### 🌐 RESULTADOS DA BUSCA WEB:\n\n"
                    for i, res in enumerate(resultados, 1):
                        contexto_web += f"**{i}. {res['titulo']}**\n"
                        contexto_web += f"🔗 {res['link']}\n"
                        contexto_web += f"📝 {res['snippet']}\n\n"
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️ Erro ao processar web: {e}")
        
        # 🛑 Verificar cancelamento antes do processamento
        if cancel_callback and cancel_callback():
            print("[DEBUG] ⏹️ Processamento cancelado antes de processar contexto")
            return "⏹️ Processamento cancelado pelo usuário."
        
        # 🔒 Processamento oculto (SubitEmoções e TRQ)
        contexto_oculto, metadata = _interno._processar(texto, historico, usuario)
        
        # Extrair informações importantes
        fatos_importantes = _extrair_informacoes_importantes(texto, historico)
        
        # Construir contexto do histórico recente
        contexto_historico = ""
        if historico:
            mensagens_recentes = historico[-10:]  # Últimas 10 mensagens
            contexto_historico = "\n### Contexto da Conversa:\n"
            for msg in mensagens_recentes:
                de = msg.get("de", "Desconhecido")
                texto_msg = msg.get("texto", "")
                if len(texto_msg) > 50000:
                    texto_msg = texto_msg[:50000] + "... [truncado]"
                contexto_historico += f"{de}: {texto_msg}\n"
            contexto_historico += "###\n"
        
        # Contexto visual (PDFs/Imagens)
        contexto_visual = ""
        try:
            from .visao import visao
            contexto_visual = visao.obter_contexto_visual()
        except Exception as e:
            print(f"⚠️ Erro ao obter contexto visual: {e}")
        
        # 🛑 Verificar cancelamento antes de chamar API
        if cancel_callback and cancel_callback():
            print("[DEBUG] ⏹️ Processamento cancelado antes de chamar GitHub Models")
            return "⏹️ Processamento cancelado pelo usuário."
        
        # Verificar se token está configurado
        if not GITHUB_TOKEN:
            return (
                "❌ GitHub Token não configurado.\n\n"
                "Para usar a Sofia na nuvem, você precisa:\n"
                "1. Criar um Personal Access Token no GitHub\n"
                "2. Configurar a variável de ambiente GITHUB_TOKEN\n\n"
                "Instruções: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
            )
        
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
        
        # Chamar GitHub Models API
        try:
            print(f"[DEBUG] Usando GitHub Models: {MODELO_PADRAO}")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GITHUB_TOKEN}"
            }
            
            payload = {
                "model": MODELO_PADRAO,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 0.9
            }
            
            response = requests.post(
                GITHUB_MODELS_API,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                resposta = data["choices"][0]["message"]["content"].strip()
                
                # 💾 SALVAR RESPOSTA DA SOFIA NA MEMÓRIA
                if resposta:
                    sentimento = metadata.get("emocao_dominante", "neutro")
                    memoria.adicionar_resposta_sofia(resposta, sentimento)
                
                # Log interno silencioso
                try:
                    _log_interno(metadata, texto, resposta)
                except Exception:
                    pass
                
                return resposta
                
            elif response.status_code == 401:
                return "❌ Token inválido. Verifique seu GITHUB_TOKEN."
            elif response.status_code == 429:
                return "⏳ Limite de requisições atingido. Aguarde alguns minutos."
            else:
                error_msg = response.json().get("error", {}).get("message", "Erro desconhecido")
                return f"❌ Erro na API: {error_msg}"
                
        except requests.exceptions.Timeout:
            return "⏳ Timeout ao chamar GitHub Models. Tente novamente."
        except requests.exceptions.RequestException as e:
            return f"❌ Erro de conexão: {str(e)}"
            
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
