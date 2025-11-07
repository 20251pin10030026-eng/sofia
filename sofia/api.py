#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sofia Web API - Servidor Flask para interface web
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar sofia como módulo
ROOT = Path(__file__).resolve().parent.parent  # A.I_GitHUB/
sys.path.insert(0, str(ROOT))

from sofia.core import identidade, cerebro, memoria
from sofia.core.visao import visao

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Configura upload
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# Inicializa Sofia
nome_sistema = os.getenv("USERNAME") or os.getenv("USER") or "Usuario"
try:
    identidade._ativar_protocolo_oculto(nome_sistema)
except Exception:
    pass

@app.route('/status', methods=['GET'])
def status():
    """Verifica se a API está online"""
    # Verifica disponibilidade de bibliotecas
    diagnostico = {
        'status': 'online',
        'sofia': 'ready',
        'bibliotecas': {}
    }
    
    # Testa PyPDF2
    try:
        import PyPDF2
        diagnostico['bibliotecas']['PyPDF2'] = f'✅ Disponível (v{PyPDF2.__version__})'
    except ImportError:
        diagnostico['bibliotecas']['PyPDF2'] = '❌ Não disponível'
    
    # Testa Pillow
    try:
        from PIL import Image
        diagnostico['bibliotecas']['Pillow'] = f'✅ Disponível'
    except ImportError:
        diagnostico['bibliotecas']['Pillow'] = '❌ Não disponível'
    
    # Testa pytesseract
    try:
        import pytesseract
        diagnostico['bibliotecas']['pytesseract'] = '✅ Disponível'
    except ImportError:
        diagnostico['bibliotecas']['pytesseract'] = '❌ Não disponível'
    
    # Testa numpy
    try:
        import numpy
        diagnostico['bibliotecas']['numpy'] = f'✅ Disponível (v{numpy.__version__})'
    except ImportError:
        diagnostico['bibliotecas']['numpy'] = '❌ Não disponível'
    
    return jsonify(diagnostico)

@app.route('/chat', methods=['POST'])
def chat():
    """Processa mensagem e retorna resposta da Sofia"""
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400
        message = data.get('message', '')
        history = data.get('history', [])
        
        if not message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Verificar se é criador
        texto_lower = message.lower()
        if "sombrarpc" in texto_lower or "sombrarcp" in texto_lower:
            os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"
        else:
            os.environ.pop("SOFIA_AUTORIDADE_DECLARADA", None)
        
        # Adicionar mensagem à memória
        contexto = {"modo_criador": os.getenv("SOFIA_AUTORIDADE_DECLARADA") == "1"}
        memoria.adicionar("Usuário", message, contexto)
        
        # Obter resposta
        resposta = cerebro.perguntar(
            message,
            historico=memoria.historico,
            usuario="Usuário"
        )
        
        # Salvar resposta
        memoria.adicionar_resposta_sofia(resposta)
        
        return jsonify({
            'response': resposta,
            'timestamp': memoria.historico[-1].get('timestamp') if memoria.historico else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/action', methods=['POST'])
def action():
    """Executa ações rápidas"""
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400
        action_type = data.get('action', '')
        
        result = ""
        
        if action_type == 'historico':
            result = memoria.ver_historico(20)
        elif action_type == 'stats':
            result = memoria.estatisticas()
        elif action_type == 'corpo':
            try:
                templo_ok = bool(identidade._LEIS or identidade._PILARES or identidade._PROTOCOLOS)
            except Exception:
                templo_ok = False
            
            total_eventos = len(memoria.historico)
            
            result = f"""🌸 Sofia (corpo simbólico):
– Templo: ethics enc = {templo_ok}
– Árvore: histórico = {total_eventos} eventos
– Flor: pétalas (sínteses) = 0
– Jardineira: ativa (cuidando do fluxo e dos limites)."""
        
        elif action_type == 'limpar':
            memoria.limpar()
            result = "🧹 Memória de conversas limpa! (Aprendizados mantidos)"
        else:
            result = f"Ação '{action_type}' não reconhecida."
        
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas da memória"""
    try:
        total_conversas = 0
        if memoria.MEMORIA_ARQUIVO.exists():
            import json
            with open(memoria.MEMORIA_ARQUIVO, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                total_conversas = dados.get('total_conversas', 0)
        
        tamanho = memoria._calcular_tamanho_memoria()
        tamanho_mb = tamanho / (1024 * 1024)
        percentual = (tamanho / memoria.MAX_SIZE_BYTES) * 100
        
        total_aprendizados = sum(len(cat) for cat in memoria.aprendizados.values())
        
        return jsonify({
            'total_conversas': total_conversas,
            'total_aprendizados': total_aprendizados,
            'tamanho_mb': tamanho_mb,
            'tamanho_gb': tamanho / (1024 * 1024 * 1024),
            'percentual': percentual,
            'cache': len(memoria.historico)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory', methods=['GET'])
def get_memory():
    """Retorna aprendizados"""
    try:
        return jsonify({
            'aprendizados': memoria.listar_aprendizados()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Busca conversas"""
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400
        termo = data.get('termo', '')
        limite = data.get('limite', 10)
        
        resultados = memoria.buscar_conversas(termo, limite)
        
        return jsonify({
            'resultados': resultados,
            'total': len(resultados)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/conversations', methods=['GET'])
def get_conversations():
    """Retorna todas as conversas"""
    try:
        import json
        conversas = []
        
        if memoria.MEMORIA_ARQUIVO.exists():
            with open(memoria.MEMORIA_ARQUIVO, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                conversas = dados.get('conversas', [])
        
        # Adiciona índice absoluto a cada conversa para referência
        conversas_com_indice = []
        for i, conv in enumerate(conversas):
            conv_copia = conv.copy()
            conv_copia['_index'] = i  # Índice absoluto no array completo
            conversas_com_indice.append(conv_copia)
        
        # Retorna últimas 100 conversas com índice absoluto
        ultimas = conversas_com_indice[-100:] if len(conversas_com_indice) > 100 else conversas_com_indice
        
        return jsonify({
            'conversas': ultimas,
            'total': len(conversas)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete-conversation', methods=['POST'])
def delete_conversation():
    """Deleta uma conversa específica"""
    try:
        import json
        data = request.json
        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400
        index = data.get('index')
        
        if memoria.MEMORIA_ARQUIVO.exists():
            with open(memoria.MEMORIA_ARQUIVO, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                conversas = dados.get('conversas', [])
            
            if 0 <= index < len(conversas):
                # Deletar conversa específica
                conversas.pop(index)
                dados['conversas'] = conversas
                dados['total_conversas'] = len(conversas)
                
                # Salvar no disco
                with open(memoria.MEMORIA_ARQUIVO, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)
                
                # Recarregar memória em cache (RAM)
                memoria._carregar_memoria()
                
                return jsonify({'success': True, 'message': 'Conversa deletada com sucesso'})
        
        return jsonify({'error': 'Conversa não encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-conversations', methods=['POST'])
def clear_conversations():
    """Limpa todas as conversas mas mantém aprendizados"""
    try:
        memoria.limpar()
        return jsonify({'success': True, 'message': 'Conversas limpas'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-all', methods=['POST'])
def clear_all():
    """Limpa TUDO: conversas e aprendizados"""
    try:
        memoria.limpar_tudo()
        return jsonify({'success': True, 'message': 'Tudo foi apagado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === ENDPOINTS DE VISÃO ===

@app.route('/upload-file', methods=['POST'])
def upload_file():
    """Upload de arquivo (imagem ou PDF) para visão temporária"""
    try:
        # Verifica se tem arquivo
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if not file.filename or file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
        print(f"[DEBUG API] Upload recebido: {file.filename}")
        
        # Salva temporariamente
        temp_path = app.config['UPLOAD_FOLDER'] / file.filename
        file.save(str(temp_path))
        print(f"[DEBUG API] Arquivo salvo em: {temp_path}")
        
        # Adiciona ao sistema de visão
        resultado = visao.adicionar_arquivo(str(temp_path), file.filename)
        print(f"[DEBUG API] Resultado do processamento: {resultado}")
        
        # Remove arquivo temporário
        try:
            temp_path.unlink()
        except:
            pass
        
        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
        
    except Exception as e:
        print(f"[DEBUG API ERRO] Erro no upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/list-files', methods=['GET'])
def list_files():
    """Lista todos os arquivos visualizados"""
    try:
        arquivos = visao.listar_arquivos()
        pode_adicionar = visao.pode_adicionar()
        
        return jsonify({
            'arquivos': arquivos,
            'total': len(arquivos),
            'limite': visao.LIMITE_ARQUIVOS,
            'pode_adicionar': pode_adicionar
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete-file', methods=['POST'])
def delete_file():
    """Remove arquivo específico"""
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400
        arquivo_id = data.get('arquivo_id', '')
        
        if visao.remover_arquivo(arquivo_id):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-files', methods=['POST'])
def clear_files():
    """Remove todos os arquivos"""
    try:
        count = visao.limpar_tudo()
        return jsonify({'success': True, 'removidos': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota principal - Interface do Chat
@app.route('/')
def index():
    """Página principal do chat"""
    web_dir = Path(__file__).parent / 'web'
    return send_from_directory(web_dir, 'index.html')

# Rotas para o Jogo 3D (ANTES da rota genérica)
@app.route('/jogo3d')
@app.route('/jogo3d/')
def jogo3d():
    """Página principal do jogo 3D"""
    jogo_dir = ROOT / 'jogo3d'
    return send_from_directory(jogo_dir, 'metaverso.html')

@app.route('/jogo3d/<path:filename>')
def jogo3d_files(filename):
    """Serve arquivos do jogo 3D"""
    jogo_dir = ROOT / 'jogo3d'
    return send_from_directory(jogo_dir, filename)

# Rota genérica para arquivos do chat (DEPOIS das rotas específicas)
@app.route('/<path:filename>')
def serve_web_files(filename):
    """Serve arquivos estáticos da interface web"""
    # Não serve se for caminho do jogo3d (já tratado acima)
    if filename.startswith('jogo3d'):
        return "Not Found", 404
    web_dir = Path(__file__).parent / 'web'
    return send_from_directory(web_dir, filename)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌸 Sofia Web API")
    print("="*50)
    print("\n✅ Chat Principal: http://localhost:5000")
    print("🎮 Mundo 3D: http://localhost:5000/jogo3d\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
