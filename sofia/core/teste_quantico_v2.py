"""
teste_quantico_v2.py

Script de teste para o módulo quantico_v2.py (TRQ–Floquet v2 de NQCs).

- Roda uma simulação com parâmetros avançados (múltiplos drives, ruído, não-linearidade)
- Mostra um resumo numérico dos resultados
- Gera gráficos das curvas TRQ (I, R, a, C) e da entropia local S_local(n)
"""

from __future__ import annotations

from quantico_v2 import ParametrosTRQFloquetV2, simular_trq_floquet_v2


def imprimir_resumo(resultado):
    import numpy as np

    I = resultado["densidade_informacao"]
    R = resultado["curvatura_efetiva"]
    a = resultado["fator_expansao_macro"]
    C = resultado["compressao_microscopica"]
    S = resultado["entropia_local"]

    def stats(nome, serie):
        return (
            f"{nome}: "
            f"min={np.min(serie): .4f}, "
            f"max={np.max(serie): .4f}, "
            f"final={serie[-1]: .4f}"
        )

    print("\n===== RESUMO NUMÉRICO v2 =====")
    print(stats("Densidade de informação (I)", I))
    print(stats("Curvatura efetiva       (R)", R))
    print(stats("Expansão macro          (a)", a))
    print(stats("Compressão micro        (C)", C))
    print(stats("Entropia local NQC0    (S)", S))
    print("================================\n")


def plotar_resultados(resultado):
    """
    Plota as séries I, R, a, C e S_local ao longo dos períodos.
    Só roda se matplotlib estiver instalado.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não está instalado. Pulei a etapa de gráficos.")
        return

    I = resultado["densidade_informacao"]
    R = resultado["curvatura_efetiva"]
    a = resultado["fator_expansao_macro"]
    C = resultado["compressao_microscopica"]
    S = resultado["entropia_local"]

    x = range(1, len(I) + 1)

    # Gráfico principal TRQ
    plt.figure(figsize=(10, 6))
    plt.plot(x, I, label="Densidade de informação I(n)")
    plt.plot(x, R, label="Curvatura efetiva R(n)")
    plt.plot(x, a, label="Expansão macro a(n)")
    plt.plot(x, C, label="Compressão micro C(n)")
    plt.xlabel("Período de Floquet (n)")
    plt.ylabel("Valor esperado")
    plt.title("TRQ–Floquet v2 dos NQCs (I, R, a, C)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Gráfico da entropia local
    plt.figure(figsize=(8, 5))
    plt.plot(x, S, label="Entropia local S_local(n) – NQC 0")
    plt.xlabel("Período de Floquet (n)")
    plt.ylabel("Entropia de von Neumann (bits)")
    plt.title("Emaranhamento local do primeiro NQC (TRQ–Floquet v2)")
    plt.grid(True)
    plt.tight_layout()

    plt.show()


def main():
    # 1. Definir parâmetros da simulação v2
    param = ParametrosTRQFloquetV2(
        N=3,           # número de NQCs (3 já dá dinâmica rica; 4 começa a pesar)
        T=1.0,
        dt=0.01,
        N_periodos=80,
        A_EC=1.0,
        A_ER=1.3,
        A_CR=0.8,
        J=0.3,
        gamma_loc=0.05,
        ruido=0.05,
        seed=1234,
        alpha_nl=0.10,
    )

    print("=== SIMULAÇÃO TRQ–FLOQUET v2 DE NQCs ===")
    print(f"N = {param.N}")
    print(f"T = {param.T}, dt = {param.dt}, períodos = {param.N_periodos}")
    print(f"A_EC = {param.A_EC}, A_ER = {param.A_ER}, A_CR = {param.A_CR}")
    print(f"J = {param.J}, gamma_loc = {param.gamma_loc}")
    print(f"ruído = {param.ruido}, alpha_nl = {param.alpha_nl}")

    # 2. Rodar simulação
    try:
        resultado = simular_trq_floquet_v2(param)
    except ImportError as e:
        print("\n[ERRO] Falta dependência para rodar a simulação quântica v2:")
        print(e)
        print("Instale com: pip install numpy qutip matplotlib")
        return

    # 3. Imprimir resumo dos resultados
    imprimir_resumo(resultado)

    # 4. Tentar plotar
    plotar_resultados(resultado)

    print("Simulação v2 concluída.")


if __name__ == "__main__":
    main()
