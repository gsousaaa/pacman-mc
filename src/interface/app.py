import sys
import os
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random

# Adiciona a pasta 'src' ao path para permitir a importação do logger
caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if caminho_src not in sys.path:
    sys.path.append(caminho_src)

from analytics.metrics_logger import MetricsLogger

logger = MetricsLogger()

st.set_page_config(page_title="Pac-Man Labirinto Clássico", layout="centered")
st_autorefresh(interval=200, key="game_loop")

LARGURA = 19
ALTURA = 11

def gerar_mapa_aleatorio(altura, largura):
    """
    Gera um labirinto autêntico de Pac-Man usando Busca em Profundidade (DFS).
    Garante caminhos estreitos de 1 bloco e sem áreas abertas estilo 'caverna'.
    """
    mapa = [[1 for _ in range(largura)] for _ in range(altura)]
    
    pilha = []
    visitado = set()
    
    inicio = (1, 1)
    pilha.append(inicio)
    visitado.add(inicio)
    mapa[1][1] = 2 
    
    while pilha:
        cx, cy = pilha[-1]
        vizinhos = []
        
        direcoes = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        
        for dx, dy in direcoes:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < altura - 1 and 0 < ny < largura - 1:
                if (nx, ny) not in visitado:
                    vizinhos.append((nx, ny, dx, dy))
                    
        if vizinhos:
            nx, ny, dx, dy = random.choice(vizinhos)
            
            mapa[cx + dx // 2][cy + dy // 2] = 2
            mapa[nx][ny] = 2
            
            visitado.add((nx, ny))
            pilha.append((nx, ny))
        else:
            pilha.pop()
            
    for i in range(2, altura - 2):
        for j in range(2, largura - 2):
            if mapa[i][j] == 1 and random.random() < 0.15:
                if (mapa[i-1][j] == 2 and mapa[i+1][j] == 2) or (mapa[i][j-1] == 2 and mapa[i][j+1] == 2):
                    mapa[i][j] = 2

    mapa[1][1] = 2
    return mapa

MAPA_PADRAO = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

if "mapa" not in st.session_state:
    st.session_state.mapa = gerar_mapa_aleatorio(ALTURA, LARGURA)
    st.session_state.pacman_pos = [1, 1]
    st.session_state.fantasma_pos = [5, 13]
    st.session_state.score = 0
    st.session_state.modo = "Manual"
    st.session_state.passos = 0
    st.session_state.game_over_registrado = False

def mover_agente(pos, direcao):
    nova_pos = pos[:]
    if direcao == "Cima":    nova_pos[0] -= 1
    elif direcao == "Baixo":  nova_pos[0] += 1
    elif direcao == "Esquerda": nova_pos[1] -= 1
    elif direcao == "Direita":  nova_pos[1] += 1
    
    if 0 <= nova_pos[0] < len(st.session_state.mapa) and 0 <= nova_pos[1] < len(st.session_state.mapa[0]):
        if st.session_state.mapa[nova_pos[0]][nova_pos[1]] != 1:
            return nova_pos
    return pos

def lógica_ia_monte_carlo():
    movimentos_possiveis = ["Cima", "Baixo", "Esquerda", "Direita"]
    return random.choice(movimentos_possiveis)

with st.sidebar:
    st.header("Configurações")
    
    if st.button("Gerar Mapa Aleatório", type="secondary"):
        st.session_state.mapa = gerar_mapa_aleatorio(ALTURA, LARGURA)
        st.session_state.pacman_pos = [1, 1]
        st.session_state.fantasma_pos = [ALTURA-2, LARGURA-2]
        st.session_state.score = 0
        st.session_state.passos = 0
        st.session_state.game_over_registrado = False
        st.rerun()

    st.markdown("---")
    modo_selecionado = st.radio("Modo de Jogo:", ("Manual", "IA (Monte Carlo)"))
    st.session_state.modo = modo_selecionado
    
    st.markdown("---")
    st.write("**Controles Manuais:**")
    
    col_up, _ = st.columns(2)
    col_left, col_down, col_right = st.columns(3)
    
    with col_up:
        if st.button("🔼 Cima", key="btn_cima"): st.session_state.direcao_manual = "Cima"
    with col_left:
        if st.button("◀️ Esq", key="btn_esq"): st.session_state.direcao_manual = "Esquerda"
    with col_down:
        if st.button("🔽 Baixo", key="btn_baixo"): st.session_state.direcao_manual = "Baixo"
    with col_right:
        if st.button("▶️ Dir", key="btn_dir"): st.session_state.direcao_manual = "Direita"

    if st.button("🔄 Reiniciar Padrão", type="primary"):
        st.session_state.mapa = [row[:] for row in MAPA_PADRAO]
        st.session_state.pacman_pos = [1, 1]
        st.session_state.fantasma_pos = [5, 13]
        st.session_state.score = 0
        st.session_state.passos = 0
        st.session_state.game_over_registrado = False
        st.rerun()

# Só movimenta e conta passos se o jogo não tiver acabado
if st.session_state.pacman_pos != st.session_state.fantasma_pos:
    st.session_state.passos += 1  # Conta os passos da rodada
    
    if st.session_state.modo == "IA (Monte Carlo)":
        direcao_ia = lógica_ia_monte_carlo()
        st.session_state.pacman_pos = mover_agente(st.session_state.pacman_pos, direcao_ia)
    else:
        if "direcao_manual" in st.session_state:
            st.session_state.pacman_pos = mover_agente(st.session_state.pacman_pos, st.session_state.direcao_manual)
            del st.session_state.direcao_manual

    direcao_fantasma = random.choice(["Cima", "Baixo", "Esquerda", "Direita"])
    st.session_state.fantasma_pos = mover_agente(st.session_state.fantasma_pos, direcao_fantasma)

    px, py = st.session_state.pacman_pos
    if st.session_state.mapa[px][py] == 2:
        st.session_state.mapa[px][py] = 0
        st.session_state.score += 10

st.title("Pac-Man - Interface Jogável")
st.metric(label="Placar (Score)", value=st.session_state.score)

grid_html = """
<table style='border-collapse: collapse; background-color: black; margin: auto; border: 0px solid #1919A6 !important; border-radius: 10px;'>
"""

for i, linha in enumerate(st.session_state.mapa):
    grid_html += "<tr>"
    for j, celula in enumerate(linha):
        grid_html += "<td style='border: 0px solid #1919A6 !important; width: 35px; height: 35px; text-align: center; vertical-align: middle; font-size: 24px; padding: 0;'>"
        
        if [i, j] == st.session_state.pacman_pos:
            grid_html += "🟡"
        elif [i, j] == st.session_state.fantasma_pos:
            grid_html += "👻"
        elif celula == 1:
            grid_html += "🟦"
        elif celula == 2:
            grid_html += "🍬"
        else:
            grid_html += "" 
            
        grid_html += "</td>"
    grid_html += "</tr>"

grid_html += "</table>"

st.markdown(grid_html, unsafe_allow_html=True)

if st.session_state.pacman_pos == st.session_state.fantasma_pos:
    st.error("💥 Fim de Jogo! O Fantasma te pegou!")
    
    if not st.session_state.game_over_registrado:
        dificuldade_jogada = "manual_play" if st.session_state.modo == "Manual" else "ia_play"
        
        # Salva no CSV usando a classe MetricsLogger
        logger.log_match(
            difficulty=dificuldade_jogada,
            result="defeat", 
            steps=st.session_state.passos,
            total_reward=st.session_state.score
        )
        
        # Bloqueia para não salvar o mesmo log infinitamente a cada 200ms
        st.session_state.game_over_registrado = True
        st.success("📊 Partida registrada nos logs com sucesso!")
# ==========================================

js_code = """
<script>
    // Conecta as teclas do teclado físico aos botões da interface do Streamlit
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

st.iframe(src=js_code)