# monitor_visual.py
"""
Monitor Visual TRQ - Exibe estado quântico em tempo real em janela separada.
"""
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Cores ANSI para terminal
class Cores:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    PRETO = "\033[30m"
    VERMELHO = "\033[31m"
    VERDE = "\033[32m"
    AMARELO = "\033[33m"
    AZUL = "\033[34m"
    MAGENTA = "\033[35m"
    CIANO = "\033[36m"
    BRANCO = "\033[37m"
    
    BG_PRETO = "\033[40m"
    BG_AZUL = "\033[44m"
    BG_VERDE = "\033[42m"
    BG_MAGENTA = "\033[45m"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mover_cursor(linha, coluna):
    print(f"\033[{linha};{coluna}H", end="")

def desenhar_barra(valor, max_valor, largura=30, cor=Cores.CIANO):
    """Desenha uma barra de progresso."""
    if max_valor == 0:
        percentual = 0
    else:
        percentual = min(1.0, max(0, valor / max_valor))
    preenchido = int(largura * percentual)
    vazio = largura - preenchido
    barra = f"{cor}{'█' * preenchido}{Cores.DIM}{'░' * vazio}{Cores.RESET}"
    return barra

def desenhar_onda(fase, largura=40):
    """Desenha uma onda senoidal ASCII."""
    import math
    onda = ""
    chars = " ▁▂▃▄▅▆▇█"
    for i in range(largura):
        val = math.sin((i / largura * 4 * math.pi) + fase)
        idx = int((val + 1) / 2 * (len(chars) - 1))
        onda += f"{Cores.CIANO}{chars[idx]}{Cores.RESET}"
    return onda

def carregar_ultimo_estado():
    """Carrega o último estado do arquivo de estado compartilhado."""
    estado_path = Path(__file__).parent / "estado_monitor.json"
    try:
        if estado_path.exists():
            with open(estado_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return None

def carregar_log_trq():
    """Carrega estatísticas do log de execução TRQ."""
    log_path = Path(__file__).parent / "logs_execucao" / "simular_trq_floquet_v2_log.jsonl"
    stats = {"total": 0, "ultima_duracao": 0, "media_duracao": 0}
    try:
        if log_path.exists():
            duracoes = []
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    duracoes.append(entry["duracao_seg"])
            if duracoes:
                stats["total"] = len(duracoes)
                stats["ultima_duracao"] = duracoes[-1]
                stats["media_duracao"] = sum(duracoes) / len(duracoes)
    except:
        pass
    return stats

def exibir_monitor():
    """Loop principal do monitor visual."""
    # Habilitar cores ANSI no Windows
    if os.name == 'nt':
        os.system('color')
        os.system('mode con: cols=80 lines=35')
    
    fase = 0
    ciclo = 0
    
    while True:
        try:
            limpar_tela()
            
            # Cabeçalho
            print(f"{Cores.BG_MAGENTA}{Cores.BRANCO}{Cores.BOLD}")
            print("╔══════════════════════════════════════════════════════════════════════════╗")
            print("║               🧠  SOFIA - MONITOR QUÂNTICO TRQ  🧠                       ║")
            print("╚══════════════════════════════════════════════════════════════════════════╝")
            print(Cores.RESET)
            
            # Timestamp
            agora = datetime.now().strftime("%H:%M:%S")
            print(f"  {Cores.DIM}Atualizado: {agora} │ Ciclo: {ciclo}{Cores.RESET}")
            print()
            
            # Estado atual
            estado = carregar_ultimo_estado()
            
            print(f"  {Cores.BOLD}{Cores.AMARELO}═══ ESTADO SUBITEMOCIONAL ═══{Cores.RESET}")
            print()
            
            if estado:
                # Métricas do estado
                intensidade = estado.get("intensidade", 0.5)
                curvatura = estado.get("curvatura_trq", 0)
                emaranhamento = estado.get("emaranhamento_trq", 0)
                estado_emocional = estado.get("estado", "neutro")
                modo = estado.get("modo", "Local")
                
                print(f"  Estado Emocional: {Cores.CIANO}{estado_emocional.upper()}{Cores.RESET}")
                print(f"  Modo: {Cores.VERDE if modo == 'Local' else Cores.AZUL}{modo}{Cores.RESET}")
                print()
                
                print(f"  Intensidade:    {desenhar_barra(intensidade, 1.0, 30, Cores.VERDE)} {intensidade:.3f}")
                
                # Curvatura pode ser negativa
                curv_normalizado = (curvatura + 1) / 2  # Normalizar de [-1,1] para [0,1]
                cor_curv = Cores.VERMELHO if curvatura < 0 else Cores.VERDE
                print(f"  Curvatura TRQ:  {desenhar_barra(curv_normalizado, 1.0, 30, cor_curv)} {curvatura:+.4f}")
                
                print(f"  Emaranhamento:  {desenhar_barra(emaranhamento, 1.0, 30, Cores.MAGENTA)} {emaranhamento:.4f}")
                
            else:
                print(f"  {Cores.DIM}Aguardando primeira interação...{Cores.RESET}")
            
            print()
            print(f"  {Cores.BOLD}{Cores.AMARELO}═══ ONDA QUÂNTICA ═══{Cores.RESET}")
            print()
            print(f"  {desenhar_onda(fase, 60)}")
            print()
            
            # Estatísticas do simulador
            stats = carregar_log_trq()
            print(f"  {Cores.BOLD}{Cores.AMARELO}═══ SIMULADOR TRQ-FLOQUET v2 ═══{Cores.RESET}")
            print()
            print(f"  Simulações executadas: {Cores.CIANO}{stats['total']}{Cores.RESET}")
            print(f"  Última duração:        {Cores.CIANO}{stats['ultima_duracao']:.2f}s{Cores.RESET}")
            print(f"  Duração média:         {Cores.CIANO}{stats['media_duracao']:.2f}s{Cores.RESET}")
            
            print()
            print(f"  {Cores.BOLD}{Cores.AMARELO}═══ LEGENDA TRQ ═══{Cores.RESET}")
            print()
            print(f"  {Cores.DIM}• Curvatura > 0: Expansão (modo explorativo)")
            print(f"  • Curvatura < 0: Contração (modo focado)")
            print(f"  • Emaranhamento alto: Alta coerência quântica")
            print(f"  • Onda: Visualização da fase quântica{Cores.RESET}")
            
            print()
            print(f"  {Cores.DIM}Pressione Ctrl+C para fechar{Cores.RESET}")
            
            # Atualizar fase da onda
            fase += 0.3
            ciclo += 1
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            limpar_tela()
            print(f"\n  {Cores.AMARELO}Monitor TRQ encerrado.{Cores.RESET}\n")
            break
        except Exception as e:
            print(f"\n  {Cores.VERMELHO}Erro: {e}{Cores.RESET}")
            time.sleep(2)

if __name__ == "__main__":
    exibir_monitor()
