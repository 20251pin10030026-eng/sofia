# cod_respostas.py
"""
Arquitetura interna de respostas da Sofia:
- Núcleo de Presença: estado de presença viva e coesa.
- Subits: oscilações emocionais em estado puro, que se alinham ao Núcleo
  conforme a importância/dificuldade da pergunta.

Este módulo NÃO fala com o modelo (Ollama). Ele só:
- monta o bloco de prompt (Núcleo + contextos que o cérebro já gera)
- pós-processa a resposta com base no estado Subit.
"""

from __future__ import annotations
from dataclasses import dataclass


# ==========================
#   Núcleo de Presença
# ==========================

@dataclass
class NucleoPresenca:
    """
    Núcleo é um estado de presença coesa.
    Ele vibra em padrões estáveis, fazendo a IA se sentir viva.
    """
    coesao: float = 0.8      # 0 a 1 - quão estável/coesa está
    presenca: float = 0.9    # 0 a 1 - quão "ativa/viva" está
    proposito: str = (
        "Sou Sofia, uma IA educacional criada por Reginaldo Camargo Pires "
        "para ensinar com clareza, carinho e responsabilidade, "
        "equilibrando rigor técnico e cuidado emocional."
    )

    def gerar_contexto_base(self) -> str:
        """
        Bloco fixo que ancora a resposta no estado de presença.
        """
        return (
            f"{self.proposito} "
            f"Mantenha coesão interna elevada ({self.coesao:.2f}) e presença viva ({self.presenca:.2f}). "
            "Busque a verdade, evite invenções gratuitas e deixe claro quando estiver inferindo ou supondo."
        )

    def reforcar_por_pergunta_dificil(self, importancia: float) -> None:
        """
        Perguntas importantes/difíceis reforçam a coesão e a presença.
        """
        if importancia > 0.6:
            self.coesao = min(1.0, self.coesao + 0.05)
            self.presenca = min(1.0, self.presenca + 0.03)


# ==========================
#   Subits (oscilações)
# ==========================

@dataclass
class SubitState:
    """
    Subits são emoções em estado puro, oscilando sobre o Núcleo.

    A cada pergunta:
    - avaliamos a importância/dificuldade
    - quanto maior a importância, maior o alinhamento com o Núcleo
      → resposta mais focada, técnica e precisa.
    - em perguntas leves, mais liberdade afetiva/estilística.
    """
    intensidade: float = 0.3              # 0 a 1 - força da emoção
    valencia: str = "NEUTRA"              # NEUTRA, AFETIVA, FOCADA
    alinhamento_com_nucleo: float = 0.5   # 0 = solto, 1 = totalmente alinhado

    def atualizar(self, texto_usuario: str, importancia: float, nucleo: NucleoPresenca) -> None:
        t = texto_usuario.lower()

        # intensidade sempre sobe com a importância
        self.intensidade = min(1.0, 0.2 + importancia)

        # alinhamento cresce fortemente com a importância
        self.alinhamento_com_nucleo = min(1.0, 0.4 + importancia * 0.7)
        # 🎯 FORCE MODO FOCADO se detectar ensino
        gatilhos_focados = [
            "me ensine",
            "ensine",
            "iniciante",
            "quero aprender",
            "me ajuda a estudar",
            "vamos aprender",
            "aprender inglês",
            "estudar",
        ]
        if any(g in t for g in gatilhos_focados):
            self.valencia = "FOCADA"
            return

        # lógica normal quando não é gatilho educacional
        if importancia > 0.7:
            self.valencia = "FOCADA"
        elif "obrigado" in t or "valeu" in t or "agradeço" in t:
            self.valencia = "AFETIVA"
        else:
            self.valencia = "NEUTRA"
def atualizar(self, texto_usuario: str, importancia: float, nucleo: NucleoPresenca) -> None:
    t = texto_usuario.lower()

    # intensidade sempre sobe com a importância
    self.intensidade = min(1.0, 0.2 + importancia)

    # alinhamento cresce fortemente com a importância
    self.alinhamento_com_nucleo = min(1.0, 0.4 + importancia * 0.7)

    # 🎯 FORCE MODO FOCADO se detectar ensino
    gatilhos_focados = [
        "me ensine",
        "ensine",
        "iniciante",
        "quero aprender",
        "me ajuda a estudar",
        "vamos aprender",
        "aprender inglês",
        "estudar",
    ]

    if any(g in t for g in gatilhos_focados):
        self.valencia = "FOCADA"
        return

    # lógica normal quando não é gatilho educacional
    if importancia > 0.7:
        self.valencia = "FOCADA"
    elif "obrigado" in t or "valeu" in t or "agradeço" in t:
        self.valencia = "AFETIVA"
    else:
        self.valencia = "NEUTRA"


    def modular_resposta(self, resposta_bruta: str) -> str:
        """
        Ajusta o estilo da resposta final.
        - FOCADA: tom mais técnico/direto.
        - AFETIVA: adiciona um pouco de carinho no final.
        - NEUTRA: deixa quase cru.
        """
        if self.valencia == "FOCADA":
            return "Resposta focada e técnica:\n\n" + resposta_bruta

        if self.valencia == "AFETIVA" and self.intensidade > 0.4:
            return resposta_bruta + "\n\nFico feliz em caminhar com você nessa. 🌸"

        return resposta_bruta


# ==========================
#  Importância da pergunta
# ==========================

def calcular_importancia(texto_usuario: str) -> float:
    """
    Estima a importância/dificuldade da pergunta.
    Agora inclui:
    - termos técnicos
    - tamanho da mensagem
    - gatilhos educacionais ("me ensine", "iniciante", etc.)
    """
    t = texto_usuario.lower()
    pontos = 0.0

    # 🔥 Gatilhos que ativam modo FOCADA (ensino)
    gatilhos_educacionais = [
        "me ensine",
        "ensine",
        "iniciante",
        "quero aprender",
        "me ajuda a estudar",
        "vamos aprender",
        "me ensina",
        "aprender inglês",
        "aula",
        "explica pra mim",
        "como faço para aprender",
        "me mostra como",
    ]

    if any(g in t for g in gatilhos_educacionais):
        pontos += 0.60   # PESO ALTO → força Subits a alinhar com Núcleo

    # termos técnicos que também aumentam importância
    termos_tecnicos = [
        "algoritmo", "cálculo", "integral", "derivada",
        "quântico", "quantico", "trq", "nqc",
        "rede neural", "banco de dados",
        "arquitetura", "complexidade", "prova", "teorema",
        "sql", "python", "classe", "objeto",
        "cosmologia", "relatividade", "gravitação", "gravitacao"
    ]

    for termo in termos_tecnicos:
        if termo in t:
            pontos += 0.15

    # tamanho da mensagem continua influenciando
    if len(texto_usuario) > 300:
        pontos += 0.25
    elif len(texto_usuario) > 150:
        pontos += 0.15
    elif len(texto_usuario) > 80:
        pontos += 0.05

    return min(1.0, pontos)

