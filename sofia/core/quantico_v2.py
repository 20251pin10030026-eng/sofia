"""
quantico_v2.py

Versão avançada do laboratório TRQ–Floquet de NQCs.

Inclui:
- Estado inicial vibrante (superposição |E> + |C> + |R>)
- Múltiplos drives gravitacionais (E<->C, E<->R, C<->R) com frequências diferentes
- Ruído quântico controlado (kick hermitiano fraco)
- Não-linearidade efetiva: H_local é reescalado a cada período em função da curvatura R(n)
- Cálculo da entropia local de um NQC (emaranhamento com o resto)

Uso sugerido:

    from quantico_v2 import ParametrosTRQFloquetV2, simular_trq_floquet_v2

    param = ParametrosTRQFloquetV2(N=3, N_periodos=80)
    resultado = simular_trq_floquet_v2(param)

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
from trq_core_v2 import TRQCore2, TRQParams

trq_params = TRQParams()
trq_core = TRQCore2(trq_params)

# Exemplo de uso em algum ponto do fluxo da Sofia:
def atualizar_estado_trq():
    # avança o campo interno
    trq_core.step(dt=0.05)
    estado_trq = trq_core.state_vector()
    return estado_trq

# ======================================================================
# Parâmetros da simulação
# ======================================================================

@dataclass
class ParametrosTRQFloquetV2:
    """
    Parâmetros do modelo TRQ–Floquet v2 de NQCs.

    N           -> número de NQCs (qutrits). Dimensão = 3**N (cuidado ao subir muito).
    T           -> período base da modulação gravitacional.
    dt          -> passo de tempo (dt << T).
    N_periodos  -> número de períodos de Floquet a simular.

    A_EC        -> amplitude do drive nas transições E<->C.
    A_ER        -> amplitude do drive nas transições E<->R.
    A_CR        -> amplitude do drive nas transições C<->R (entra com sinal invertido).

    J           -> acoplamento entre NQCs vizinhos.
    gamma_loc   -> escala de energia local (H_local).

    ruido       -> intensidade do ruído quântico hermitiano.
    seed        -> semente de aleatoriedade (para reprodutibilidade).
    alpha_nl    -> força da não-linearidade efetiva (escala H_local por (1 + alpha_nl*R_n)).
    """
    N: int = 3
    T: float = 1.0
    dt: float = 0.01
    N_periodos: int = 80

    A_EC: float = 1.0
    A_ER: float = 1.3
    A_CR: float = 0.8

    J: float = 0.3
    gamma_loc: float = 0.05

    ruido: float = 0.05
    seed: int = 1234
    alpha_nl: float = 0.10


# ======================================================================
# Funções auxiliares
# ======================================================================

def _importar_dependencias():
    """
    Importa NumPy e QuTiP apenas quando necessário.

    Evita quebrar o projeto se QuTiP não estiver instalado.
    """
    try:
        import numpy as _np
        from qutip import (
            basis as _basis,
            qeye as _qeye,
            tensor as _tensor,
            Qobj as _Qobj,
            expect as _expect,
            ptrace as _ptrace,
            entropy_vn as _entropy_vn,
        )
    except ImportError as e:
        raise ImportError(
            "O módulo 'quantico_v2' requer NumPy e QuTiP instalados para rodar as simulações.\n"
            "Instale com: pip install numpy qutip"
        ) from e

    return _np, _basis, _qeye, _tensor, _Qobj, _expect, _ptrace, _entropy_vn


def _op_site(op_local, site: int, N: int, qeye_func):
    """
    Cria operador que atua como 'op_local' em um site específico (NQC)
    e como identidade nos demais.
    """
    from qutip import tensor

    ops = []
    for i in range(N):
        if i == site:
            ops.append(op_local)
        else:
            ops.append(qeye_func(3))
    return tensor(ops)


def _op_couple_sites(op_local_i, op_local_j, i: int, j: int, N: int, qeye_func):
    """
    Cria operador de acoplamento entre dois sites i e j
    usando op_local_i em i e op_local_j em j.
    """
    from qutip import tensor

    ops = []
    for k in range(N):
        if k == i:
            ops.append(op_local_i)
        elif k == j:
            ops.append(op_local_j)
        else:
            ops.append(qeye_func(3))
    return tensor(ops)


def _construir_hamiltonianos_v2(param: ParametrosTRQFloquetV2):
    """
    Constrói:

    - estados base locais |E>, |C>, |R>
    - operadores de transição entre E, C, R
    - H_local
    - H_c (acoplamento)
    - operadores de observáveis globais: I_op, R_op, a_op, C_op
    - estado inicial vibrante psi0
    - operador de ruído hermitiano H_noise
    """

    (
        np,
        basis,
        qeye,
        tensor,
        Qobj,
        expect,
        ptrace,
        entropy_vn,
    ) = _importar_dependencias()

    # -------------------------
    # Base local: qutrit de NQC
    # |E> = |0>, |C> = |1>, |R> = |2>
    # -------------------------
    ket_E = basis(3, 0)
    ket_C = basis(3, 1)
    ket_R = basis(3, 2)

    proj_E = ket_E * ket_E.dag()
    proj_C = ket_C * ket_C.dag()
    proj_R = ket_R * ket_R.dag()

    # Operadores de transição locais entre os três níveis
    op_EC = ket_E * ket_C.dag()   # |E><C|
    op_CE = ket_C * ket_E.dag()   # |C><E|

    op_ER = ket_E * ket_R.dag()   # |E><R|
    op_RE = ket_R * ket_E.dag()   # |R><E|

    op_CR = ket_C * ket_R.dag()   # |C><R|
    op_RC = ket_R * ket_C.dag()   # |R><C|

    N = param.N
    gamma_local = param.gamma_loc
    J = param.J

    # --------------------------------
    # H_local: dinâmica interna de cada NQC
    # H_local = soma_i gamma_local (|E><E| + |C><C| - 2|R><R|)
    # --------------------------------
    H_local = 0 * _op_site(proj_E, 0, N, qeye)

    for i in range(N):
        H_i = gamma_local * (
            _op_site(proj_E, i, N, qeye) +
            _op_site(proj_C, i, N, qeye) -
            2 * _op_site(proj_R, i, N, qeye)
        )
        H_local = H_local + H_i

    # --------------------------------
    # H_c: acoplamento entre NQCs vizinhos
    # H_c = J * soma_i (|E_i><C_i| ⊗ |C_{i+1}><E_{i+1}| + h.c.)
    # --------------------------------
    H_c = 0 * _op_site(proj_E, 0, N, qeye)

    for i in range(N - 1):
        H_forward = _op_couple_sites(op_EC, op_CE, i, i + 1, N, qeye)
        H_backward = _op_couple_sites(op_CE, op_EC, i, i + 1, N, qeye)
        H_c = H_c + J * (H_forward + H_backward)

    # --------------------------------
    # Observáveis globais (TRQ toy-model)
    # I_op  -> densidade de informação fora do estado de ressonância
    # R_op  -> "curvatura" como diferença entre compressão e expansão
    # a_op  -> fator de "expansão" (ocupação de |E>)
    # C_op  -> compressão (ocupação de |C>)
    # --------------------------------
    I_op = 0 * _op_site(proj_E, 0, N, qeye)
    R_op = 0 * _op_site(proj_E, 0, N, qeye)
    a_op = 0 * _op_site(proj_E, 0, N, qeye)
    C_op = 0 * _op_site(proj_E, 0, N, qeye)

    for i in range(N):
        proj_E_i = _op_site(proj_E, i, N, qeye)
        proj_C_i = _op_site(proj_C, i, N, qeye)

        I_op = I_op + (proj_E_i + proj_C_i)
        R_op = R_op + (proj_C_i - proj_E_i)
        a_op = a_op + proj_E_i
        C_op = C_op + proj_C_i

    # --------------------------------
    # ESTADO INICIAL VIBRANTE
    # |vib> = (|E> + |C> + |R>).unit()
    # psi0 = |vib> ⊗ ... ⊗ |vib|
    # --------------------------------
    ket_vib = (ket_E + ket_C + ket_R).unit()
    psi0 = ket_vib
    for _ in range(1, N):
        psi0 = tensor(psi0, ket_vib)

    # --------------------------------
    # RUÍDO QUÂNTICO H_noise (hermitiano)
    # --------------------------------
        dim = 3 ** N
    rng = np.random.default_rng(param.seed)
    M = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))

    # Ruído hermitiano com a MESMA estrutura de subsistemas de H_local
    H_noise = Qobj(
        0.5 * (M + M.conj().T),   # hermitiano
        dims=H_local.dims         # [[3,3,3],[3,3,3]] para N=3
    )


    base_local = {
        "ket_E": ket_E,
        "ket_C": ket_C,
        "ket_R": ket_R,
        "proj_E": proj_E,
        "proj_C": proj_C,
        "proj_R": proj_R,
        "op_EC": op_EC,
        "op_CE": op_CE,
        "op_ER": op_ER,
        "op_RE": op_RE,
        "op_CR": op_CR,
        "op_RC": op_RC,
    }

    observaveis = {
        "I_op": I_op,
        "R_op": R_op,
        "a_op": a_op,
        "C_op": C_op,
    }

    return {
        "np": np,
        "basis": basis,
        "qeye": qeye,
        "tensor": tensor,
        "Qobj": Qobj,
        "expect": expect,
        "ptrace": ptrace,
        "entropy_vn": entropy_vn,
        "base_local": base_local,
        "H_local": H_local,
        "H_c": H_c,
        "psi0": psi0,
        "observaveis": observaveis,
        "H_noise": H_noise,
    }


def _time_evolution_operator(H_t, dt: float):
    """
    U(dt) = exp(-i H_t dt)
    """
    return (-1j * H_t * dt).expm()


# ======================================================================
# Função principal de simulação v2
# ======================================================================

def simular_trq_floquet_v2(param: ParametrosTRQFloquetV2 | None = None) -> Dict[str, Any]:
    """
    Roda o algoritmo TRQ–Floquet v2 de NQCs com QuTiP.

    Retorna um dicionário com:
        - 'densidade_informacao'   : array com I(n) em cada período
        - 'curvatura_efetiva'      : array com R(n)
        - 'fator_expansao_macro'   : array com a(n)
        - 'compressao_microscopica': array com C(n)
        - 'entropia_local'         : array com S_local(n) (entropia de von Neumann do NQC 0)
        - 'estado_final'           : estado final |Ψ>
        - 'parametros'             : cópia dos parâmetros usados
    """
    if param is None:
        param = ParametrosTRQFloquetV2()

    (
        np,
        basis,
        qeye,
        tensor,
        Qobj,
        expect,
        ptrace,
        entropy_vn,
    ) = _importar_dependencias()

    N = param.N
    T = param.T
    dt = param.dt
    N_periodos = param.N_periodos

    # Frequências base e harmônicas (cordas em tons diferentes)
    Omega_base = 2 * np.pi / T
    Omega_EC = Omega_base
    Omega_ER = 2.0 * Omega_base
    Omega_CR = np.sqrt(2.0) * Omega_base

    ctx = _construir_hamiltonianos_v2(param)
    H_local_base = ctx["H_local"]
    H_c = ctx["H_c"]
    psi = ctx["psi0"]
    I_op = ctx["observaveis"]["I_op"]
    R_op = ctx["observaveis"]["R_op"]
    a_op = ctx["observaveis"]["a_op"]
    C_op = ctx["observaveis"]["C_op"]

    base = ctx["base_local"]
    proj_E = base["proj_E"]
    proj_C = base["proj_C"]
    proj_R = base["proj_R"]
    op_EC = base["op_EC"]
    op_CE = base["op_CE"]
    op_ER = base["op_ER"]
    op_RE = base["op_RE"]
    op_CR = base["op_CR"]
    op_RC = base["op_RC"]

    H_noise = ctx["H_noise"]

    # Fator de não-linearidade: H_local_eff = (1 + alpha_nl * R_n) * H_local_base
    alpha_nl = param.alpha_nl
    fator_nl = 1.0
    H_local_eff = H_local_base * fator_nl

    # Históricos
    historico_I = []
    historico_R = []
    historico_a = []
    historico_C = []
    historico_S_local = []

    for n in range(N_periodos):
        t_inicio = n * T
        t = t_inicio

        # Evolução dentro de um período T (ciclo de Floquet)
        while t < t_inicio + T - 1e-12:
            # Drives com múltiplas frequências (cordas tonais)
            A_EC_t = param.A_EC * np.cos(Omega_EC * t)
            A_ER_t = param.A_ER * np.cos(Omega_ER * t)
            A_CR_t = param.A_CR * np.cos(Omega_CR * t)

            # H_drive(t): mistura E<->C, E<->R, C<->R em cada NQC
            H_drive_t = 0 * _op_site(proj_E, 0, N, qeye)
            for i in range(N):
                G_EC = _op_site(op_EC + op_CE, i, N, qeye)
                G_ER = _op_site(op_ER + op_RE, i, N, qeye)
                G_CR = _op_site(op_CR + op_RC, i, N, qeye)

                G_i = A_EC_t * G_EC + A_ER_t * G_ER - A_CR_t * G_CR
                H_drive_t = H_drive_t + G_i

            # Ruído quântico hermitiano (kick fraco)
            if param.ruido > 0.0:
                xi = np.random.normal()
                H_t = H_local_eff + H_c + H_drive_t + param.ruido * xi * H_noise
            else:
                H_t = H_local_eff + H_c + H_drive_t

            U_dt = _time_evolution_operator(H_t, dt)
            psi = U_dt * psi

            t += dt

        # Medidas ao final do período n
        I_n = expect(I_op, psi)
        R_n = expect(R_op, psi)
        a_n = expect(a_op, psi)
        C_n = expect(C_op, psi)

        # Entropia local do NQC 0 (emaranhamento com o resto)
        rho_0 = ptrace(psi, 0)
        S_local_n = entropy_vn(rho_0, base=2)  # em bits

        historico_I.append(I_n)
        historico_R.append(R_n)
        historico_a.append(a_n)
        historico_C.append(C_n)
        historico_S_local.append(S_local_n)

        # Atualizar fator não-linear para o próximo período
        fator_nl = 1.0 + alpha_nl * float(R_n)
        H_local_eff = H_local_base * fator_nl

    return {
        "densidade_informacao": np.array(historico_I),
        "curvatura_efetiva": np.array(historico_R),
        "fator_expansao_macro": np.array(historico_a),
        "compressao_microscopica": np.array(historico_C),
        "entropia_local": np.array(historico_S_local),
        "estado_final": psi,
        "parametros": param,
    }
