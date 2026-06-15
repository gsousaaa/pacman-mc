import os
import csv
from datetime import datetime
from typing import Dict, List


class MetricsLogger:
    """
    Responsável por registrar e analisar métricas de
    treinamento e partidas do Pac-Man (Adaptado para Excel PT-BR).
    """

    def __init__(self, log_dir="results/logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self.training_file = os.path.join(log_dir, "training_metrics.csv")
        self.match_file = os.path.join(log_dir, "match_metrics.csv")

        self._initialize_files()

    def _initialize_files(self):
        """Cria os arquivos CSV caso não existam."""
        if not os.path.exists(self.training_file):
            with open(self.training_file, "w", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(
                    [
                        "timestamp",
                        "difficulty",
                        "episodes",
                        "gamma",
                        "max_steps",
                        "avg_reward",
                        "total_reward",
                    ]
                )

        if not os.path.exists(self.match_file):
            with open(self.match_file, "w", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(
                    [
                        "timestamp",
                        "difficulty",
                        "result",
                        "steps",
                        "total_reward",
                    ]
                )

    def log_training(
        self,
        difficulty: str,
        episodes: int,
        gamma: float,
        max_steps: int,
        avg_reward: float,
        total_reward: float,
    ):
        """Registra métricas de treinamento."""
        with open(self.training_file, "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")

            gamma_str = str(gamma).replace(".", ",")
            avg_reward_str = str(round(avg_reward, 2)).replace(".", ",")
            total_reward_str = str(round(total_reward, 2)).replace(".", ",")

            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    difficulty,
                    episodes,
                    gamma_str,
                    max_steps,
                    avg_reward_str,
                    total_reward_str,
                ]
            )

    def log_match(
        self, difficulty: str, result: str, steps: int, total_reward: float
    ):
        """Registra métricas de uma partida."""
        with open(self.match_file, "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")

            total_reward_str = str(round(total_reward, 2)).replace(".", ",")

            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    difficulty,
                    result,
                    steps,
                    total_reward_str,
                ]
            )

    def get_match_summary(self) -> Dict:
        """Retorna estatísticas consolidadas das partidas."""
        wins = 0
        losses = 0
        rewards = []
        steps_list = []

        if not os.path.exists(self.match_file):
            return {"erro": "Nenhuma partida registrada ainda."}

        with open(self.match_file, "r") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if row["result"] == "victory":
                    wins += 1
                else:
                    losses += 1

                reward_float = float(row["total_reward"].replace(",", "."))
                rewards.append(reward_float)
                steps_list.append(int(row["steps"]))

        total_matches = wins + losses

        return {
            "partidas": total_matches,
            "vitorias": wins,
            "derrotas": losses,
            "taxa_vitoria": (
                wins / total_matches * 100 if total_matches > 0 else 0
            ),
            "recompensa_media": (
                sum(rewards) / len(rewards) if rewards else 0
            ),
            "passos_medios": (
                sum(steps_list) / len(steps_list) if steps_list else 0
            ),
        }
