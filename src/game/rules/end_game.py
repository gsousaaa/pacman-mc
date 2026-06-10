from game.entities.position import Position
"""
Regra para o fim do jogo, acaba quando o ghost captura o pacman
"""
def is_capture(player_position: Position, ghost_position: Position) -> bool: 
    return player_position == ghost_position   