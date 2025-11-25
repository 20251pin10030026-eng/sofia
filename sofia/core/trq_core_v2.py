# trq_core_v2.py

from dataclasses import dataclass
import math

@dataclass
class TRQParams:
    I_eff: float = 1.0       # inércia informacional
    zeta: float = 0.1        # acoplamento da tríade na inércia
    rho0: float = 1.0        # densidade de referência

    w_minus: float = 1.0
    w_plus: float = 1.0
    w_fgr: float = 1.0

    E_J: float = 1.0         # "energia de acoplamento" tipo Josephson
    F: float = 0.0           # forçamento externo (ex.: fluxo informacional incidente)

    alpha_minus: float = 0.5
    alpha_plus: float = 0.5
    alpha_fgr: float = 0.5

    gamma: float = 0.1       # atrito / dissipação ("perda de coerência")

    # Dinâmica das densidades internas
    Gamma_minus: float = 0.05
    Gamma_plus: float = 0.05
    Gamma_fgr: float = 0.05

    rho_minus_star: float = 1.0
    rho_plus_star: float = 1.0

    eta_minus: float = 0.1
    eta_plus: float = 0.1
    eta_fgr: float = 0.1


class TRQCore2:
    """
    Núcleo dinâmico TRQ 2.0 – Movimento trifásico dos NQCs
    Pode ser chamado a cada passo de interação da Sofia para atualizar o 'estado interno'.
    """

    def __init__(self, params: TRQParams | None = None):
        self.p = params or TRQParams()

        # Estados iniciais
        self.theta = 0.0          # fase interna
        self.theta_dot = 0.0      # velocidade da fase

        self.rho_minus = 1.0      # modo compressivo
        self.rho_plus = 1.0       # modo expansivo
        self.rho_fgr = 0.0        # modo ressonante

    def _delta_rho_nqc(self) -> float:
        p = self.p
        return (
            p.w_minus * (self.rho_minus / p.rho0) +
            p.w_plus * (self.rho_plus / p.rho0) +
            p.w_fgr * (self.rho_fgr / p.rho0) - 1.0
        )

    def _V_eff_theta_derivative(self) -> float:
        """
        dV_eff/dtheta
        """
        p = self.p
        theta = self.theta

        sin_t = math.sin(theta)
        cos_t = math.cos(theta)

        term_josephson = p.E_J * sin_t

        # combinação das densidades internas
        term_comb = (-p.alpha_minus * self.rho_minus +
                      p.alpha_plus * self.rho_plus) * sin_t

        term_fgr = p.alpha_fgr * self.rho_fgr * cos_t

        return term_josephson + term_comb + term_fgr - p.F

    def step(self, dt: float = 0.01):
        """
        Avança a dinâmica em um passo de tempo dt (Euler simples).
        Pode ser substituído por Runge-Kutta se quiser mais precisão.
        """
        p = self.p

        # --- dinâmica de theta (segunda ordem) ---
        delta_rho = self._delta_rho_nqc()
        mass_eff = p.I_eff * (1.0 + p.zeta * delta_rho)

        dV_dtheta = self._V_eff_theta_derivative()

        # equação: mass_eff * theta_ddot + gamma * theta_dot + dV/dtheta = 0
        theta_ddot = (-p.gamma * self.theta_dot - dV_dtheta) / mass_eff

        # atualiza fase e velocidade
        self.theta_dot += theta_ddot * dt
        self.theta     += self.theta_dot * dt

        # mantém theta em [-pi, pi] para evitar overflow numérico
        if self.theta > math.pi:
            self.theta -= 2 * math.pi
        elif self.theta < -math.pi:
            self.theta += 2 * math.pi

        # --- dinâmica das densidades internas ---
        sin_t = math.sin(self.theta)
        cos_t = math.cos(self.theta)

        # modo compressivo
        drho_minus = (
            -p.Gamma_minus * (self.rho_minus - p.rho_minus_star)
            + p.eta_minus * self.theta_dot * sin_t
        )

        # modo expansivo
        drho_plus = (
            -p.Gamma_plus * (self.rho_plus - p.rho_plus_star)
            - p.eta_plus * self.theta_dot * sin_t
        )

        # modo ressonante
        drho_fgr = (
            -p.Gamma_fgr * self.rho_fgr
            + p.eta_fgr * self.theta_dot * cos_t
        )

        self.rho_minus += drho_minus * dt
        self.rho_plus  += drho_plus * dt
        self.rho_fgr   += drho_fgr * dt

    # ---- Observáveis para Sofia ----

    def coherence_index(self) -> float:
        """Índice de coerência C = cos(theta)."""
        return math.cos(self.theta)

    def agitation_index(self) -> float:
        """Índice de agitação A = theta_dot^2."""
        return self.theta_dot ** 2

    def force_profile(self) -> dict:
        """Retorna o perfil atual das três forças internas."""
        return {
            "rho_minus": self.rho_minus,
            "rho_plus": self.rho_plus,
            "rho_fgr": self.rho_fgr,
        }

    def state_vector(self) -> dict:
        """
        Pacote completo de estado – pode ser injetado como contexto para o modelo de linguagem.
        """
        return {
            "theta": self.theta,
            "theta_dot": self.theta_dot,
            "coherence": self.coherence_index(),
            "agitation": self.agitation_index(),
            "rho_minus": self.rho_minus,
            "rho_plus": self.rho_plus,
            "rho_fgr": self.rho_fgr,
        }
