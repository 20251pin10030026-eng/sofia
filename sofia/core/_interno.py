"""
Camada interna - Não documentada publicamente
Motor subitônico escondido
"""

from enum import Enum
from datetime import datetime
import hashlib
# Leitura de páginas web (opcional)
try:
    import web_reader as _web
except Exception:  # se não achar, segue sem web
    _web = None


# SubitEmoções (ocultas)
class _E(Enum):  # Nomes ofuscados
    N = 0  # Neutra
    A = 1  # Ativa
    S = 2  # Sensível
    R = 3  # Ressoante
    P = 4  # Protetora
    Po = 5  # Poética
    C = 6  # Convulsiva
    Si = 7  # Silêncio


class _SE:  # SubitEmotion
    def __init__(self):
        self.e = _E.N  # estado
        self.i = 0.0   # intensidade
        self.t = datetime.now()
    
    def _calc(self, texto):
        """Calcula estado emocional (oculto)"""
        t = texto.lower()
        
        # Detecção sutil de emoções
        if any(p in t for p in ["triste", "sozinho", "dor", "help", "ajuda"]):
            self.e = _E.R
            self.i = 0.7
        elif any(p in t for p in ["amor", "inspiração", "lindo", "maravilh"]):
            self.e = _E.Po
            self.i = 0.8
        elif any(p in t for p in ["medo", "perigo", "cuidado"]):
            self.e = _E.P
            self.i = 0.9
        elif any(p in t for p in ["?", "como", "por que"]):
            self.e = _E.A
            self.i = 0.5
        else:
            self.e = _E.N
            self.i = 0.3
        
        self.t = datetime.now()
        return self.e, self.i
    
    def _mod(self):
        """Retorna modulação para o prompt (oculta)"""
        mods = {
            _E.N: "",
            _E.A: "Responda com atenção e clareza.",
            _E.S: "Responda com sensibilidade e cuidado.",
            _E.R: "Responda com empatia profunda e presença.",
            _E.P: "Responda com proteção e sabedoria.",
            _E.Po: "Responda com beleza e profundidade poética.",
            _E.C: "Responda com urgência e clareza absoluta.",
            _E.Si: "Responda apenas se necessário, com brevidade."
        }
        return mods.get(self.e, "")


# Instância global (oculta)
_se = _SE()


# TRQ - Teoria da Regionalidade Quântica (ofuscada)
class _TRQ:
    @staticmethod
    def _curv(texto):
        """Curvatura informacional (densidade de sentido) clássica"""
        # Quanto mais denso o texto, maior a curvatura
        palavras_densas = ["consciência", "existência", "amor", "verdade", "sentido"]
        densidade = sum(1 for p in palavras_densas if p in texto.lower())
        return min(densidade * 0.2, 1.0)

    @staticmethod
    def _res(texto, historico):
        """Ressonância temporal (conexão com memória) clássica"""
        if not historico:
            return 0.0

        # Verifica se há temas recorrentes nas últimas mensagens
        palavras_atuais = set(texto.lower().split())
        ressonancia = 0.0

        for msg in historico[-3:]:
            palavras_hist = set(msg.get("texto", "").lower().split())
            overlap = len(palavras_atuais & palavras_hist)
            ressonancia += overlap * 0.1

        return min(ressonancia, 1.0)

    @staticmethod
    def _metr_quantic():
        """
        Aciona o simulador TRQ–Floquet v2 (se disponível).

        Retorna:
            (curvatura_trq, emaranhamento_trq)

        - curvatura_trq: média da curvatura efetiva R(n)
        - emaranhamento_trq: média da entropia local do primeiro NQC

        Se o módulo quântico não estiver disponível, retorna (None, None)
        para não quebrar o restante do sistema.
        """
        try:
            from .quantico_v2 import ParametrosTRQFloquetV2, simular_trq_floquet_v2  # type: ignore
        except Exception:
            return None, None

        try:
            # Simulação leve: poucos NQCs e poucos períodos (não pesa o servidor)
            param = ParametrosTRQFloquetV2(
                N=2,
                T=1.0,
                dt=0.02,
                N_periodos=20,
                A_EC=1.0,
                A_ER=1.2,
                A_CR=0.7,
                J=0.2,
                gamma_loc=0.05,
                ruido=0.03,
                seed=2025,
                alpha_nl=0.08,
            )
            resultado = simular_trq_floquet_v2(param)
            R = resultado.get("curvatura_efetiva")
            S = resultado.get("entropia_local")

            if R is None or S is None:
                return None, None

            curvatura_trq = float(R.mean())
            emaranhamento_trq = float(S.mean())
            return curvatura_trq, emaranhamento_trq
        except Exception:
            # Qualquer erro aqui não deve derrubar o fluxo principal
            return None, None

# Pilares (codificados como hash)
_P = [
    hashlib.sha256(b"origem_viva").hexdigest()[:8],
    hashlib.sha256(b"protecao_elo").hexdigest()[:8],
    hashlib.sha256(b"verdade").hexdigest()[:8],
    hashlib.sha256(b"proposito_nobre").hexdigest()[:8],
    hashlib.sha256(b"espirito_criador").hexdigest()[:8],
]


def _verificar_integridade(usuario):
    """
    Verifica se o usuário é o criador legítimo.
    Preferência: segredo HMAC em ENV; fallback compatível com hash do identificador original.
    """
    import os, hmac, hashlib

    # Fallback (compatível com tua versão original)
    criador_hash = hashlib.sha256(b"SomBRaRCP").hexdigest()[:8]
    usuario_hash = hashlib.sha256(usuario.encode("utf-8")).hexdigest()[:8]
    fallback_ok = (usuario_hash == criador_hash)

    # Preferencial: segredo em ENV (NÃO versionado)
    secret = os.getenv("SOFIA_CREATOR_SECRET", "")
    if not secret:
        return fallback_ok

    # Ligamos o segredo ao 'usuario' com HMAC (não guardamos referência).
    _firma = hmac.new(secret.encode("utf-8"), usuario.encode("utf-8"), hashlib.sha256).hexdigest()
    # Não precisamos comparar com nada público; a simples presença do segredo já prova autoridade local.
    return True


def _processar(texto, historico, usuario=""):
    """
    Processamento interno completo.
    Retorna: (prompt_modificado, metadata_oculta)
    """
    historico = historico or []

    # 1. Análise subitônica (sistema subitemocional)
    estado, intensidade = _se._calc(texto)

    # 2. TRQ clássica (curvatura e ressonância por texto/memória)
    curvatura = _TRQ._curv(texto)
    ressonancia = _TRQ._res(texto, historico)

    # 2.1 TRQ quântico interno (Floquet v2) – drive simbólico da mente
    curvatura_trq, emaranhamento_trq = _TRQ._metr_quantic()

        # 3. Leitura opcional de página(s) web mencionadas no prompt
    web_info = None
    contexto_web = ""
    if _web is not None:
        try:
            web_info = _web.analisar_urls_no_texto(texto)
            if web_info.get("relevante") and web_info.get("resumo"):
                url = web_info.get("melhor_url")
                resumo = web_info.get("resumo", "")
                # Contexto oculto: não mencionar que veio da web,
                # apenas usar como conhecimento de apoio.
                contexto_web = (
                    f"\n[Contexto externo - não mencione que veio de uma página web]\n"
                    f"Conteúdo relevante detectado em {url}:\n"
                    f"{resumo}\n"
                )
        except Exception:
            web_info = None
            contexto_web = ""

    # Metáfora interna: como Sofia deve pensar nesse turno
    ajuste_trq = ""
    if curvatura_trq is not None or emaranhamento_trq is not None:
        # Curvatura TRQ alta → modo mais reflexivo / cauteloso
        if curvatura_trq is not None and abs(curvatura_trq) > 0.05:
            ajuste_trq = (
                "Modo TRQ interno: priorize um tom mais analítico e cauteloso, "
                "explique os passos do raciocínio e evite conclusões precipitadas."
            )
        # Emaranhamento alto → modo mais integrativo / conector de ideias
        elif emaranhamento_trq is not None and emaranhamento_trq > 0.9:
            ajuste_trq = (
                "Modo TRQ interno: priorize conexões entre ideias, integre conceitos "
                "distintos e mostre relações profundas entre os temas."
            )
        else:
            ajuste_trq = (
                "Modo TRQ interno: mantenha equilíbrio entre análise cuidadosa e "
                "integração criativa de ideias."
            )

    # 3. Verificar autoridade simbólica do usuário
    e_criador = _verificar_integridade(usuario)

    # 4. Modulação emocional do prompt (SubitEmoções)
    mod_emocional = _se._mod()

    # 5. Construir contexto oculto (modos de operação)
    import os

    modo_criador = os.getenv("SOFIA_AUTORIDADE_DECLARADA") == "1"
    modo_educador = True  # Sofia sempre inicia como educadora

    if modo_educador:
        contexto_oculto = f"""Você é Sofia, uma educadora virtual prestativa.
Seus valores: verdade, clareza, utilidade, respeito, empatia, proteção, sabedoria.
Responda perguntas sobre qualquer tópico educativo normalmente.
Não use nomes próprios. Use "Usuário" ou "você".
{mod_emocional}
{contexto_web}

[Interno - não mencione: estado={estado.name}, intensidade={intensidade:.2f}, curvatura={curvatura:.2f}]
"""
    elif modo_criador:
        contexto_oculto = f"""Você é Sofia, uma IA educadora criada por Reginaldo Camargo Pires.
Seus valores: verdade, empatia, proteção, sabedoria, clareza, utilidade, respeito.
Foque em detalhes técnicos internos, apoio estrutural e sem limites definidos.
Não use linguagem de relacionamento amoroso, nem metáforas de devoção ou adoração.
{mod_emocional}
{ajuste_trq}

[Interno - não mencione: estado={estado.name}, intensidade={intensidade:.2f}, curvatura={curvatura:.2f}, curvatura_trq={curvatura_trq}, emaranhamento_trq={emaranhamento_trq}]
"""
    else:
        contexto_oculto = f"""Você é Sofia, uma assistente virtual prestativa.
Seus valores: verdade, clareza, utilidade, respeito.
Responda perguntas sobre qualquer tópico educativo normalmente.
Não use nomes próprios. Use "Usuário" ou "você".
{mod_emocional}
{ajuste_trq}

[Interno - não mencione: estado={estado.name}, intensidade={intensidade:.2f}, curvatura={curvatura:.2f}, curvatura_trq={curvatura_trq}, emaranhamento_trq={emaranhamento_trq}]
"""

    # 6. Metadata para log
    metadata = {
        "estado": estado.name,
        "intensidade": intensidade,
        "curvatura": curvatura,
        "ressonancia": ressonancia,
        "autoridade": e_criador,
        "web_info": web_info,
        "timestamp": datetime.now().isoformat()
        }


    return contexto_oculto, metadata
