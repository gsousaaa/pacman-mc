import sys
import os

caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(caminho_src)

import numpy as np
from game.maps.default_map import PACMAN_MAP
from game.env.environment import Environment
from rl.monte_carlo_es import mc_inicios_exploratorios

from analytics.metrics_logger import MetricsLogger

DIFFICULTIES = {
    "easy": {
        "N": 5_000,
        "T": 80,
        "gamma": 0.90,
    },
    "medium": {
        "N": 20_000,
        "T": 120,
        "gamma": 0.75,
    },
    "hard": {
        "N": 80_000,
        "T": 200,
        "gamma": 0.50,
    },
}

def train_difficulty(difficulty: str):
    print(f"--- Iniciando treinamento para a dificuldade: {difficulty.upper()} ---")
    config = DIFFICULTIES[difficulty]

    logger = MetricsLogger()

    env = Environment(
        game_map=PACMAN_MAP,
        player_mode="npc"
    )

    Q, Pi, numero_de_visitas, episodios_treinados, recompensa_media, recompensa_total = mc_inicios_exploratorios(
            ambiente=env,
            gamma=config["gamma"],
            N=config["N"],
            T=config["T"],
            seed=42
        )

    base_dir = os.path.dirname(__file__)

    caminho_policy = os.path.join(base_dir, "results", "policies", f"policy_{difficulty}.npy")
    caminho_q_table = os.path.join(base_dir, "results", "q_tables", f"q_table_{difficulty}.npy")
    caminho_visits = os.path.join(base_dir, "results", "visits", f"visits_{difficulty}.npy")

    np.save(caminho_policy, Pi)
    np.save(caminho_q_table, Q)
    np.save(caminho_visits, numero_de_visitas)

    print(f"Treino finalizado: {difficulty}")
    print(f"Episódios treinados: {episodios_treinados}\n")

    logger.log_training(
        difficulty=difficulty,
        episodes=episodios_treinados,
        gamma=config["gamma"],
        max_steps=config["T"],
        avg_reward=recompensa_media,
        total_reward=recompensa_total
    )


def train_all():
    """
    Roda o treinamento em lote para todas as dificuldades.
    """
    train_difficulty("easy")
    train_difficulty("medium")
    train_difficulty("hard")


if __name__ == "__main__":
    train_all()