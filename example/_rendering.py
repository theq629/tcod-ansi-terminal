"""
Rendering of the world.
"""

from typing import Literal
import numpy
from tcod.console import Console
from ._world import World

FLOOR_BG = (64, 64, 64)
WALL_BG = (64, 64, 128)

class WorldRenderer:
    def __init__(self, world: World, console_order: Literal['C', 'F']):
        self.world = world

        self._walls_update = numpy.full(world.dim, FLOOR_BG, dtype="3B")
        for xy in numpy.ndindex(world.dim):
            if world.walls[xy]:
                self._walls_update[xy] = WALL_BG
        if console_order == 'C':
            self._walls_update = self._walls_update.transpose(1, 0, 2)

    def render(self, console: Console) -> None:
        i = min(console.rgba.shape[0], self._walls_update.shape[0])
        j = min(console.rgba.shape[1], self._walls_update.shape[1])
        console.rgb['bg'][0:i, 0:j] = self._walls_update[0:i, 0:j]
        console.print(x=self.world.player_pos[0], y=self.world.player_pos[1], string="@")
        console.print(x=2, y=0, string=f"{console.width}x{console.height}")
