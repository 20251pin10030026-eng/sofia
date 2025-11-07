"""
Memória persistente de conversas com aprendizado
Sistema de memória de 5GB para armazenar e aprender com conversas
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Configurações
MEMORIA_DIR = Path(__file__).resolve().parents[1] / ".sofia_internal" / "memoria"
MEMORIA_ARQUIVO = MEMORIA_DIR / "conversas.json"
APRENDIZADOS_ARQUIVO = MEMORIA_DIR / "aprendizados.json"
MAX_SIZE_BYTES = 5 * 1024 * 1024 * 1024  # 5 GB
CONTEXTO_RECENTE = 200  # Número de mensagens recentes mantidas em RAM (aumentado de 50)
MAX_CHARS_POR_MENSAGEM = 100000  # Máximo de 100.000 caracteres por mensagem individual

# Memória em RAM (cache)
historico = []
aprendizados = {}

def _garantir_diretorio():
    """Cria o diretório de memória se não existir"""
    MEMORIA_DIR.mkdir(parents=True, exist_ok=True)

def _calcular_tamanho_memoria():
    """Calcula o tamanho total da memória em disco"""
    tamanho = 0
    if MEMORIA_ARQUIVO.exists():
        tamanho += MEMORIA_ARQUIVO.stat().st_size
    if APRENDIZADOS_ARQUIVO.exists():
        tamanho += APRENDIZADOS_ARQUIVO.stat().st_size
    return tamanho

def _carregar_memoria():
    """Carrega o histórico do disco"""
    global historico
    _garantir_diretorio()
    
    if MEMORIA_ARQUIVO.exists():
        try:
            with open(MEMORIA_ARQUIVO, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                historico = dados.get('conversas', [])
                # Mantém apenas as mais recentes em RAM
                if len(historico) > CONTEXTO_RECENTE:
                    historico = historico[-CONTEXTO_RECENTE:]
        except Exception as e:
            print(f"⚠️ Erro ao carregar memória: {e}")
            historico = []

def _carregar_aprendizados():
    """Carrega aprendizados do disco"""
    global aprendizados
    _garantir_diretorio()
    
    if APRENDIZADOS_ARQUIVO.exists():
        try:
            with open(APRENDIZADOS_ARQUIVO, 'r', encoding='utf-8') as f:
                aprendizados = json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar aprendizados: {e}")
            aprendizados = {}

def _salvar_memoria():
    """Salva o histórico completo no disco"""
    _garantir_diretorio()
    
    # Verifica o tamanho antes de salvar
    if _calcular_tamanho_memoria() >= MAX_SIZE_BYTES:
        # Remove 20% das conversas mais antigas
        _compactar_memoria()
    
    try:
        # Carrega todas as conversas do disco se existir
        todas_conversas = []
        if MEMORIA_ARQUIVO.exists():
            with open(MEMORIA_ARQUIVO, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                todas_conversas = dados.get('conversas', [])
        
        # Adiciona as novas conversas do histórico em RAM
        for conv in historico:
            if conv not in todas_conversas:
                todas_conversas.append(conv)
        
        # Salva tudo
        dados = {
            'conversas': todas_conversas,
            'total_conversas': len(todas_conversas),
            'ultima_atualizacao': datetime.now().isoformat(),
            'tamanho_bytes': _calcular_tamanho_memoria()
        }
        
        with open(MEMORIA_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Erro ao salvar memória: {e}")

def _salvar_aprendizados():
    """Salva aprendizados no disco"""
    _garantir_diretorio()
    
    try:
        with open(APRENDIZADOS_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump(aprendizados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Erro ao salvar aprendizados: {e}")

def _compactar_memoria():
    """Remove 20% das conversas mais antigas quando atinge o limite"""
    try:
        if MEMORIA_ARQUIVO.exists():
            with open(MEMORIA_ARQUIVO, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                conversas = dados.get('conversas', [])
            
            # Remove 20% das mais antigas
            quantidade_remover = int(len(conversas) * 0.2)
            conversas = conversas[quantidade_remover:]
            
            dados['conversas'] = conversas
            dados['total_conversas'] = len(conversas)
            dados['ultima_compactacao'] = datetime.now().isoformat()
            
            with open(MEMORIA_ARQUIVO, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            
            print(f"🗜️ Memória compactada: {quantidade_remover} conversas antigas removidas")
    except Exception as e:
        print(f"⚠️ Erro ao compactar memória: {e}")

def inicializar():
    """Inicializa o sistema de memória"""
    _carregar_memoria()
    _carregar_aprendizados()

def adicionar(usuario, mensagem, contexto=None):
    """
    Adiciona uma mensagem ao histórico com timestamp e contexto
    
    Args:
        usuario: Nome do usuário
        mensagem: Texto da mensagem (até 100.000 caracteres)
        contexto: Dicionário opcional com informações adicionais
    """
    global historico
    
    # Validar tamanho da mensagem
    if len(mensagem) > MAX_CHARS_POR_MENSAGEM:
        print(f"⚠️ Mensagem muito longa ({len(mensagem)} caracteres). Truncando para {MAX_CHARS_POR_MENSAGEM} caracteres.")
        mensagem = mensagem[:MAX_CHARS_POR_MENSAGEM] + "... [mensagem truncada automaticamente]"
    
    entrada = {
        "de": usuario,
        "texto": mensagem,
        "timestamp": datetime.now().isoformat(),
        "contexto": contexto or {},
        "tamanho": len(mensagem)  # Adiciona informação de tamanho
    }
    
    historico.append(entrada)
    
    # Salva periodicamente (a cada 5 mensagens)
    if len(historico) % 5 == 0:
        _salvar_memoria()

def adicionar_resposta_sofia(mensagem, sentimento=None):
    """
    Adiciona uma resposta da Sofia ao histórico
    
    Args:
        mensagem: Texto da resposta (até 100.000 caracteres)
        sentimento: Sentimento associado à resposta
    """
    # Validar tamanho da mensagem
    if len(mensagem) > MAX_CHARS_POR_MENSAGEM:
        print(f"⚠️ Resposta muito longa ({len(mensagem)} caracteres). Truncando para {MAX_CHARS_POR_MENSAGEM} caracteres.")
        mensagem = mensagem[:MAX_CHARS_POR_MENSAGEM] + "... [resposta truncada automaticamente]"
    
    entrada = {
        "de": "Sofia",
        "texto": mensagem,
        "timestamp": datetime.now().isoformat(),
        "sentimento": sentimento,
        "tamanho": len(mensagem)  # Adiciona informação de tamanho
    }
    
    historico.append(entrada)
    _salvar_memoria()

def aprender(chave: str, valor: Any, categoria: str = "geral"):
    """
    Armazena um aprendizado
    
    Args:
        chave: Identificador do aprendizado
        valor: Conteúdo do aprendizado
        categoria: Categoria do aprendizado (preferencias, fatos, padroes, etc)
    """
    global aprendizados
    
    if categoria not in aprendizados:
        aprendizados[categoria] = {}
    
    aprendizados[categoria][chave] = {
        "valor": valor,
        "aprendido_em": datetime.now().isoformat(),
        "frequencia": aprendizados.get(categoria, {}).get(chave, {}).get("frequencia", 0) + 1
    }
    
    _salvar_aprendizados()

def buscar_aprendizado(chave: str, categoria: str = "geral"):
    """Busca um aprendizado específico"""
    return aprendizados.get(categoria, {}).get(chave)

def listar_aprendizados(categoria: str | None = None):
    """Lista todos os aprendizados de uma categoria ou todas"""
    if categoria:
        return aprendizados.get(categoria, {})
    return aprendizados

def buscar_conversas(termo: str, limite: int = 10) -> List[Dict]:
    """
    Busca conversas que contenham um termo específico
    
    Args:
        termo: Termo a buscar
        limite: Número máximo de resultados
    
    Returns:
        Lista de conversas encontradas
    """
    _garantir_diretorio()
    resultados = []
    
    try:
        if MEMORIA_ARQUIVO.exists():
            with open(MEMORIA_ARQUIVO, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                conversas = dados.get('conversas', [])
                
                for conv in conversas:
                    if termo.lower() in conv.get('texto', '').lower():
                        resultados.append(conv)
                        if len(resultados) >= limite:
                            break
    except Exception as e:
        print(f"⚠️ Erro ao buscar conversas: {e}")
    
    return resultados

def ver_historico(quantidade: int = 10):
    """Mostra o histórico de conversas"""
    if not historico:
        return "📭 Nenhuma conversa ainda."
    
    texto = f"\n📚 Últimas {min(quantidade, len(historico))} conversas:\n" + "-"*40 + "\n"
    for msg in historico[-quantidade:]:
        timestamp = msg.get('timestamp', '')
        if timestamp:
            dt = datetime.fromisoformat(timestamp)
            hora = dt.strftime('%H:%M:%S')
            texto += f"[{hora}] "
        texto += f"{msg['de']}: {msg['texto'][:100]}\n"
    return texto

def estatisticas():
    """Mostra estatísticas da memória"""
    _garantir_diretorio()
    
    total_conversas = 0
    if MEMORIA_ARQUIVO.exists():
        try:
            with open(MEMORIA_ARQUIVO, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                total_conversas = dados.get('total_conversas', 0)
        except:
            pass
    
    tamanho = _calcular_tamanho_memoria()
    tamanho_mb = tamanho / (1024 * 1024)
    tamanho_gb = tamanho / (1024 * 1024 * 1024)
    percentual = (tamanho / MAX_SIZE_BYTES) * 100
    
    total_aprendizados = sum(len(cat) for cat in aprendizados.values())
    
    # Calcular estatísticas de tamanho das mensagens
    tamanhos = [msg.get("tamanho", len(msg.get("texto", ""))) for msg in historico]
    tamanho_medio = sum(tamanhos) / len(tamanhos) if tamanhos else 0
    tamanho_maximo = max(tamanhos) if tamanhos else 0
    
    stats = f"""
📊 Estatísticas da Memória de Sofia
{"="*50}
💾 Conversas armazenadas: {total_conversas}
🧠 Aprendizados: {total_aprendizados}
📁 Tamanho em disco: {tamanho_mb:.2f} MB ({tamanho_gb:.4f} GB)
📈 Uso da memória: {percentual:.2f}% de 5 GB
🔢 Em cache (RAM): {len(historico)} conversas
📝 Tamanho médio por mensagem: {tamanho_medio:.0f} caracteres
📏 Maior mensagem: {tamanho_maximo:,} caracteres
💯 Capacidade por mensagem: {MAX_CHARS_POR_MENSAGEM:,} caracteres
🔄 Contexto enviado à IA: últimas 30 mensagens
{"="*50}
"""
    return stats

def limpar():
    """Limpa o histórico (mantém aprendizados)"""
    global historico
    historico = []
    _salvar_memoria()
    print("🧹 Memória de conversas limpa! (Aprendizados mantidos)")

def limpar_tudo():
    """Limpa tudo: histórico e aprendizados"""
    global historico, aprendizados
    historico = []
    aprendizados = {}
    
    if MEMORIA_ARQUIVO.exists():
        MEMORIA_ARQUIVO.unlink()
    if APRENDIZADOS_ARQUIVO.exists():
        APRENDIZADOS_ARQUIVO.unlink()
    
    print("🧹 Memória completamente limpa! (Conversas e aprendizados)")

def salvar_tudo():
    """Força salvamento de tudo"""
    _salvar_memoria()
    _salvar_aprendizados()
    print("💾 Memória salva com sucesso!")

# Inicializa ao importar
inicializar()
