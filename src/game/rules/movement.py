from game.env.action import Action
from game.entities.position import Position

def get_next_position(position: Position, action: int) -> Position:
    if action == Action.UP:
        return Position(position.row - 1, position.col)

    if action == Action.DOWN:
        return Position(position.row + 1, position.col)

    if action == Action.LEFT:
        return Position(position.row, position.col - 1)

    if action == Action.RIGHT:
        return Position(position.row, position.col + 1)

    return position


"""
Calcula a quantidade de passos necessários para ir de uma posição a outra,
será usada para saber se ghost se aproximou ou não do pacman
"""

def manhattan_distance(a: Position, b: Position) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)