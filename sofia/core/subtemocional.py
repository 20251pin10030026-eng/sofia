"""
subtemocional.py
Sistema Subtemocional Avançado da Sofia
---------------------------------------

Responsável por gerar um estado emocional (SubitState)
que será utilizado pelo cérebro principal para modular
a resposta final.

Este módulo NÃO conversa diretamente com o modelo.
Ele só calcula emoção, intensidade, alinhamento
e aplica modulações estilísticas.
"""

from __future__ import annotations
from dataclasses import dataclass


# -----------------------------------------------------
#  Núcleo Simplificado – base emocional estável
# -----------------------------------------------------

@dataclass
class NucleoEmocional:
    """
    Núcleo emocional estável — influencia o alinhamento dos subits.
    """
    estabilidade: float = 0.85
    suavidade: float = 0.75
    foco: float = 0.70

    def contexto(self) -> str:
        return (
            f"Estado emocional estável (estabilidade={self.estabilidade:.2f}, "
            f"suavidade={self.suavidade:.2f}, foco={self.foco:.2f}). "
        )


# -----------------------------------------------------
#  Subits – estado emocional dinâmico
# -----------------------------------------------------

@dataclass
class SubtemocionalState:
    """
    Representa a emoção ativa da Sofia.
    """

    tipo: str = "NEUTRO"           # NEUTRO | CALOROSO | ANALITICO
    intensidade: float = 0.3       # 0 a 1
    alinhamento: float = 0.5       # 0 a 1

    def atualizar(self, mensagem: str, importancia: float, nucleo: NucleoEmocional):
        """
        Atualiza o estado emocional com base no texto e importância.
        """

        t = mensagem.lower()

        # intensidade sempre sobe proporcional à importância
        self.intensidade = min(1.0, 0.2 + importancia)

        # alinhamento cres­ce em sincronia com o núcleo
        self.alinhamento = min(1.0, nucleo.foco * 0.5 + importancia * 0.5)

        # ------------------------------
        #    Gatilhos emocionais
        # ------------------------------

        if any(x in t for x in ["obrigado", "valeu", "carinho", "gentileza"]):
            self.tipo = "CALOROSO"
            return

        if importancia > 0.65:
            self.tipo = "ANALITICO"
            return

        self.tipo = "NEUTRO"

    def modular(self, resposta: str) -> str:
        """
        Ajusta o estilo da resposta final.
        """

        if self.tipo == "ANALITICO":
            return (
                "🔎 Resposta analítica:\n"
                + resposta
            )

        if self.tipo == "CALOROSO":
            return (
                resposta
                + "\n\n🌸 Estou aqui com você, caminhando passo a passo."
            )

        return resposta


# -----------------------------------------------------
#  Função pública principal deste módulo
# -----------------------------------------------------

def processar_subtemocional(mensagem: str, importancia: float, resposta_bruta: str) -> str:
    """
    Pipeline completo:
    - cria núcleo
    - cria subestado
    - atualiza subestado
    - aplica modulação
    - retorna resposta final modulada
    """

    nucleo = NucleoEmocional()
    sub = SubtemocionalState()

    sub.atualizar(mensagem, importancia, nucleo)
    resposta_modulada = sub.modular(resposta_bruta)

    return resposta_modulada
