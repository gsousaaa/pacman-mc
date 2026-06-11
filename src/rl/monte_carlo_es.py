import numpy as np
from typing import List, Tuple

def gerar_episodio(
    ambiente,
    estado_inicial: int,
    acao_inicial: int,
    Pi: np.ndarray,
    T: int,
) -> List[Tuple[int, int, float]]:
    """
    Gera um episódio de comprimento fixo T atendendo à condição
    de inícios exploratórios, adaptado para o ambiente do Pac-Man.
    """
    if T < 1:
        raise ValueError("T deve ser >= 1.")

    trajetoria: List[Tuple[int, int, float]] = []

    # O ambiente usa o reset com start_state para os inícios exploratórios
    state = ambiente.reset(start_state=estado_inicial)
    action = acao_inicial

    # Loop do episódio até o limite de tempo T
    for _ in range(T):
        # Executa a ação no ambiente e recebe o retorno
        next_state, reward, done = ambiente.step(action)
        
        trajetoria.append((state, action, reward))
        
        # Se o Ghost capturou o Pac-Man, encerramos a coleta
        if done:
            break
            
        # Atualiza o estado para o próximo turno
        state = next_state
        
        # Seleciona a próxima ação com base nas probabilidades da política
        action = np.random.choice(ambiente.n_actions, p=Pi[state])

    # Preenchimento da trajetória caso tenha terminado antes de T
    while len(trajetoria) < T:
        trajetoria.append((state, action, 0.0))

    return trajetoria


def mc_inicios_exploratorios(
    ambiente,
    gamma: float = 0.9,
    N: int = 10_000,
    T: int = 50,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """
    Monte Carlo com Inícios Exploratórios (ES).
    """
    rng = np.random.default_rng(seed)

    n_estados = ambiente.n_states
    n_acoes = ambiente.n_actions

    Q = np.zeros((n_estados, n_acoes), dtype=float)
    numero_de_visitas = np.zeros((n_estados, n_acoes), dtype=float)
    soma_dos_retornos = np.zeros((n_estados, n_acoes), dtype=float)

    # Política inicial aleatória
    Pi = np.zeros((n_estados, n_acoes), dtype=float)
    Pi[np.arange(n_estados), rng.integers(n_acoes, size=n_estados)] = 1.0

    for k in range(1, N + 1):
        # 1) Inícios exploratórios
        s0 = int(rng.integers(n_estados))
        a0 = int(rng.integers(n_acoes))

        # 2) Gera trajetória
        trajetoria = gerar_episodio(ambiente, s0, a0, Pi, T)

        # 3) Varredura reversa
        g = 0.0
        for t in range(T - 1, -1, -1):
            s_t, a_t, r_t_plus_1 = trajetoria[t]

            g = gamma * g + r_t_plus_1

            soma_dos_retornos[s_t, a_t] += g
            numero_de_visitas[s_t, a_t] += 1

            Q[s_t, a_t] = soma_dos_retornos[s_t, a_t] / numero_de_visitas[s_t, a_t]

            best_a = int(np.argmax(Q[s_t]))
            Pi[s_t] = 0.0 
            Pi[s_t, best_a] = 1.0 

    return Q, Pi, numero_de_visitas, k