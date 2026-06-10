from game.entities.position import Position

"""
Classe responsável por codificar, decodificar e quantificar os estados do jogo,
onde cada estado é representado por um número inteiro único. A quantidade de estados
possíveis é calculado fazendo a multiplicação entre o número de posições válidas para 
o ghost e para o pacman.
"""

class StateEncoder:
    def __init__(self, game_map):
        self.game_map = game_map

        self.valid_positions = []
        self.position_to_index = {}
        self.index_to_position = {}

        self._map_positions()

    def _map_positions(self):
        index = 0

        for row in range(len(self.game_map)):
            for col in range(len(self.game_map[row])):
                cell = self.game_map[row][col]

                if cell != "#":
                    position = Position(row, col)

                    self.valid_positions.append(position)
                    self.position_to_index[position] = index
                    self.index_to_position[index] = position

                    index += 1

    @property
    def n_positions(self):
        return len(self.valid_positions)

    @property
    def n_states(self):
        return self.n_positions * self.n_positions

    def encode(self, ghost_position: Position, player_position: Position) -> int:
        ghost_index = self.position_to_index[ghost_position]
        player_index = self.position_to_index[player_position]

        return ghost_index * self.n_positions + player_index

    def decode(self, state: int):
        ghost_index = state // self.n_positions
        player_index = state % self.n_positions

        ghost_position = self.index_to_position[ghost_index]
        player_position = self.index_to_position[player_index]

        return ghost_position, player_position