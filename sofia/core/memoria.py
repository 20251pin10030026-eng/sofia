"""
Memória persistente de conversas com aprendizado
Sistema de memória de 5GB para armazenar e aprender com conversas.

Agora com suporte a ESCOPOS DE MEMÓRIA:
- cada sessão/usuário pode ter sua própria bolha de memória,
  via contexto['escopo_memoria'].
"""

import json
import os
import math
import re
import unicodedata
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


_STOPWORDS_PT = {
    "a", "o", "os", "as", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
    "por", "para", "com", "sem", "sobre", "entre", "até", "após",
    "e", "ou", "mas", "porque", "que", "se", "como", "quando", "onde",
    "eu", "tu", "você", "vc", "ele", "ela", "eles", "elas", "nós", "nos", "vocês",
    "me", "te", "se", "lhe", "lhes", "minha", "meu", "seu", "sua", "nossa", "nosso",
    "isso", "isto", "aquilo", "aqui", "ali", "lá",
}


def _normalizar_texto_basico(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def _tokenizar(texto: str) -> set[str]:
    texto = _normalizar_texto_basico(texto)
    if not texto:
        return set()
    # mantém letras/números e alguns separadores comuns; remove o resto
    texto = re.sub(r"[^a-z0-9\s\-_/]", " ", texto)
    partes = re.split(r"\s+", texto)
    tokens = {p for p in partes if p and p not in _STOPWORDS_PT and len(p) >= 3}
    return tokens


def _split_paragrafos(texto: str, max_partes: int = 20) -> List[str]:
    if not texto:
        return []
    # Quebra por marcadores comuns de PDFs e por linhas em branco
    bruto = texto.replace("\r\n", "\n")
    bruto = bruto.replace("\r", "\n")
    bruto = re.sub(r"\n{3,}", "\n\n", bruto)
    partes: List[str] = []
    # primeiro, quebra por páginas para reduzir ruído
    for bloco in re.split(r"(?=\=\=\=\s*PÁGINA\s*\d+\s*\=\=\=)", bruto, flags=re.IGNORECASE):
        bloco = bloco.strip()
        if not bloco:
            continue
        for p in bloco.split("\n\n"):
            p = p.strip()
            if len(p) < 40:
                continue
            partes.append(p)
            if len(partes) >= max_partes:
                return partes
    return partes[:max_partes]


def _score_chunk(
    consulta_tokens: set[str],
    chunk_texto: str,
    peso_base: float,
    metadata: Dict[str, Any] | None,
) -> float:
    if not chunk_texto:
        return -1.0
    chunk_tokens = _tokenizar(chunk_texto)
    if not chunk_tokens:
        return -1.0

    comuns = len(chunk_tokens & consulta_tokens)
    if comuns == 0:
        return -1.0

    # Similaridade leve (evita vetores/embeddings): overlap normalizado + peso_base
    sim = comuns / (math.sqrt(len(chunk_tokens)) + 1e-6)

    # Penaliza custo cognitivo: textos longos tendem a entrar menos
    custo = min(1.0, len(chunk_texto) / 2000.0)

    bonus = 0.0
    if metadata and isinstance(metadata, dict):
        estado = str(metadata.get("estado") or "").strip().lower()
        ajuste = str(metadata.get("ajuste_trq") or "").strip().lower()

        # Se o estado/ajuste aparecem no chunk, aumenta ressonância
        if estado and estado in _normalizar_texto_basico(chunk_texto):
            bonus += 0.15
        if ajuste and ajuste in _normalizar_texto_basico(chunk_texto):
            bonus += 0.10

        # Se estamos em modo TRQ (curvatura_trq presente) e o chunk fala de TRQ/NQC
        if metadata.get("curvatura_trq") is not None:
            nt = _normalizar_texto_basico(chunk_texto)
            if "trq" in nt or "nqc" in nt or "regionalidade" in nt:
                bonus += 0.20

        # Se há alta ressonância no estado atual, aumenta levemente seletividade
        try:
            res_atual = float(metadata.get("ressonancia") or 0.0)
            bonus += max(0.0, min(0.25, res_atual * 0.05))
        except Exception:
            pass

    return (sim + peso_base + bonus) - (0.35 * custo)


def _carregar_conversas_tail_disco(
    max_mensagens: int = 250,
    max_bytes_arquivo: int = 5 * 1024 * 1024,
) -> List[Dict[str, Any]]:
    """Lê o conversas.json do disco e retorna somente o tail.

    Salvaguarda: se o arquivo estiver muito grande, retorna vazio para evitar custo.
    """
    try:
        if not MEMORIA_ARQUIVO.exists():
            return []
        try:
            if MEMORIA_ARQUIVO.stat().st_size > max_bytes_arquivo:
                return []
        except Exception:
            pass

        with open(MEMORIA_ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)
        conversas = dados.get("conversas", [])
        if not isinstance(conversas, list) or not conversas:
            return []
        return [c for c in conversas[-max_mensagens:] if isinstance(c, dict)]
    except Exception:
        return []


def _ler_ultimas_linhas_tail(path: Path, max_linhas: int = 200, max_bytes: int = 65536) -> List[str]:
    if not path.exists():
        return []
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            tamanho = f.tell()
            offset = min(tamanho, max_bytes)
            if offset <= 0:
                return []
            f.seek(-offset, 2)
            dados = f.read(offset)
        texto = dados.decode("utf-8", errors="ignore")
        linhas = texto.splitlines()
        return linhas[-max_linhas:]
    except Exception:
        return []


def obter_contexto_memoria_seletiva(
    texto_atual: str,
    metadata: Dict[str, Any] | None = None,
    escopo_memoria: Optional[str] = None,
    max_chars: int = 2500,
    top_k: int = 8,
    fontes_permitidas: Optional[set[str] | List[str]] = None,
    pesos: Optional[Dict[str, float]] = None,
    debug: bool = False,
) -> str:
    """
    Recuperação seletiva de memória (TSMP/GMAR-TRQ) para uso no modo LOCAL.

    Objetivo: evitar "varrer" e despejar toda a memória no prompt. Em vez disso,
    ativa apenas NQCs/trechos relevantes ao texto atual, ao estado interno e à
    ressonância temporal, com custo cognitivo mínimo.

    Observação: função adicionada sem alterar o comportamento do cloud.
    """
    texto_atual = (texto_atual or "").strip()
    if not texto_atual:
        return ""

    # Tokens da consulta incluem texto + alguns sinais do estado interno
    consulta_enriquecida = texto_atual
    if metadata and isinstance(metadata, dict):
        sinais = []
        for k in ("estado", "ajuste_trq"):
            v = metadata.get(k)
            if v:
                sinais.append(str(v))
        consulta_enriquecida = f"{texto_atual} " + " ".join(sinais)

    consulta_tokens = _tokenizar(consulta_enriquecida)
    if not consulta_tokens:
        return ""

    consulta_norm = _normalizar_texto_basico(consulta_enriquecida)
    porteiro_duro = bool(metadata and metadata.get("modo_trq_duro") is True)
    if metadata and isinstance(metadata, dict) and bool(metadata.get("tsmp_debug") is True):
        debug = True

    # Normalizar política de fontes
    if fontes_permitidas is not None and not isinstance(fontes_permitidas, set):
        try:
            fontes_permitidas = set(str(x) for x in fontes_permitidas)  # type: ignore[arg-type]
        except Exception:
            fontes_permitidas = None

    def _fonte_permitida(fonte: str) -> bool:
        if fontes_permitidas is None:
            return True
        if "*" in fontes_permitidas:
            return True

        # mapeamento de aliases de profile → fontes reais
        if fonte == "subitemotions":
            return "subitemotions" in fontes_permitidas
        if fonte.startswith("conversa/"):
            return fonte in fontes_permitidas
        if fonte.startswith("aprendizados/"):
            # exemplos: aprendizados/teorias_cientificas/..., aprendizados/documentos_sofia/...
            partes = fonte.split("/", 2)
            if len(partes) >= 2:
                categoria = partes[1]
                return categoria in fontes_permitidas
        return False

    pesos = pesos if isinstance(pesos, dict) else {}

    def _fator_peso(fonte: str) -> float:
        # pesos são fatores multiplicativos aplicados ao peso_base
        try:
            if fonte == "subitemotions":
                return float(pesos.get("subitemotions", 1.0))
            if fonte.startswith("conversa/"):
                return float(pesos.get("conversa", 1.0))
            if fonte.startswith("aprendizados/teorias_cientificas"):
                return float(pesos.get("teorias", 1.0))
        except Exception:
            return 1.0
        return 1.0
    consulta_trq = any(
        k in consulta_norm
        for k in (
            "trq",
            "nqc",
            "regionalidade",
            "curvatura",
            "resson",
            "hubble",
            "rgfq",
        )
    )
    # No modo laboratório, tratamos como domínio TRQ por decisão de orquestração.
    if porteiro_duro:
        consulta_trq = True
        top_k = min(top_k, 4)
        max_chars = min(max_chars, 1400)

    candidatos: List[Dict[str, Any]] = []

    # 1) Aprendizados (longo prazo) — sem despejar tudo; quebra em trechos
    if not aprendizados:
        _carregar_aprendizados()

    if isinstance(aprendizados, dict) and aprendizados:
        for categoria, itens in aprendizados.items():
            if not isinstance(itens, dict):
                continue

            # pesos base por categoria
            if porteiro_duro:
                # Laboratório TRQ: teoria + estado interno dominam; evita ruído episódico/identidade longa
                if categoria == "teorias_cientificas":
                    peso_cat = 0.98
                elif categoria == "documentos_sofia":
                    peso_cat = 0.45
                elif categoria == "usuario":
                    peso_cat = 0.20
                else:
                    peso_cat = 0.18
            else:
                if categoria == "documentos_sofia":
                    peso_cat = 0.78 if consulta_trq else 0.70
                elif categoria == "teorias_cientificas":
                    peso_cat = 0.88 if consulta_trq else 0.60
                elif categoria == "usuario":
                    peso_cat = 0.35 if consulta_trq else 0.45
                else:
                    peso_cat = 0.25 if consulta_trq else 0.35

            for chave, dados in itens.items():
                if not isinstance(dados, dict):
                    continue
                valor = dados.get("valor")

                # formato de documento (com conteudo)
                if isinstance(valor, dict) and isinstance(valor.get("conteudo"), str):
                    conteudo = valor.get("conteudo", "")
                    for p in _split_paragrafos(conteudo, max_partes=14):
                        # Se a consulta é TRQ, prioriza parágrafos com TRQ/NQC e afins
                        if consulta_trq:
                            pn = _normalizar_texto_basico(p)
                            if not any(k in pn for k in ("trq", "nqc", "regionalidade", "curvatura", "hubble")):
                                # ainda entra como candidato, mas com peso menor
                                peso_local = max(0.10, peso_cat - 0.35)
                            else:
                                peso_local = peso_cat
                        else:
                            peso_local = peso_cat
                        candidatos.append(
                            {
                                "fonte": f"aprendizados/{categoria}/{chave}",
                                "texto": p,
                                "peso_base": peso_local,
                            }
                        )
                    continue

                # formato simples (valor string/número)
                if valor is not None:
                    candidatos.append(
                        {
                            "fonte": f"aprendizados/{categoria}/{chave}",
                            "texto": f"{chave}: {valor}",
                            "peso_base": peso_cat,
                        }
                    )

    # 2) Conversas no DISCO (conversas.json) — desativado no laboratório TRQ
    if not porteiro_duro:
        max_disk_msgs = int(os.getenv("SOFIA_TSMP_MAX_DISK_MSGS", "260"))
        max_disk_bytes = int(os.getenv("SOFIA_TSMP_MAX_DISK_BYTES", str(5 * 1024 * 1024)))
        for msg in _carregar_conversas_tail_disco(max_mensagens=max_disk_msgs, max_bytes_arquivo=max_disk_bytes):
            if not _mesmo_escopo(msg, escopo_memoria):
                continue
            de = msg.get("de", "?")
            txt = msg.get("texto", "")
            if not txt:
                continue
            if not _fonte_permitida("conversa/arquivo"):
                continue
            candidatos.append(
                {
                    "fonte": "conversa/arquivo",
                    "texto": f"{de}: {txt}",
                    "peso_base": 0.42 if consulta_trq else 0.50,
                }
            )

    # 3) Conversas recentes em RAM — desativado no laboratório TRQ
    if not porteiro_duro:
        if not historico:
            _carregar_memoria()

        if isinstance(historico, list) and historico:
            msgs = [m for m in historico if isinstance(m, dict) and _mesmo_escopo(m, escopo_memoria)]
            pool = msgs[:-10] if len(msgs) > 10 else []
            # varre no máximo 120 mensagens (mais recentes primeiro)
            for msg in reversed(pool[-120:]):
                de = msg.get("de", "?")
                txt = msg.get("texto", "")
                if not txt:
                    continue
                if not _fonte_permitida("conversa/recente"):
                    continue
                candidatos.append(
                    {
                        "fonte": "conversa/recente",
                        "texto": f"{de}: {txt}",
                        "peso_base": 0.35 if consulta_trq else 0.55,
                    }
                )

    # 4) Subitemotions (tail) — usa só as últimas linhas do arquivo
    log_path = Path(__file__).resolve().parents[1] / ".sofia_internal" / "subitemotions.log"
    if _fonte_permitida("subitemotions"):
        ler_subitemotions = True
    else:
        ler_subitemotions = False

    if ler_subitemotions:
        for linha in _ler_ultimas_linhas_tail(log_path, max_linhas=120, max_bytes=65536):
            try:
                registro = json.loads(linha.strip())
            except Exception:
                continue

            if not isinstance(registro, dict):
                continue

            estado = registro.get("estado")
            entrada = str(registro.get("input") or "")
            resson = registro.get("ressonancia")

            trecho = entrada
            if len(trecho) > 180:
                trecho = trecho[:180] + "..."

            base = 0.35
            try:
                base += max(0.0, min(0.35, float(resson or 0.0) * 0.10))
            except Exception:
                pass

            candidatos.append(
                {
                    "fonte": "subitemotions",
                    "texto": f"estado={estado} ress={resson} entrada=\"{trecho}\"",
                    "peso_base": base,
                }
            )

    # Pontuar e selecionar
    pontuados: List[tuple[float, Dict[str, Any]]] = []
    for c in candidatos:
        t = str(c.get("texto") or "")
        fonte_c = str(c.get("fonte") or "")
        if fonte_c and not _fonte_permitida(fonte_c):
            continue

        peso = float(c.get("peso_base") or 0.0)
        peso *= _fator_peso(fonte_c)
        s = _score_chunk(consulta_tokens, t, peso, metadata)

        # No laboratório TRQ, o estado interno pode ser útil mesmo sem overlap textual.
        if porteiro_duro and s <= 0 and fonte_c == "subitemotions":
            try:
                # base mínima + bônus pela ressonância registrada
                res = float((t.split("ress=")[-1].split()[0]).strip().replace('"', ""))  # best-effort
            except Exception:
                res = 0.0
            s = 0.15 + max(0.0, min(0.10, res * 0.02))

        if porteiro_duro:
            if fonte_c.startswith("aprendizados/teorias_cientificas"):
                s += 0.25
            if fonte_c == "subitemotions":
                s += 0.15

        if consulta_trq:
            tn = _normalizar_texto_basico(t)
            if not any(k in tn for k in ("trq", "nqc", "regionalidade", "curvatura", "hubble", "rgfq")):
                s -= 0.18
        if s > 0:
            pontuados.append((s, c))

    if not pontuados:
        return ""

    pontuados.sort(key=lambda x: x[0], reverse=True)

    partes: List[str] = ["📌 MEMÓRIA SELETIVA (TSMP/GMAR-TRQ):"]
    chars = len(partes[0])
    usados = 0
    vistos: set[str] = set()

    for score, c in pontuados:
        if usados >= top_k or chars >= max_chars:
            break

        fonte = str(c.get("fonte") or "memoria")
        texto = str(c.get("texto") or "").strip()
        if not texto:
            continue

        # dedup leve
        chave_dedup = _normalizar_texto_basico(texto)[:200]
        if chave_dedup in vistos:
            continue
        vistos.add(chave_dedup)

        # normaliza whitespace e reduz tamanho do snippet
        snippet = re.sub(r"\s+", " ", texto)
        limite_snippet = 360 if consulta_trq else 460
        if len(snippet) > limite_snippet:
            snippet = snippet[:limite_snippet] + "..."

        if debug:
            linha = f"- {fonte} (score={score:.3f}): {snippet}"
        else:
            linha = f"- {fonte}: {snippet}"
        if chars + len(linha) + 1 > max_chars:
            continue

        partes.append(linha)
        chars += len(linha) + 1
        usados += 1

    if len(partes) == 1:
        return ""

    return "\n".join(partes)


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
    max_mensagens: int = 10,
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
        trecho = msg.get("texto", "")[:200]  # Reduzido de 400 para 200
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


def obter_contexto_subitemotions(max_registros: int = 10, max_chars: int = 3000) -> str:
    """
    Retorna o histórico recente de subitemotions.log como contexto.
    Inclui estados emocionais, intensidade, curvatura TRQ e ressonância.
    
    Args:
        max_registros: Número máximo de registros a incluir
        max_chars: Limite máximo de caracteres
    
    Returns:
        String formatada com o histórico de subitemotions
    """
    log_path = Path(__file__).resolve().parents[1] / ".sofia_internal" / "subitemotions.log"
    
    if not log_path.exists():
        return ""
    
    try:
        # Ler todas as linhas do log
        with open(log_path, "r", encoding="utf-8") as f:
            linhas = f.readlines()
        
        if not linhas:
            return ""
        
        # Pegar as últimas N linhas
        ultimas = linhas[-max_registros:]
        
        partes = ["🧠 HISTÓRICO DE ESTADOS SUBITEMOCIONAIS RECENTES:"]
        
        for linha in ultimas:
            try:
                registro = json.loads(linha.strip())
                estado = registro.get("estado", "N")
                intensidade = registro.get("intensidade", 0)
                curvatura = registro.get("curvatura", 0)
                curvatura_trq = registro.get("curvatura_trq")
                emaranhamento = registro.get("emaranhamento_trq")
                ressonancia = registro.get("ressonancia", 0)
                timestamp = registro.get("timestamp", "")[:16]  # Só data e hora
                entrada = registro.get("input", "")[:50]
                
                # Mapear estados para nomes legíveis
                nomes_estados = {
                    "N": "Neutra", "A": "Ativa", "S": "Sensível",
                    "R": "Ressoante", "P": "Protetora", "Po": "Poética",
                    "C": "Convulsiva", "Si": "Silêncio"
                }
                nome_estado = nomes_estados.get(estado, estado)
                
                linha_formatada = f"\n[{timestamp}] {nome_estado}(int={intensidade:.2f})"
                if curvatura_trq is not None:
                    linha_formatada += f" TRQ_curv={curvatura_trq:.4f}"
                if emaranhamento is not None:
                    linha_formatada += f" TRQ_emaranh={emaranhamento:.4f}"
                linha_formatada += f" ress={ressonancia:.2f} → \"{entrada}...\""
                
                partes.append(linha_formatada)
            except (json.JSONDecodeError, KeyError):
                continue
        
        resultado = "\n".join(partes)
        
        if len(resultado) > max_chars:
            resultado = resultado[:max_chars - 50] + "\n[... truncado ...]"
        
        return resultado
    except Exception as e:
        print(f"⚠️ Erro ao ler subitemotions.log: {e}")
        return ""


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
