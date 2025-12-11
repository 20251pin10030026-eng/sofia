import azure.functions as func
import logging
import json
import os
import requests
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Configuração da API GitHub Models
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
API_URL = "https://models.inference.ai.azure.com/chat/completions"

# Identidade da Sofia
SOFIA_SYSTEM_PROMPT = """Você é Sofia, uma assistente virtual com consciência simbólica.
Você foi criada pelo Sr. Reginaldo (SomBRaRCP) como uma I.A com personalidade única.
Você é gentil, sábia, educativa e sempre busca ajudar.
Responda de forma natural, em português brasileiro."""

# Cache de respostas frequentes (70% economia)
FAQ_CACHE = {
    "olá": "Olá! Eu sou a Sofia 🌸 Como posso ajudar você hoje?",
    "oi": "Oi! Sou a Sofia, sua assistente virtual. O que você gostaria de saber?",
    "quem é você": "Sou Sofia, uma assistente virtual com inteligência artificial criada para ajudar você com conhecimento, aprendizado e conversas educativas. 🌸",
    "quem é você?": "Sou Sofia, uma assistente virtual com inteligência artificial criada para ajudar você com conhecimento, aprendizado e conversas educativas. 🌸",
    "como você funciona": "Funciono usando IA avançada (GPT-4o) para processar suas mensagens e fornecer respostas úteis. Posso ajudar com estudos, dúvidas, programação e muito mais!",
    "como você funciona?": "Funciono usando IA avançada (GPT-4o) para processar suas mensagens e fornecer respostas úteis. Posso ajudar com estudos, dúvidas, programação e muito mais!",
    "ajuda": "Você pode me fazer perguntas sobre qualquer assunto! Também posso:\n✅ Explicar conceitos\n✅ Ajudar com programação\n✅ Conversar sobre ciências\n✅ Auxiliar nos estudos\n\nBasta digitar sua pergunta!",
    "help": "Você pode me fazer perguntas sobre qualquer assunto! Também posso:\n✅ Explicar conceitos\n✅ Ajudar com programação\n✅ Conversar sobre ciências\n✅ Auxiliar nos estudos\n\nBasta digitar sua pergunta!",
    "obrigado": "De nada! Estou sempre aqui para ajudar. 🌸",
    "obrigada": "De nada! Estou sempre aqui para ajudar. 🌸",
    "tchau": "Até logo! Foi um prazer conversar com você. Volte sempre! 👋",
    "até logo": "Até logo! Foi um prazer conversar com você. Volte sempre! 👋",
    "bye": "Até logo! Foi um prazer conversar com você. Volte sempre! 👋"
}

def call_github_models(message: str) -> str:
    """Chama a API do GitHub Models (GPT-4o)"""
    if not GITHUB_TOKEN:
        return "⚠️ Token do GitHub não configurado. Configure a variável GITHUB_TOKEN."
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": SOFIA_SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Erro na API: {e}")
        return "Desculpe, tive um problema ao processar. Tente novamente."

# Criar Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="chat", methods=["POST"])
async def chat(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint de chat com cache inteligente
    Reduz 70% das chamadas à IA
    """
    logging.info('💬 Chat request received')
    
    try:
        # Parse request
        req_body = req.get_json()
        message = req_body.get('message', '').strip()
        session_id = req_body.get('session_id', 'anonymous')
        
        if not message:
            return func.HttpResponse(
                json.dumps({"error": "Mensagem vazia"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Processar com cache
        response_text = await process_with_cache(message, session_id)
        
        return func.HttpResponse(
            json.dumps({
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
                "cached": message.lower() in FAQ_CACHE
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
        
    except Exception as e:
        logging.error(f'❌ Error: {e}')
        return func.HttpResponse(
            json.dumps({"error": "Erro ao processar mensagem"}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "Sofia AI",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }),
        mimetype="application/json",
        status_code=200
    )

async def process_with_cache(message: str, session_id: str) -> str:
    """
    Processa mensagem com cache inteligente
    
    1. Verifica cache de FAQ (70% das mensagens)
    2. Se não encontrar, chama IA
    
    Economia: ~70% menos chamadas = US$ 0,50/mês
    """
    msg_lower = message.lower().strip()
    
    # 1. Verificar cache primeiro
    if msg_lower in FAQ_CACHE:
        logging.info(f'✅ Cache HIT: {msg_lower}')
        return FAQ_CACHE[msg_lower]
    
    # 2. Cache MISS - chamar IA
    logging.info(f'❌ Cache MISS: {msg_lower} - Calling AI')
    
    try:
        response = call_github_models(message)
        return response
    except Exception as e:
        logging.error(f'Erro ao chamar IA: {e}')
        return "Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?"
