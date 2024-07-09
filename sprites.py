# This file holds game objects.

import random

import pygame as pg

import utils
from colors import Color

from typing import Sequence, Hashable

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

PLAYER_THRUSTER_POS = (0, 10)
PLAYER_GUN_POS = (0, -20)
PLAYER_THRUST_ACC = 500
PLAYER_BULLET_RADIUS = 5
PLAYER_BULLET_SPEED = 500
PLAYER_FIRE_RATE = 500

ARENA_BOUNCE = 0.8


def darken(color: tuple[int, int, int], amount: float) -> pg.Color:
    return pg.Color(color).lerp(Color.BLACK, amount)


def centroid(points: Sequence[Sequence[float]]) -> tuple[float, float]:
    return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)


class ThrustParticle(utils.Particle):
    def __init__(self, pos: Sequence[float], vel: Sequence[float], radius: int):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa
        self.radius = radius
        self.start_time = pg.time.get_ticks()
        self.life_time = random.randint(200, 350)

    def update(self, dt: float, *args, **kwargs) -> bool:
        if pg.time.get_ticks() - self.start_time >= self.life_time:
            return False
        self.pos += self.vel * dt
        return True

    def draw_pos(self, image: pg.Surface) -> Sequence[float]:
        return self.pos - (self.radius, self.radius)

    def cache_lookup(self) -> Hashable:
        return self.radius


class Bullet(utils.Particle):
    def __init__(self, pos: Sequence[float], vel: Sequence[float]):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa

    def update(self, dt: float, *args, **kwargs) -> bool:
        if self.pos.length_squared() > kwargs["arena_radius"] ** 2:
            return False
        self.pos += self.vel * dt
        return True

    def draw_pos(self, image: pg.Surface) -> Sequence[float]:
        return self.pos - (PLAYER_BULLET_RADIUS, PLAYER_BULLET_RADIUS)

    def cache_lookup(self) -> Hashable:
        return Color.GREEN


class GameObject:
    def __init__(self, pos: Sequence[float], polygons, color):
        self.pos = pg.Vector2(pos)  # noqa
        self.angle = 0
        self.polygons = polygons
        self.color = color

    def update(self, dt: float, arena_radius: int):
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

    def update(self, dt: float, arena_radius: int):
        self.angle += self.turn_speed * dt
        self.angle %= 360


class Player(GameObject):
    def __init__(self, pos: Sequence[float], polygons, color):
        super().__init__(pos, polygons, color)
        self.acc = pg.Vector2(0, 0)
        self.vel = pg.Vector2(0, 0)
        self.thrusting = False
        self.thrust_pos = self.pos + pg.Vector2(PLAYER_THRUSTER_POS).rotate(self.angle)
        self.gun_pos = self.pos + pg.Vector2(PLAYER_GUN_POS).rotate(self.angle)
        self.last_fire = 0

    def update(self, dt: float, arena_radius: int):
        self.thrust_pos = self.pos + pg.Vector2(PLAYER_THRUSTER_POS).rotate(self.angle)
        self.gun_pos = self.pos + pg.Vector2(PLAYER_GUN_POS).rotate(self.angle)
        if self.thrusting:
            self.acc.from_polar((-PLAYER_THRUST_ACC, self.angle + 90))
        else:
            self.acc = pg.Vector2()
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        if self.pos.length_squared() > arena_radius ** 2:
            self.pos.scale_to_length(arena_radius)
            self.vel = self.vel.reflect(self.pos) * ARENA_BOUNCE
