"""
Minimal world for example.
"""

from typing import Tuple
from random import Random
import numpy
from numpy.typing import NDArray

def _make_walls(dim: Tuple[int, int], rng: Random) -> NDArray[numpy.bool_]:
    walls = numpy.full(dim, False)
    for x in range(dim[0]):
        walls[x, 0] = True
        walls[x, dim[1] - 1] = True
    for y in range(dim[1]):
        walls[0, y] = True
        walls[dim[0] - 1, y] = True
    for _ in range(int(dim[0] * dim[1] * 0.05)):
        x = rng.randint(1, dim[0] - 1)
        y = rng.randint(1, dim[1] - 1)
        walls[x, y] = True
    return walls

class World:
    def __init__(self, dim: Tuple[int, int], rng: Random):
        self.dim = dim
        self.walls = _make_walls(dim, rng)
        self.player_pos = dim[0] // 2, dim[1] // 2
        self.walls[self.player_pos] = False

    def move_player(self, offset: Tuple[int, int]) -> None:
        new_pos = self.player_pos[0] + offset[0], self.player_pos[1] + offset[1]
        if self.walls[new_pos]:
            return
        self.player_pos = new_pos
