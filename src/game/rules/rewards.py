"""
Recompensas por: 
Andar, bater em parede, 
se aproximar do pacman, se afastar do pacman e capturar o pacman, respectivamente.
"""
REWARD_STEP = -1
REWARD_WALL = -5
REWARD_APPROACH = 5
REWARD_MOVE_AWAY = -5
REWARD_CAPTURE = 100