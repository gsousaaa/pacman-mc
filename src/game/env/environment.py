from typing import Optional
import random

from game.entities.position import Position
from game.entities.ghost import Ghost
from game.entities.player import Player

from game.env.action import N_ACTIONS, Action
from game.env.state_encoder import StateEncoder


from game.rules.movement import get_next_position, manhattan_distance
from game.rules.rewards import (
    REWARD_STEP,
    REWARD_WALL,
    REWARD_CAPTURE,
    REWARD_APPROACH,
    REWARD_MOVE_AWAY
)
from game.rules.end_game import is_capture

"""
Ambiente do jogo para o agente Ghost, que tem o objetivo de capturar o Pacman.
player_mode = "npc" será usado para treinar o ghost contra um player que se move aleatoriamente,
player_mode = "human" será usado para humanos jogarem contra o agente.
"""

class Environment:
    def __init__(self, game_map, player_mode: str = "npc"):
        self.original_map = [list(row) for row in game_map]

        self.height = len(game_map)
        self.width = len(game_map[0])

        self.player_mode = player_mode

        self.n_actions = N_ACTIONS

        self.state_encoder = StateEncoder(self.original_map)
        self.n_states = self.state_encoder.n_states

        self.initial_ghost_position = None
        self.initial_player_position = None

        self._find_initial_positions()

        self.reset()

    def _find_initial_positions(self):
        for row in range(self.height):
            for col in range(self.width):
                cell = self.original_map[row][col]

                if cell == "G":
                    self.initial_ghost_position = Position(row, col)

                elif cell == "P":
                    self.initial_player_position = Position(row, col)

        if self.initial_ghost_position is None:
            raise ValueError("O mapa precisa ter uma posição inicial G para o Ghost.")

        if self.initial_player_position is None:
            raise ValueError("O mapa precisa ter uma posição inicial P para o Player.")

    def reset(self, start_state: Optional[int] = None) -> int:
        self.map = [row.copy() for row in self.original_map]

        ghost_position = self.initial_ghost_position
        player_position = self.initial_player_position

        if start_state is not None:
            ghost_position, player_position = self.decode_state(start_state)

            if ghost_position == player_position:
                ghost_position = self.initial_ghost_position
                player_position = self.initial_player_position

        self.ghost = Ghost(position=ghost_position)
        self.player = Player(position=player_position)

        self.done = False
        self.steps = 0
        self.total_reward = 0

        return self.encode_state()

    def step(self, action: int):
        if self.done:
            return self.encode_state(), 0, True

        self.steps += 1

        old_distance = manhattan_distance(
            self.ghost.position,
            self.player.position,
        )

        reward = REWARD_STEP

        ghost_moved = self._move_ghost(action)
    # Se o ghost bateu na parede, -10 de recompensa
        if not ghost_moved:
            reward += REWARD_WALL

        if self._is_capture():
            reward = REWARD_CAPTURE
            self.done = True
            self.total_reward += reward
            return self.encode_state(), reward, self.done

        if self.player_mode == "npc":
            self._move_player_npc()

        if self._is_capture():
            reward = REWARD_CAPTURE
            self.done = True
            self.total_reward += reward
            return self.encode_state(), reward, self.done

        new_distance = manhattan_distance(
            self.ghost.position,
            self.player.position,
        )
     # Se a distância diminuiu, +10 de recompensa
        if new_distance < old_distance:
            reward += REWARD_APPROACH
     # Se a distância aumentou, -10 de recompensa
        elif new_distance > old_distance:
            reward += REWARD_MOVE_AWAY

        self.total_reward += reward

        return self.encode_state(), reward, self.done

    def _move_ghost(self, action: int) -> bool:
        next_position = get_next_position(self.ghost.position, action)

        if self.is_wall(next_position):
            return False

        self.ghost.position = next_position
        return True

    # Função para mover o pacman aleatoriamente quando o player_mode = npc
    def _choose_random_action(self, player_position, is_wall): 
        actions = [
            Action.UP,
            Action.DOWN,
            Action.LEFT,
            Action.RIGHT,
        ]

        random.shuffle(actions)

        for action in actions:
            next_position = get_next_position(player_position, action)

            if not is_wall(next_position):
                 return action

        return None
        
    def _move_player_npc(self):
        action = self._choose_random_action(
            player_position=self.player.position,
            is_wall=self.is_wall,
        )

        if action is None:
            return

        next_position = get_next_position(self.player.position, action)

        if not self.is_wall(next_position):
            self.player.position = next_position
            
    # Função para mover o pacman quando o player_mode = human
    def move_player(self, action: int) -> bool:
        if self.done:
            return False

        next_position = get_next_position(self.player.position, action)

        if self.is_wall(next_position):
            return False

        self.player.position = next_position

        if self._is_capture():
            self.done = True

        return True

    def _is_capture(self) -> bool:
        return is_capture(
            ghost_position=self.ghost.position,
            player_position=self.player.position,
        )

    def encode_state(self) -> int:
        return self.state_encoder.encode(
            ghost_position=self.ghost.position,
            player_position=self.player.position,
        )

    def decode_state(self, state: int):
        return self.state_encoder.decode(state)

    def is_wall(self, position: Position) -> bool:
        if position.row < 0 or position.row >= self.height:
            return True

        if position.col < 0 or position.col >= self.width:
            return True

        return self.original_map[position.row][position.col] == "#"

    def get_render_data(self):
        return {
            "map": self.map,
            "ghost": self.ghost,
            "player": self.player,
            "steps": self.steps,
            "total_reward": self.total_reward,
            "done": self.done,
            "height": self.height,
            "width": self.width,
        }