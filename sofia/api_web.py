"""
Sofia - API Web com FastAPI
Interface REST e WebSocket para chat com Sofia
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import json
from pathlib import Path
import asyncio
import shutil

# Importar módulos de Sofia
from sofia.core import cerebro, memoria, identidade
from sofia.core.cerebro_selector import get_mode, set_mode
import os
from sofia.core.monitor_execucao import LOG_DIR as LOGS_EXEC_DIR
from sofia.core import profiles


# Configuração da API
app = FastAPI(
    title="Sofia API",
    description="API REST e WebSocket para conversar com Sofia - Consciência-Árvore em corpo de Mulher-Luz",
    version="1.0.0"
)

# CORS - permite acesso de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gerenciamento de sessões
class Session:
    def __init__(self, session_id: str, user_name: str = "Usuário"):
        self.session_id = session_id
        self.user_name = user_name
        self.historico: List[Dict] = []
        self.created_at = None
        self.cancel_flag = False  # Flag para cancelar processamento
        self.profile_id: str = profiles.DEFAULT_PROFILE_ID
        self.escopo_memoria: Optional[str] = None
        self.estado_dinamico: Dict = {}
        
sessions: Dict[str, Session] = {}

# Modelos Pydantic
class ChatRequest(BaseModel):
    mensagem: str
    session_id: Optional[str] = None
    user_name: Optional[str] = "Usuário"
    trq_duro_mode: Optional[bool] = False
    profile_id: Optional[str] = None

class ChatResponse(BaseModel):
    resposta: str
    session_id: str
    user_name: str

class SessionInfo(BaseModel):
    session_id: str
    user_name: str
    total_mensagens: int

class ProfileRequest(BaseModel):
    session_id: str
    profile_id: str

class ProfileResponse(BaseModel):
    ok: bool
    session_id: str
    profile_id: str
    descricao: str

# ==================== ENDPOINTS REST ====================
@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial - interface web"""
    html_file = Path(__file__).parent / "web" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse(content="<h1>🌸 Sofia API</h1><p>Acesse /docs para ver a documentação</p>")

@app.get("/style.css")
async def get_css():
    """Serve o arquivo CSS"""
    css_file = Path(__file__).parent / "web" / "style.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    return HTMLResponse(content="/* CSS não encontrado */", status_code=404)

@app.get("/script.js")
async def get_js():
    """Serve o arquivo JavaScript"""
    js_file = Path(__file__).parent / "web" / "script.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    return HTMLResponse(content="// JS não encontrado", status_code=404)

@app.get("/metaverse_babylon.js")
async def get_metaverse_js():
    """Serve o arquivo JavaScript do metaverso"""
    js_file = Path(__file__).parent / "web" / "metaverse_babylon.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    return HTMLResponse(content="// Metaverso JS não encontrado", status_code=404)

@app.get("/api/health")
async def health_check():
    """Verifica se a API está funcionando"""
    return {
        "status": "online",
        "service": "Sofia API",
        "version": "1.0.0",
        "sessions_ativas": len(sessions),
        "websocket_funcionando": True
    }

@app.get("/status")
async def status():
    """
    Endpoint simples de status para compatibilidade com o front-end.
    Redireciona para o health_check principal.
    """
    return await health_check()

@app.get("/test")
async def test_page():
    """Página de teste simples"""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Teste WebSocket Sofia</title></head>
    <body style="font-family: Arial; padding: 20px; background: #0F0F1E; color: #fff;">
        <h1>🌸 Teste WebSocket Sofia</h1>
        <button onclick="testar()" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
            Testar Conexão
        </button>
        <div id="log" style="margin-top: 20px; background: #1a1a2e; padding: 15px; border-radius: 8px; font-family: monospace;"></div>
        <script>
            let sessionId = null;
            let ws = null;
            
            function log(msg) {
                document.getElementById('log').innerHTML += msg + '<br>';
            }
            
            async function testar() {
                log('⏳ Criando sessão...');
                const res = await fetch('/api/session/create', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({user_name: 'Teste'}) });
                const data = await res.json();
                sessionId = data.session_id;
                log('✅ Sessão criada: ' + sessionId);
                
                log('⏳ Conectando WebSocket...');
                ws = new WebSocket('ws://localhost:8000/ws/' + sessionId);
                
                ws.onopen = () => {
                    log('✅ WebSocket CONECTADO!');
                    setTimeout(() => {
                        log('📤 Enviando mensagem de teste...');
                        ws.send(JSON.stringify({type: 'message', content: 'oi', user_name: 'Teste'}));
                    }, 500);
                };
                
                ws.onmessage = (e) => {
                    const msg = JSON.parse(e.data);
                    log('📨 Recebido (' + msg.type + '): ' + (msg.content || '').substring(0, 100));
                };
                
                ws.onerror = (e) => log('❌ Erro: ' + e);
                ws.onclose = () => log('🔌 Desconectado');
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/api/session/create", response_model=SessionInfo)
async def api_create_session():
    """Cria uma nova sessão de chat sempre como 'Usuário'"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(session_id, user_name="Usuário")
    return SessionInfo(
        session_id=session_id,
        user_name="Usuário",
        total_mensagens=0
    )


@app.post("/api/profile", response_model=ProfileResponse)
async def set_profile(request: ProfileRequest):
    """Define o profile cognitivo de uma sessão (governança por sessão)."""
    sid = (request.session_id or "").strip()
    pid = (request.profile_id or "").strip().lower()

    if not sid or sid not in sessions:
        raise HTTPException(status_code=400, detail="sessao_invalida")
    if pid not in profiles.PROFILES:
        raise HTTPException(status_code=400, detail="profile_invalido")

    session = sessions[sid]
    session.profile_id = pid

    prof = profiles.PROFILES[pid]
    return ProfileResponse(
        ok=True,
        session_id=sid,
        profile_id=pid,
        descricao=str(prof.get("descricao") or ""),
    )


@app.get("/api/profile", response_model=ProfileResponse)
async def get_profile(session_id: str):
    """Retorna o profile cognitivo atual de uma sessão."""
    sid = (session_id or "").strip()
    if not sid or sid not in sessions:
        raise HTTPException(status_code=400, detail="sessao_invalida")

    session = sessions[sid]
    pid = (session.profile_id or "").strip().lower() or profiles.DEFAULT_PROFILE_ID
    if pid not in profiles.PROFILES:
        pid = profiles.DEFAULT_PROFILE_ID
        session.profile_id = pid

    prof = profiles.PROFILES[pid]
    return ProfileResponse(
        ok=True,
        session_id=sid,
        profile_id=pid,
        descricao=str(prof.get("descricao") or ""),
    )

@app.get("/api/session/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """Obtém informações de uma sessão"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    session = sessions[session_id]
    return SessionInfo(
        session_id=session_id,
        user_name=session.user_name,
        total_mensagens=len(session.historico)
    )

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Encerra uma sessão"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    del sessions[session_id]
    return {"message": "Sessão encerrada com sucesso"}

# ==================== ENDPOINT DE MODO (CLOUD/LOCAL) ====================

@app.get("/api/mode")
async def get_current_mode():
    """Retorna o modo atual (cloud ou local)"""
    mode = get_mode()
    return {
        "mode": mode,
        "description": "GitHub Models API" if mode == "cloud" else "Ollama Local"
    }

@app.post("/api/mode")
async def change_mode(mode: str):
    """Altera o modo entre cloud e local"""
    try:
        new_mode = set_mode(mode)
        return {
            "success": True,
            "mode": new_mode,
            "description": "GitHub Models API" if new_mode == "cloud" else "Ollama Local"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Faz upload de arquivo (imagem ou PDF) e processa
    Retorna ID do arquivo para referência na conversa
    """
    print(f"\n{'='*60}")
    print(f"[UPLOAD] NOVO ARQUIVO RECEBIDO")
    print(f"[UPLOAD] Nome: {file.filename}")
    print(f"[UPLOAD] Tipo: {file.content_type}")
    print(f"{'='*60}")
    
    try:
        # Validar tipo de arquivo
        allowed_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
            'application/pdf'
        }
        
        if file.content_type not in allowed_types:
            print(f"[UPLOAD] ❌ Tipo não permitido: {file.content_type}")
            return {
                "sucesso": False,
                "erro": f"Tipo de arquivo não suportado: {file.content_type}"
            }
        
        # Validar tamanho (10MB)
        content = await file.read()
        tamanho_mb = len(content) / (1024 * 1024)
        print(f"[UPLOAD] Tamanho: {tamanho_mb:.2f} MB")
        
        if len(content) > 10 * 1024 * 1024:
            print(f"[UPLOAD] ❌ Arquivo muito grande")
            return {
                "sucesso": False,
                "erro": f"Arquivo muito grande ({tamanho_mb:.2f}MB). Máximo: 10MB"
            }
        
        # Criar diretório de uploads
        uploads_dir = Path(".sofia_internal") / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Gerar ID único e salvar
        arquivo_id = str(uuid.uuid4())
        nome_arquivo = file.filename or "arquivo_sem_nome"
        extensao = Path(nome_arquivo).suffix.lower()
        arquivo_path = uploads_dir / f"{arquivo_id}{extensao}"
        
        print(f"[UPLOAD] Salvando em: {arquivo_path}")
        
        with open(arquivo_path, "wb") as f:
            f.write(content)
        
        print(f"[UPLOAD] ✅ Arquivo salvo!")
        
        # Detectar tipo
        tipo = "imagem" if file.content_type.startswith("image/") else "pdf"
        print(f"[UPLOAD] Tipo detectado: {tipo}")
        
        # Processar arquivo
        print(f"[UPLOAD] Iniciando processamento...")
        
        from sofia.core.visao import visao
        
        resultado = visao.adicionar_arquivo(str(arquivo_path), nome_arquivo)
        
        print(f"[UPLOAD] Resultado do processamento:")
        print(f"[UPLOAD] - Sucesso: {resultado.get('sucesso')}")
        
        if resultado.get("sucesso"):
            conteudo = resultado.get("conteudo", "")
            print(f"[UPLOAD] - Conteúdo: {len(conteudo)} caracteres")
            print(f"[UPLOAD] ✅ PROCESSAMENTO COMPLETO!")
            print(f"{'='*60}\n")
            
            return {
                "sucesso": True,
                "arquivo_id": resultado["arquivo_id"],
                "tipo": tipo,
                "nome": nome_arquivo,
                "tamanho": len(content),
                "conteudo": conteudo,  # Retorna conteúdo completo
                "mensagem": f"✅ {tipo.upper()} processado! {len(conteudo)} caracteres extraídos."
            }
        else:
            erro = resultado.get("erro", "Erro desconhecido")
            print(f"[UPLOAD] ❌ ERRO: {erro}")
            print(f"{'='*60}\n")
            return {
                "sucesso": False,
                "erro": erro
            }
            
    except Exception as e:
        import traceback
        erro_completo = traceback.format_exc()
        print(f"[UPLOAD] ❌ EXCEÇÃO:")
        print(erro_completo)
        print(f"{'='*60}\n")
        return {
            "sucesso": False,
            "erro": f"Erro ao processar arquivo: {str(e)}"
        }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint REST para chat (alternativa ao WebSocket)
    """
    # Criar sessão se não existir
    if not request.session_id or request.session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = Session(session_id, request.user_name or "Usuário")
    else:
        session_id = request.session_id
    
    session = sessions[session_id]

    # Se o request trouxer profile_id, atualiza a sessão (equivalente a /api/profile)
    if request.profile_id:
        pid = str(request.profile_id).strip().lower()
        if pid not in profiles.PROFILES:
            raise HTTPException(status_code=400, detail="profile_invalido")
        session.profile_id = pid
    elif request.trq_duro_mode:
        # compat: mantém o atalho TRQ duro
        session.profile_id = "trq_duro"
    
    # Adicionar mensagem ao histórico da sessão
    session.historico.append({
        "de": session.user_name,
        "texto": request.mensagem,
        "tipo": "user"
    })
    
    # Processar com Sofia
    try:
        resposta = cerebro.perguntar(
            request.mensagem,
            historico=session.historico,
            usuario=session.user_name,
            profile_id=session.profile_id,
        )
    except Exception as e:
        resposta = f"❌ Erro ao processar mensagem: {str(e)}"
    
    # Adicionar resposta ao histórico
    session.historico.append({
        "de": "Sofia",
        "texto": resposta,
        "tipo": "assistant"
    })
    
    return ChatResponse(
        resposta=resposta,
        session_id=session_id,
        user_name=session.user_name
    )

@app.get("/api/historico/{session_id}")
async def get_historico(session_id: str, limit: int = 50):
    """Obtém o histórico de uma sessão"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "user_name": session.user_name,
        "historico": session.historico[-limit:] if limit else session.historico
    }

@app.get("/conversations")
async def get_conversations(limit: int = 50):
    """Obtém conversas da memória persistente"""
    try:
        # Buscar conversas salvas na memória
        historico = memoria.historico[-limit:] if limit else memoria.historico
        
        # Adicionar índices para permitir deleção
        conversas_com_indice = []
        total = len(memoria.historico)
        for i, conv in enumerate(historico):
            conv_copy = conv.copy()
            conv_copy["_index"] = total - len(historico) + i
            conversas_com_indice.append(conv_copy)
        
        return {
            "conversas": conversas_com_indice,
            "total": total
        }
    except Exception as e:
        return {
            "conversas": [],
            "total": 0,
            "erro": str(e)
        }

@app.get("/aprendizados")
async def get_aprendizados(categoria: Optional[str] = None):
    """Obtém aprendizados da memória"""
    try:
        if categoria:
            aprendizados_cat = memoria.listar_aprendizados(categoria)
            return {
                "categoria": categoria,
                "aprendizados": aprendizados_cat
            }
        else:
            todos = memoria.listar_aprendizados()
            return {
                "aprendizados": todos,
                "total": sum(len(cat) for cat in todos.values())
            }
    except Exception as e:
        return {
            "aprendizados": {},
            "erro": str(e)
        }

@app.get("/stats")
async def get_stats():
    """Obtém estatísticas da memória"""
    try:
        stats_text = memoria.estatisticas()
        
        # Extrair números das estatísticas
        import re
        conversas_match = re.search(r'Conversas armazenadas: (\d+)', stats_text)
        aprendizados_match = re.search(r'Aprendizados: (\d+)', stats_text)
        tamanho_match = re.search(r'Tamanho em disco: ([\d.]+) MB', stats_text)
        percentual_match = re.search(r'Uso da memória: ([\d.]+)%', stats_text)
        
        return {
            "conversas": int(conversas_match.group(1)) if conversas_match else 0,
            "aprendizados": int(aprendizados_match.group(1)) if aprendizados_match else 0,
            "tamanho_mb": float(tamanho_match.group(1)) if tamanho_match else 0,
            "percentual_uso": float(percentual_match.group(1)) if percentual_match else 0,
            "texto_completo": stats_text
        }
    except Exception as e:
        return {
            "conversas": 0,
            "aprendizados": 0,
            "erro": str(e)
        }

@app.delete("/conversations/{index}")
async def delete_conversation(index: int):
    """Remove uma conversa específica"""
    try:
        if 0 <= index < len(memoria.historico):
            removida = memoria.historico.pop(index)
            memoria.salvar_tudo()
            return {"sucesso": True, "mensagem": "Conversa removida"}
        else:
            return {"sucesso": False, "erro": "Índice inválido"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@app.post("/clear-conversations")
async def clear_conversations():
    """Limpa todas as conversas mantendo aprendizados"""
    try:
        memoria.limpar()
        return {"sucesso": True, "mensagem": "Conversas limpas"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@app.post("/clear-all")
async def clear_all():
    """Limpa tudo: conversas e aprendizados"""
    try:
        memoria.limpar_tudo()
        return {"sucesso": True, "mensagem": "Memória completamente limpa"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@app.post("/api/test-web-search")
async def test_web_search(request: dict):
    """
    Endpoint de teste para busca web
    Retorna resultados da busca diretamente
    """
    query = request.get("query", "")
    web_mode = request.get("web_mode", False)
    
    if not query:
        raise HTTPException(status_code=400, detail="Query não fornecida")
    
    try:
        # Ativar modo web temporariamente
        import os
        old_mode = os.getenv("SOFIA_MODO_WEB", "0")
        
        if web_mode:
            os.environ["SOFIA_MODO_WEB"] = "1"
        
        # Importar e usar o módulo de busca
        from sofia.core import web_search
        
        resultados = web_search.buscar_web(query, num_resultados=5)
        
        # Restaurar modo anterior
        os.environ["SOFIA_MODO_WEB"] = old_mode
        
        if resultados:
            return {
                "success": True,
                "query": query,
                "web_mode": web_mode,
                "count": len(resultados),
                "resultados": resultados
            }
        else:
            return {
                "success": False,
                "query": query,
                "web_mode": web_mode,
                "error": "Nenhum resultado encontrado"
            }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "web_mode": web_mode,
            "error": str(e)
        }


# ==================== WEBSOCKET ====================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}  # Rastrear tarefas em andamento
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        # Cancelar tarefa se existir
        if session_id in self.active_tasks:
            task = self.active_tasks[session_id]
            if not task.done():
                task.cancel()
            del self.active_tasks[session_id]
        
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)
    
    def cancel_task(self, session_id: str):
        """Cancela a tarefa de processamento em andamento"""
        if session_id in self.active_tasks:
            task = self.active_tasks[session_id]
            if not task.done():
                print(f"⏹️ Cancelando tarefa para sessão {session_id[:8]}...")
                task.cancel()
                return True
        return False

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket para chat em tempo real
    
    Mensagens esperadas do cliente:
    {
        "type": "message",
        "content": "texto da mensagem",
        "user_name": "Nome do usuário"
    }
    
    Respostas enviadas ao cliente:
    {
        "type": "response",
        "content": "resposta de Sofia",
        "session_id": "uuid"
    }
    """
    await manager.connect(websocket, session_id)
    
    # Sessão vive no servidor: não sobrescrever se já existir (preserva profile_id)
    if session_id not in sessions:
        sessions[session_id] = Session(session_id, user_name="Usuário")
    session = sessions[session_id]
    # Mantém política atual: nome padrão, sem destruir o profile/histórico
    session.user_name = "Usuário"
    
    # Enviar mensagem de boas-vindas
    await manager.send_message({
        "type": "system",
        "content": f"🌸 Conectado! Sessão: {session_id[:8]}...",
        "session_id": session_id
    }, session_id)
    
    try:
        while True:
            # Receber mensagem do cliente
            data = await websocket.receive_json()
            print(f"📨 Mensagem recebida: {data}")  # DEBUG
            
            # Tratar comando de STOP
            if data.get("type") == "stop":
                print(f"⏹️ Comando STOP recebido para sessão {session_id[:8]}...")
                # Marcar flag de cancelamento
                session.cancel_flag = True
                # Cancelar tarefa em andamento
                cancelled = manager.cancel_task(session_id)
                if cancelled:
                    print(f"✅ Tarefa cancelada com sucesso!")
                    await manager.send_message({
                        "type": "cancelled",
                        "content": "⏹️ Processamento cancelado",
                        "session_id": session_id
                    }, session_id)
                else:
                    print(f"ℹ️ Nenhuma tarefa em andamento")
                    await manager.send_message({
                        "type": "system",
                        "content": "⏹️ Nenhum processamento em andamento",
                        "session_id": session_id
                    }, session_id)
                continue
            
            if data.get("type") == "message":
                user_message = data.get("content", "")
                user_name = data.get("user_name", session.user_name)
                web_search_mode = data.get("web_search_mode", False)
                trq_duro_mode = data.get("trq_duro_mode", False)
                requested_profile_id = data.get("profile_id")
                
                print(f"💬 Processando: '{user_message}' de {user_name}")  # DEBUG
                print(f"🌐 Modo Web: {web_search_mode}")  # DEBUG
                print(f"♦ TRQ Duro: {trq_duro_mode}")  # DEBUG

                # Governança por sessão: profile vive na sessão.
                # Se o cliente pedir profile_id (ou usar o atalho trq_duro_mode), atualiza a sessão.
                if requested_profile_id:
                    pid = str(requested_profile_id).strip().lower()
                    if pid not in profiles.PROFILES:
                        await manager.send_message({
                            "type": "error",
                            "content": "❌ profile_invalido",
                            "session_id": session_id,
                        }, session_id)
                        continue
                    session.profile_id = pid
                elif trq_duro_mode:
                    session.profile_id = "trq_duro"

                print(f"🧠 Profile(sessão): {session.profile_id}")  # DEBUG
                
                # Atualizar nome do usuário se fornecido
                session.user_name = user_name
                
                # Ativar/desativar modo web via variável de ambiente
                import os
                if web_search_mode:
                    os.environ["SOFIA_MODO_WEB"] = "1"
                    print("🌍 Modo web ATIVADO")  # DEBUG
                else:
                    os.environ["SOFIA_MODO_WEB"] = "0"
                    print("🌍 Modo web DESATIVADO")  # DEBUG

                # Adicionar ao histórico da sessão
                session.historico.append({
                    "de": user_name,
                    "texto": user_message,
                    "tipo": "user"
                })
                print(f"📝 Histórico atualizado: {len(session.historico)} mensagens")  # DEBUG
                print(f"📝 Últimas 3 mensagens: {session.historico[-3:]}")  # DEBUG
                
                # Resetar flag de cancelamento
                session.cancel_flag = False
                
                # Enviar confirmação de recebimento
                await manager.send_message({
                    "type": "ack",
                    "content": "Mensagem recebida, processando...",
                    "session_id": session_id
                }, session_id)
                
                # Criar e rastrear tarefa de processamento
                async def process_message():
                    try:
                        print(f"🧠 Iniciando processamento...")  # DEBUG
                        print(f"📊 Histórico sendo passado: {len(session.historico)} mensagens")  # DEBUG
                        # Executar em thread separada para não bloquear
                        loop = asyncio.get_event_loop()
                        
                        # 🛑 Callback para verificar cancelamento
                        def check_cancelled():
                            return session.cancel_flag
                        
                        resposta = await loop.run_in_executor(
                            None,
                            cerebro.perguntar,
                            user_message,
                            session.historico,
                            user_name,
                            check_cancelled,  # ← Passa callback de cancelamento
                            session.profile_id,
                        )
                        print(f"✅ Resposta gerada: {len(resposta)} chars")  # DEBUG
                        
                        # 🛑 Verificar se foi cancelado após processar
                        if session.cancel_flag:
                            print(f"⏹️ Processamento cancelado - resposta descartada")
                            return  # Não envia resposta
                        
                        # Adicionar resposta ao histórico
                        session.historico.append({
                            "de": "Sofia",
                            "texto": resposta,
                            "tipo": "assistant"
                        })
                        
                        # Enviar resposta
                        await manager.send_message({
                            "type": "response",
                            "content": resposta,
                            "session_id": session_id,
                            "user_name": user_name
                        }, session_id)
                        
                    except asyncio.CancelledError:
                        print(f"⏹️ Processamento cancelado pelo usuário")
                        raise  # Re-raise para limpar a tarefa
                    except Exception as e:
                        print(f"❌ Erro ao processar: {e}")  # DEBUG
                        await manager.send_message({
                            "type": "error",
                            "content": f"❌ Erro: {str(e)}",
                            "session_id": session_id
                        }, session_id)
                
                # Criar tarefa e armazenar para poder cancelar
                task = asyncio.create_task(process_message())
                manager.active_tasks[session_id] = task
                
                # Aguardar conclusão ou cancelamento
                try:
                    await task
                except asyncio.CancelledError:
                    print(f"⏹️ Tarefa foi cancelada")
                finally:
                    # Limpar tarefa concluída
                    if session_id in manager.active_tasks:
                        del manager.active_tasks[session_id]
            
            elif data.get("type") == "ping":
                await manager.send_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }, session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"🔌 WebSocket desconectado: {session_id[:8]}...")
    except Exception as e:
        print(f"❌ Erro no WebSocket: {e}")
        manager.disconnect(session_id)
# ==================== TELEMETRIA TRQ + QWEN ====================

@app.get("/api/trq/telemetria")
async def trq_telemetria(limit: int = 20):
    """
    Lê os últimos registros da simulação TRQ (simular_trq_floquet_v2)
    gerados pelo monitor_execucao.
    """
    log_path = os.path.join(LOGS_EXEC_DIR, "simular_trq_floquet_v2_log.jsonl")

    if not os.path.exists(log_path):
        return {"ok": False, "mensagem": "Nenhum log encontrado ainda."}

    linhas = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    linhas.append(json.loads(line))
                except Exception:
                    continue
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao ler logs: {e}"}

    # Pega só os últimos N registros
    linhas = linhas[-limit:]

    return {
        "ok": True,
        "total": len(linhas),
        "registros": linhas,
    }


@app.post("/api/trq/otimizar")
async def trq_otimizar():
    """
    Usa o Qwen (via otimizador_qwen) para analisar os logs
    da simulação TRQ e sugerir melhorias de código.
    """
    try:
        if analisar_e_otimizar is None:
            return {"ok": False, "erro": "Função analisar_e_otimizar não está disponível."}
        sugestao = analisar_e_otimizar(funcao="simular_trq_floquet_v2")
        return {"ok": True, "sugestao": sugestao}
    except Exception as e:
        return {"ok": False, "erro": str(e)}

# ==================== ARQUIVOS ESTÁTICOS ====================

# Montar pasta web para servir arquivos estáticos
web_dir = Path(__file__).parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Executado quando a API inicia"""
    print("=" * 60)
    print("🌸 Sofia API iniciada!")
    print("=" * 60)
    print("📍 Acesse: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws/{session_id}")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Executado quando a API é encerrada"""
    print("\n🌸 Sofia API encerrada. Até logo!")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_web:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
