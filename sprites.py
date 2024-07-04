# This file holds game objects.

import pygame as pg

from colors import Color

from typing import Sequence

EQUILATERAL_TRIANGLE_HEIGHT_FACTOR = 0.866

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

PLAYER_POLYGONS = (
    ((0, -20), (-10, 20)),
    ((0, -20), (10, 20)),
    ((-10, 20), (0, 10), (10, 20)),
)


def darken(color: tuple[int, int, int], amount: float) -> pg.Color:
    return pg.Color(color).lerp(Color.BLACK, amount)


def centroid(points: Sequence[Sequence[float]]) -> tuple[float, float]:
    return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)


class GameObject:
    def __init__(self, pos: Sequence[float], polygons, color):
        self.pos = pg.Vector2(pos)  # noqa
        self.angle = 0
        self.polygons = polygons
        self.color = color

    def update(self, dt: float):
        pass

    def draw(self, screen: pg.Surface, light_source: Sequence[float], camera: Sequence[float]):
        # Draw each polygon separately.
        for polygon in self.polygons:
            # Calculate the world coordinates for each point, rotating as needed.
            points = [self.pos,] + [self.pos + pg.Vector2(point).rotate(self.angle) for point in polygon]
            # Calculate the lighting vectors.
            try:
                lighting_vector = (light_source - self.pos).normalize()  # noqa
            except ValueError:
                # Object is on top of the light source.
                # The dot product with a zero vector is always zero, so the object will be halfway lit.
                lighting_vector = (0, 0)
            normal_vector = (centroid(points) - self.pos).normalize()
            # Calculate the lighting amount.
            lighting = pg.math.remap(-1, 1, 0.75, 0, lighting_vector * normal_vector)
            # Transform the world coordinates into screen coordinates.
            draw_points = [point + camera for point in points]  # noqa
            # Draw the solid face.
            pg.draw.polygon(screen, darken(self.color, lighting), draw_points)
            # Draw the outline.
            pg.draw.aalines(screen, self.color, True, draw_points)


class Asteroid(GameObject):
    def __init__(self, pos: Sequence[float], polygons, color, turn_speed):
        super().__init__(pos, polygons, color)
        self.turn_speed = turn_speed

    def update(self, dt: float):
        self.angle += self.turn_speed * dt
        self.angle %= 360


class Player(GameObject):
    def __init__(self, pos: Sequence[float], polygons, color):
        super().__init__(pos, polygons, color)
        self.acc = pg.Vector2(0, 0)
        self.vel = pg.Vector2(0, 0)

    def update(self, dt: float):
        self.vel += self.acc * dt
        self.pos += self.vel * dt
