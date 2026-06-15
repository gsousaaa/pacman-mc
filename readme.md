# Pacman - MC

[![Repo Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow.svg)]()

Uma implementação personalizada do clássico jogo **Pacman**, desenvolvida como parte de um projeto acadêmico/estudo prático. O projeto busca recriar as mecânicas fundamentais do jogo original (movimentação, labirinto, coleta de pastilhas e comportamento dos fantasmas) aplicando conceitos modernos de programação e arquitetura de software.

---

## Funcionalidades

* **Mecânicas Clássicas:** Controle do Pacman pelo mapa e coleta de pontos.
* **Sistema de Score:** Contagem dinâmica de pontuação conforme pastilhas são devoradas.
* **Fantasmas com IA:** Comportamentos baseados em algoritmos de busca de caminhos (Pathfinding).
* **Interface Gráfica:** Renderização do mapa e dos personagens de forma fluida.

---

## Tecnologias e Ferramentas

O projeto foi construído utilizando as seguintes tecnologias:

* **Linguagem Principal:** Python
* **Biblioteca Gráfica/Engine:** Streamlit
* **Gerenciador de Dependências:** Pip

---

## Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter instalado em sua máquina o Python e o Git.

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/gsousaaa/pacman-mc.git](https://github.com/gsousaaa/pacman-mc.git)
   cd pacman-mc
2. **Instalação**
    ```bash
    pip install -r requirements.txt
    ```
3. **Execução**
    ```bash
    streamlit run src/interface/app.py
    ```