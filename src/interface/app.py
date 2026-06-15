import sys
import os

import numpy as np
import streamlit as st
from streamlit_autorefresh import st_autorefresh

caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if caminho_src not in sys.path:
    sys.path.append(caminho_src)

from game.maps.default_map import PACMAN_MAP
from game.env.environment import Environment
from game.env.action import Action
from analytics.metrics_logger import MetricsLogger


logger = MetricsLogger()

st.set_page_config(page_title="Pac-Man Monte Carlo", layout="centered")

st_autorefresh(interval=200, key="game_loop")


DIFFICULTIES = {
    "easy": {
        "label": "Easy",
        "episodes": 1_000,
        "policy_file": "policy_easy.npy",
    },
    "medium": {
        "label": "Medium",
        "episodes": 10_000,
        "policy_file": "policy_medium.npy",
    },
    "hard": {
        "label": "Hard",
        "episodes": 50_000,
        "policy_file": "policy_hard.npy",
    },
}


def get_policy_path(difficulty: str) -> str:
    """
    Mesmo padrão usado no train.py:
    src/rl/results/policies/policy_<difficulty>.npy
    """
    base_dir = caminho_src

    return os.path.join(
        base_dir,
        "rl",
        "results",
        "policies",
        DIFFICULTIES[difficulty]["policy_file"],
    )


def load_policy(difficulty: str):
    policy_path = get_policy_path(difficulty)

    if not os.path.exists(policy_path):
        return None

    return np.load(policy_path)


def create_env():
    """
    Interface usa player_mode="human",
    porque o usuário controla o Pac-Man.
    """
    return Environment(
        game_map=PACMAN_MAP,
        player_mode="human",
    )


def reset_game(difficulty: str):
    policy = load_policy(difficulty)

    st.session_state.env = create_env()
    st.session_state.env.reset()

    st.session_state.policy = policy
    st.session_state.difficulty = difficulty
    st.session_state.game_over_registrado = False
    st.session_state.last_reward = 0
    st.session_state.last_ghost_action = None


def get_action_name(action: int) -> str:
    if action == Action.UP:
        return "Cima"
    if action == Action.DOWN:
        return "Baixo"
    if action == Action.LEFT:
        return "Esquerda"
    if action == Action.RIGHT:
        return "Direita"
    if action == Action.STAY:
        return "Parado"

    return "Desconhecida"


def render_grid(env):
    data = env.get_render_data()

    game_map = data["map"]
    player = data["player"]
    ghost = data["ghost"]

    player_pos = [player.position.row, player.position.col]
    ghost_pos = [ghost.position.row, ghost.position.col]

    grid_html = """
    <table style='border-collapse: collapse; background-color: black; margin: auto; border: 0px solid #1919A6 !important; border-radius: 10px;'>
    """

    for row in range(data["height"]):
        grid_html += "<tr>"

        for col in range(data["width"]):
            cell = game_map[row][col]

            grid_html += """
            <td style='border: 0px solid #1919A6 !important; width: 35px; height: 35px; text-align: center; vertical-align: middle; font-size: 24px; padding: 0;'>
            """

            current_pos = [row, col]

            if current_pos == player_pos and current_pos == ghost_pos:
                grid_html += "💥"
            elif current_pos == player_pos:
                grid_html += "🟡"
            elif current_pos == ghost_pos:
                grid_html += "👻"
            elif cell == "#":
                grid_html += "🟦"
            elif cell == ".":
                grid_html += "🍬"
            else:
                grid_html += ""

            grid_html += "</td>"

        grid_html += "</tr>"

    grid_html += "</table>"

    st.markdown(grid_html, unsafe_allow_html=True)


def move_ghost():
    env = st.session_state.env
    policy = st.session_state.policy

    if policy is None:
        return

    if env.done:
        return

    state = env.encode_state()

    ghost_action = int(np.argmax(policy[state]))

    next_state, reward, done = env.step(ghost_action)

    st.session_state.last_reward = reward
    st.session_state.last_ghost_action = ghost_action


def move_player(action: int):
    env = st.session_state.env

    if env.done:
        return

    env.move_player(action)


if "difficulty" not in st.session_state:
    reset_game("easy")


st.title("Pac-Man - Ghost com Monte Carlo")

with st.sidebar:
    st.header("Configurações")

    selected_difficulty = st.radio(
        "Dificuldade:",
        options=["easy", "medium", "hard"],
        format_func=lambda value: DIFFICULTIES[value]["label"],
        index=["easy", "medium", "hard"].index(st.session_state.difficulty),
    )

    if selected_difficulty != st.session_state.difficulty:
        reset_game(selected_difficulty)
        st.rerun()

    st.write(
        f"Ghost treinado com **{DIFFICULTIES[selected_difficulty]['episodes']} episódios**."
    )

    policy_path = get_policy_path(selected_difficulty)

    if st.session_state.policy is None:
        st.error("Política não encontrada.")
        st.code(policy_path)
        st.warning("Rode o train.py antes de jogar nessa dificuldade.")
    else:
        st.success("Política carregada com sucesso.")

    st.markdown("---")

    st.write("**Controles do Pac-Man:**")

    col_up, _ = st.columns(2)
    col_left, col_down, col_right = st.columns(3)

    with col_up:
        if st.button("🔼 Cima", key="btn_cima"):
            move_player(Action.UP)
            move_ghost()

    with col_left:
        if st.button("◀️ Esq", key="btn_esq"):
            move_player(Action.LEFT)
            move_ghost()

    with col_down:
        if st.button("🔽 Baixo", key="btn_baixo"):
            move_player(Action.DOWN)
            move_ghost()

    with col_right:
        if st.button("▶️ Dir", key="btn_dir"):
            move_player(Action.RIGHT)
            move_ghost()

    st.markdown("---")

    if st.button("🔄 Reiniciar", type="primary"):
        reset_game(st.session_state.difficulty)
        st.rerun()


env = st.session_state.env
data = env.get_render_data()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Score Pac-Man", data.get("player_score", 0))

with col2:
    st.metric("Passos", data["steps"])

with col3:
    st.metric("Reward Ghost", data["total_reward"])

st.write(f"**Dificuldade:** {DIFFICULTIES[st.session_state.difficulty]['label']}")

if st.session_state.last_ghost_action is not None:
    st.write(
        f"Última ação do Ghost: **{get_action_name(st.session_state.last_ghost_action)}** | "
        f"Última recompensa: **{st.session_state.last_reward}**"
    )

render_grid(env)


if data["done"]:
    if data.get("player_won") is True:
        st.success("🏆 Parabéns! Você venceu!")
        result = "win"

    elif data.get("player_won") is False:
        st.error("💥 Fim de jogo! Você foi capturado!")
        result = "defeat"

    else:
        st.warning("Fim de jogo.")
        result = "unknown"

    if not st.session_state.game_over_registrado:
        logger.log_match(
            difficulty=st.session_state.difficulty,
            result=result,
            steps=data["steps"],
            total_reward=data.get("player_score", 0),
        )

        st.session_state.game_over_registrado = True
        st.info("📊 Partida registrada nos logs.")


js_code = """
<script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        let btn;
        if (e.key === 'ArrowUp') {
            btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Cima'));
        } else if (e.key === 'ArrowDown') {
            btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Baixo'));
        } else if (e.key === 'ArrowLeft') {
            btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Esq'));
        } else if (e.key === 'ArrowRight') {
            btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Dir'));
        }
        if (btn) {
            btn.click();
        }
    });
</script>
"""

st.components.v1.html(js_code, height=0)