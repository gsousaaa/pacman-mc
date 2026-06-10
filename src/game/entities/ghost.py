from dataclasses import dataclass
from game.entities.position import Position

@dataclass
class Ghost:
    position: Position