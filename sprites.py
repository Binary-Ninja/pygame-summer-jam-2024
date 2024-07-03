# This file holds game objects.

import pygame as pg

from colors import Color

from typing import Sequence


SQUARE_TRIANGLES = (
    ((0, -40), (40, 0)),
    ((40, 0), (0, 40)),
    ((0, 40), (-40, 0)),
    ((-40, 0), (0, -40)),
)

HEXAGON_TRIANGLES = (
    ((0, -40), (35, -20)),
    ((35, -20), (35, 20)),
    ((35, 20), (0, 40)),
    ((0, 40), (-35, 20)),
    ((-35, 20), (-35, -20)),
    ((-35, -20), (0, -40)),
)

# Light comes from the origin.
LIGHT_SOURCE = pg.Vector2(0, 0)


def darken(color: tuple[int, int, int], amount: float) -> pg.Color:
    return pg.Color(color).lerp(Color.BLACK, amount)


def centroid(points: Sequence[Sequence[float]]) -> tuple[float, float]:
    return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)


class Asteroid:
    def __init__(self, pos: Sequence[float]):
        self.pos = pg.Vector2(pos)  # noqa
        self.angle = 0
        self.turn_speed = 20
        self.triangles = HEXAGON_TRIANGLES
        self.color = Color.WHITE

    def update(self, dt: float):
        self.angle += self.turn_speed * dt
        self.angle %= 360

    def draw(self, screen: pg.Surface, light_source):
        # Draw each polygon separately.
        for triangle in self.triangles:
            # Calculate the world coordinates for each point, rotating as needed.
            points = [self.pos,] + [self.pos + pg.Vector2(point).rotate(self.angle) for point in triangle]
            # Calculate the lighting vectors.
            to_light_vec = light_source - self.pos
            to_centroid_vec = centroid(points) - self.pos
            # Calculate the lighting amount.
            max_dot_value = to_light_vec.length() * to_centroid_vec.length()
            amount = pg.math.remap(-max_dot_value, max_dot_value, 0.75, 0, to_light_vec * to_centroid_vec)
            # Draw the solid face.
            pg.draw.polygon(screen, darken(self.color, amount), points)
            # Draw the outline.
            pg.draw.aalines(screen, self.color, True, points)
