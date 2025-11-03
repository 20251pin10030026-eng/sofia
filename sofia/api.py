#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sofia Web API - Servidor Flask para interface web
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar sofia como módulo
ROOT = Path(__file__).resolve().parent.parent  # A.I_GitHUB/
sys.path.insert(0, str(ROOT))

from sofia.core import identidade, cerebro, memoria

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Inicializa Sofia
nome_sistema = os.getenv("USERNAME") or os.getenv("USER") or "Usuario"
try:
    identidade._ativar_protocolo_oculto(nome_sistema)
except Exception:
    pass

@app.route('/status', methods=['GET'])
def status():
    """Verifica se a API está online"""
    return jsonify({
        'status': 'online',
        'sofia': 'ready'
    })

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

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌸 Sofia Web API")
    print("="*50)
    print("\n✅ Servidor iniciado em http://localhost:5000")
    print("✅ Abra web/index.html no navegador para acessar a interface\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
