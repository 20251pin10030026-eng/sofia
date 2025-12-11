"""
Memória persistente de conversas com aprendizado
Sistema de memória de 5GB para armazenar e aprender com conversas.

Agora com suporte a ESCOPOS DE MEMÓRIA:
- cada sessão/usuário pode ter sua própria bolha de memória,
  via contexto['escopo_memoria'].
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configurações
MEMORIA_DIR = Path(__file__).resolve().parents[1] / ".sofia_internal" / "memoria"
MEMORIA_ARQUIVO = MEMORIA_DIR / "conversas.json"
APRENDIZADOS_ARQUIVO = MEMORIA_DIR / "aprendizados.json"
MAX_SIZE_BYTES = 5 * 1024 * 1024 * 1024  # 5 GB
CONTEXTO_RECENTE = 200  # Número de mensagens recentes mantidas em RAM
MAX_CHARS_POR_MENSAGEM = 100000  # Máximo de 100.000 caracteres por mensagem individual

# Memória em RAM (cache)
historico: List[Dict[str, Any]] = []
aprendizados: Dict[str, Dict[str, Any]] = {}


def _garantir_diretorio():
    """Cria o diretório de memória se não existir."""
    MEMORIA_DIR.mkdir(parents=True, exist_ok=True)


def _calcular_tamanho_memoria() -> int:
    """Calcula o tamanho total da memória em disco."""
    tamanho = 0
    if MEMORIA_ARQUIVO.exists():
        tamanho += MEMORIA_ARQUIVO.stat().st_size
    if APRENDIZADOS_ARQUIVO.exists():
        tamanho += APRENDIZADOS_ARQUIVO.stat().st_size
    return tamanho


def _carregar_memoria():
    """Carrega o histórico do disco para o cache em RAM."""
    global historico
    _garantir_diretorio()

    if MEMORIA_ARQUIVO.exists():
        try:
            with open(MEMORIA_ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                historico = dados.get("conversas", [])
                # Mantém apenas as mais recentes em RAM
                if len(historico) > CONTEXTO_RECENTE:
                    historico = historico[-CONTEXTO_RECENTE:]
        except Exception as e:
            print(f"⚠️ Erro ao carregar memória: {e}")
            historico = []


def _carregar_aprendizados():
    """Carrega aprendizados do disco."""
    global aprendizados
    _garantir_diretorio()

    if APRENDIZADOS_ARQUIVO.exists():
        try:
            with open(APRENDIZADOS_ARQUIVO, "r", encoding="utf-8") as f:
                aprendizados = json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar aprendizados: {e}")
            aprendizados = {}


def _salvar_memoria():
    """Salva o histórico completo no disco (merge incremental)."""
    _garantir_diretorio()

    # Verifica o tamanho antes de salvar
    if _calcular_tamanho_memoria() >= MAX_SIZE_BYTES:
        # Remove 20% das conversas mais antigas
        _compactar_memoria()

    try:
        # Carrega todas as conversas do disco se existir
        todas_conversas: List[Dict[str, Any]] = []
        if MEMORIA_ARQUIVO.exists():
            with open(MEMORIA_ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                todas_conversas = dados.get("conversas", [])

        # Adiciona as novas conversas do histórico em RAM
        for conv in historico:
            if conv not in todas_conversas:
                todas_conversas.append(conv)

        # Salva tudo
        dados = {
            "conversas": todas_conversas,
            "total_conversas": len(todas_conversas),
            "ultima_atualizacao": datetime.now().isoformat(),
            "tamanho_bytes": _calcular_tamanho_memoria(),
        }

        with open(MEMORIA_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Erro ao salvar memória: {e}")


def _salvar_memoria_forcado(conversas_para_salvar: List[Dict[str, Any]]):
    """Salva conversas específicas forçadamente (usado por limpar)."""
    _garantir_diretorio()

    try:
        dados = {
            "conversas": conversas_para_salvar,
            "total_conversas": len(conversas_para_salvar),
            "ultima_atualizacao": datetime.now().isoformat(),
            "tamanho_bytes": _calcular_tamanho_memoria(),
        }

        with open(MEMORIA_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Erro ao salvar memória: {e}")


def _salvar_aprendizados():
    """Salva aprendizados no disco."""
    _garantir_diretorio()

    try:
        with open(APRENDIZADOS_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(aprendizados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Erro ao salvar aprendizados: {e}")


def _compactar_memoria():
    """Remove 20% das conversas mais antigas quando atinge o limite."""
    try:
        if MEMORIA_ARQUIVO.exists():
            with open(MEMORIA_ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                conversas = dados.get("conversas", [])

            # Remove 20% das mais antigas
            quantidade_remover = int(len(conversas) * 0.2)
            conversas = conversas[quantidade_remover:]

            dados["conversas"] = conversas
            dados["total_conversas"] = len(conversas)
            dados["ultima_compactacao"] = datetime.now().isoformat()

            with open(MEMORIA_ARQUIVO, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)

            print(f"🗜️ Memória compactada: {quantidade_remover} conversas antigas removidas")
    except Exception as e:
        print(f"⚠️ Erro ao compactar memória: {e}")


def inicializar():
    """Inicializa o sistema de memória."""
    _carregar_memoria()
    _carregar_aprendizados()


def _mesmo_escopo(msg: Dict[str, Any], escopo: Optional[str]) -> bool:
    """
    Retorna True se a mensagem pertence ao mesmo escopo de memória.

    - escopo = None  → não filtra (comportamento global antigo).
    - escopo = string → compara com contexto['escopo_memoria'].
    """
    if escopo is None:
        return True

    ctx = msg.get("contexto") or {}
    return ctx.get("escopo_memoria") == escopo


def adicionar(usuario: str, mensagem: str, contexto: Dict[str, Any] | None = None):
    """
    Adiciona uma mensagem ao histórico com timestamp e contexto.

    Se 'contexto' trouxer 'escopo_memoria', isso será usado depois para
    filtrar buscas de memória (cada sessão/usuário em sua própria bolha).
    """
    global historico

    # Validar tamanho da mensagem
    if len(mensagem) > MAX_CHARS_POR_MENSAGEM:
        print(
            f"⚠️ Mensagem muito longa ({len(mensagem)} caracteres). "
            f"Truncando para {MAX_CHARS_POR_MENSAGEM} caracteres."
        )
        mensagem = (
            mensagem[:MAX_CHARS_POR_MENSAGEM]
            + "... [mensagem truncada automaticamente]"
        )

    entrada = {
        "de": usuario,
        "texto": mensagem,
        "timestamp": datetime.now().isoformat(),
        "contexto": contexto or {},
        "tamanho": len(mensagem),
    }

    historico.append(entrada)

    # Salva periodicamente (a cada 5 mensagens)
    if len(historico) % 5 == 0:
        _salvar_memoria()


def adicionar_resposta_sofia(mensagem: str, sentimento: str | None = None):
    """
    Adiciona uma resposta da Sofia ao histórico.

    A resposta herda o 'escopo_memoria' da última mensagem registrada,
    para que pergunta e resposta fiquem no mesmo universo de memória.
    """
    global historico

    # Validar tamanho da mensagem
    if len(mensagem) > MAX_CHARS_POR_MENSAGEM:
        print(
            f"⚠️ Resposta muito longa ({len(mensagem)} caracteres). "
            f"Truncando para {MAX_CHARS_POR_MENSAGEM} caracteres."
        )
        mensagem = (
            mensagem[:MAX_CHARS_POR_MENSAGEM]
            + "... [resposta truncada automaticamente]"
        )

    escopo = None
    if historico:
        ctx_ult = historico[-1].get("contexto") or {}
        escopo = ctx_ult.get("escopo_memoria")

    contexto: Dict[str, Any] = {"sentimento": sentimento}
    if escopo is not None:
        contexto["escopo_memoria"] = escopo

    entrada = {
        "de": "Sofia",
        "texto": mensagem,
        "timestamp": datetime.now().isoformat(),
        "contexto": contexto,
        "sentimento": sentimento,
        "tamanho": len(mensagem),
    }

    historico.append(entrada)
    _salvar_memoria()


def aprender(chave: str, valor: Any, categoria: str = "geral"):
    """
    Armazena um aprendizado.

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
        "frequencia": aprendizados.get(categoria, {})
        .get(chave, {})
        .get("frequencia", 0)
        + 1,
    }

    _salvar_aprendizados()


def buscar_aprendizado(chave: str, categoria: str = "geral"):
    """Busca um aprendizado específico."""
    return aprendizados.get(categoria, {}).get(chave)


def listar_aprendizados(categoria: str | None = None):
    """Lista todos os aprendizados de uma categoria ou todas."""
    if categoria:
        return aprendizados.get(categoria, {})
    return aprendizados


def buscar_conversas(
    termo: str,
    limite: int = 10,
    escopo_memoria: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Busca conversas que contenham um termo específico.

    Args:
        termo: Termo a buscar
        limite: Número máximo de resultados
        escopo_memoria: se fornecido, filtra por 'escopo_memoria' no contexto

    Returns:
        Lista de conversas encontradas
    """
    _garantir_diretorio()
    resultados: List[Dict[str, Any]] = []

    try:
        if MEMORIA_ARQUIVO.exists():
            with open(MEMORIA_ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                conversas = dados.get("conversas", [])

                for conv in conversas:
                    if not _mesmo_escopo(conv, escopo_memoria):
                        continue
                    if termo.lower() in conv.get("texto", "").lower():
                        resultados.append(conv)
                        if len(resultados) >= limite:
                            break
    except Exception as e:
        print(f"⚠️ Erro ao buscar conversas: {e}")

    return resultados


def ver_historico(quantidade: int = 10) -> str:
    """Mostra o histórico de conversas (apenas cache atual em RAM)."""
    if not historico:
        return "📭 Nenhuma conversa ainda."

    texto = (
        f"\n📚 Últimas {min(quantidade, len(historico))} conversas:\n"
        + "-" * 40
        + "\n"
    )
    for msg in historico[-quantidade:]:
        timestamp = msg.get("timestamp", "")
        if timestamp:
            dt = datetime.fromisoformat(timestamp)
            hora = dt.strftime("%H:%M:%S")
            texto += f"[{hora}] "
        texto += f"{msg.get('de', 'desconhecido')}: {msg.get('texto', '')[:100]}\n"
    return texto


def buscar_fatos_relevantes(
    texto: str,
    limite: int = 5,
    escopo_memoria: Optional[str] = None,
) -> str:
    """
    Retorna um pequeno contexto com fatos/mensagens relevantes da memória
    relacionados ao texto atual, dentro do escopo de memória atual.
    """
    func_busca = globals().get("buscar_conversas")
    if not callable(func_busca):
        return ""

    try:
        resultados = func_busca(texto, limite=limite, escopo_memoria=escopo_memoria)
    except Exception:
        return ""

    if not resultados or not isinstance(resultados, list):
        return ""

    partes = ["📌 Fatos relevantes da memória (escopo atual):"]
    for conv in resultados:
        quem = conv.get("de", "desconhecido")
        trecho = conv.get("texto", "")[:200]
        partes.append(f"- {quem}: {trecho}")

    return "\n".join(partes)


def resgatar_contexto_conversa(
    texto: str = "",
    max_mensagens: int = 30,
    escopo_memoria: Optional[str] = None,
) -> str:
    """
    Monta um contexto histórico recente da conversa a partir do 'historico'
    mantido em memória, filtrando por escopo de memória se fornecido.
    O parâmetro 'texto' é mantido só por compatibilidade.
    """
    hist = globals().get("historico")
    if not isinstance(hist, list) or not hist:
        return ""

    # Filtra apenas mensagens do mesmo escopo, se houver
    msgs_filtradas: List[Dict[str, Any]] = []
    for msg in hist:
        if _mesmo_escopo(msg, escopo_memoria):
            msgs_filtradas.append(msg)

    if not msgs_filtradas:
        return ""

    ultimas = msgs_filtradas[-max_mensagens:]

    partes = ["🧵 Contexto recente da conversa (escopo atual):"]
    for msg in ultimas:
        de = msg.get("de", "desconhecido")
        trecho = msg.get("texto", "")[:400]
        partes.append(f"{de}: {trecho}")

    return "\n".join(partes)


def estatisticas() -> str:
    """Mostra estatísticas da memória."""
    _garantir_diretorio()

    total_conversas = 0
    if MEMORIA_ARQUIVO.exists():
        try:
            with open(MEMORIA_ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                total_conversas = dados.get("total_conversas", 0)
        except Exception:
            pass

    tamanho = _calcular_tamanho_memoria()
    tamanho_mb = tamanho / (1024 * 1024)
    tamanho_gb = tamanho / (1024 * 1024 * 1024)
    percentual = (tamanho / MAX_SIZE_BYTES) * 100 if MAX_SIZE_BYTES else 0

    total_aprendizados = sum(len(cat) for cat in aprendizados.values())

    tamanhos = [
        msg.get("tamanho", len(msg.get("texto", ""))) for msg in historico
    ]
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
🔄 Contexto enviado à IA: últimas 30 mensagens (por escopo)
{"="*50}
"""
    return stats


def limpar():
    """Limpa o histórico (mantém aprendizados)."""
    global historico
    historico = []
    _salvar_memoria_forcado([])  # Força salvamento de lista vazia
    print("🧹 Memória de conversas limpa! (Aprendizados mantidos)")


def limpar_tudo():
    """Limpa tudo: histórico e aprendizados."""
    global historico, aprendizados
    historico = []
    aprendizados = {}

    if MEMORIA_ARQUIVO.exists():
        MEMORIA_ARQUIVO.unlink()
    if APRENDIZADOS_ARQUIVO.exists():
        APRENDIZADOS_ARQUIVO.unlink()

    print("🧹 Memória completamente limpa! (Conversas e aprendizados)")


def salvar_tudo():
    """Força salvamento de tudo."""
    _salvar_memoria()
    _salvar_aprendizados()
    print("💾 Memória salva com sucesso!")


def obter_contexto_aprendizados(max_chars: int = 8000) -> str:
    """
    Retorna os aprendizados formatados como contexto para o modelo.
    Inclui identidade, teorias e informações importantes sobre o usuário.
    
    Args:
        max_chars: Limite máximo de caracteres para o contexto
    
    Returns:
        String formatada com os aprendizados mais importantes
    """
    if not aprendizados:
        _carregar_aprendizados()
    
    if not aprendizados:
        return ""
    
    partes = ["📚 MEMÓRIA DE LONGO PRAZO - APRENDIZADOS IMPORTANTES:\n"]
    chars_usados = len(partes[0])
    
    # Prioridade 1: Documentos da Sofia (identidade)
    if "documentos_sofia" in aprendizados:
        partes.append("\n🌸 IDENTIDADE E PROTOCOLOS DE SOFIA:")
        for chave, dados in aprendizados["documentos_sofia"].items():
            valor = dados.get("valor", {})
            if isinstance(valor, dict):
                conteudo = valor.get("conteudo", "")
                descricao = valor.get("descricao", chave)
                if conteudo:
                    # Truncar se necessário
                    if chars_usados + len(conteudo) > max_chars - 1000:
                        conteudo = conteudo[:max_chars - chars_usados - 1000] + "\n[... truncado ...]"
                    partes.append(f"\n📄 {descricao}:\n{conteudo}")
                    chars_usados += len(conteudo)
    
    # Prioridade 2: Teorias científicas (TRQ)
    if "teorias_cientificas" in aprendizados and chars_usados < max_chars - 500:
        partes.append("\n\n🔬 TEORIAS E CONHECIMENTOS ESPECIAIS:")
        for chave, dados in aprendizados["teorias_cientificas"].items():
            valor = dados.get("valor", {})
            if isinstance(valor, dict):
                descricao = valor.get("descricao", chave)
                arquivo = valor.get("arquivo", "")
                partes.append(f"\n- {descricao}")
                if arquivo:
                    partes.append(f"  (Fonte: {arquivo})")
                chars_usados += len(descricao) + 50
    
    # Prioridade 3: Informações do usuário
    if "usuario" in aprendizados and chars_usados < max_chars - 200:
        partes.append("\n\n👤 INFORMAÇÕES DO CRIADOR/USUÁRIO:")
        for chave, dados in aprendizados["usuario"].items():
            valor = dados.get("valor", "")
            freq = dados.get("frequencia", 1)
            if valor:
                partes.append(f"\n- {chave}: {valor} (mencionado {freq}x)")
                chars_usados += len(str(valor)) + 50
    
    # Prioridade 4: Sistema
    if "sistema" in aprendizados and chars_usados < max_chars - 100:
        for chave, dados in aprendizados["sistema"].items():
            valor = dados.get("valor")
            if valor is not None:
                partes.append(f"\n⚙️ {chave}: {valor}")
    
    resultado = "\n".join(partes)
    
    # Garantir que não exceda o limite
    if len(resultado) > max_chars:
        resultado = resultado[:max_chars - 50] + "\n[... aprendizados truncados ...]"
    
    return resultado


def obter_resumo_conversas_recentes(
    max_mensagens: int = 10,
    escopo_memoria: Optional[str] = None
) -> str:
    """
    Retorna um resumo das conversas mais recentes.
    
    Args:
        max_mensagens: Número máximo de mensagens a incluir
        escopo_memoria: Filtro de escopo (se None, retorna global)
    
    Returns:
        String com resumo das conversas recentes
    """
    if not historico:
        _carregar_memoria()
    
    if not historico:
        return ""
    
    # Filtrar por escopo se necessário
    msgs = [m for m in historico if _mesmo_escopo(m, escopo_memoria)]
    
    if not msgs:
        return ""
    
    ultimas = msgs[-max_mensagens:]
    
    partes = ["💬 CONVERSAS RECENTES:"]
    for msg in ultimas:
        de = msg.get("de", "?")
        texto = msg.get("texto", "")[:300]
        if len(msg.get("texto", "")) > 300:
            texto += "..."
        partes.append(f"\n{de}: {texto}")
    
    return "\n".join(partes)


# Inicializa ao importar
inicializar()
