# This file holds game objects.

import random

import pygame as pg

import utils
from colors import Color

from typing import Sequence, Hashable

EQUILATERAL_TRIANGLE_HEIGHT_FACTOR = 0.866

TRIANGLE_TRIANGLES = (
    ((0, -25), (23, 15)),
    ((0, -25), (-23, 15)),
    ((23, 15), (-23, 15)),
)

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

HP_POLYGON = (
    (0, -10),
    (-5, 10),
    (0, 5),
    (5, 10),
)

PLAYER_THRUSTER_POS = (0, 10)
PLAYER_GUN_POS = (0, -20)
PLAYER_THRUST_ACC = 500
PLAYER_BULLET_RADIUS = 5
PLAYER_BULLET_SPEED = 500
PLAYER_FIRE_RATE = 500
PLAYER_RADIUS = 15

ENEMY_THRUST_ACC = 250

ARENA_BOUNCE = 0.8

BULLET_DAMAGE = 1
BOUNCE_DAMAGE = 1
BOUNCE_I_FRAMES = 200

DAMAGE_FLASH_MS = 200

ASTEROID_HIT_SOUND = "explosion.wav"
ASTEROID_BREAK_SOUND = "asteroid_break.wav"


def darken(color: tuple[int, int, int] | pg.Color, amount: float) -> pg.Color:
    return pg.Color(color).lerp(Color.BLACK, amount)


def lighten(color: tuple[int, int, int] | pg.Color, amount: float) -> pg.Color:
    return pg.Color(color).lerp(Color.WHITE, amount)


def centroid(points: Sequence[Sequence[float]]) -> tuple[float, float]:
    return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)


class Button:
    def __init__(self, y_offset: int):
        self.y_offset = y_offset
        self.rect = pg.Rect(0, 0, 0, 50)
        self.hover = False
        self.pressed = False

    def update(self) -> bool:
        self.hover = False
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.hover = True
            if pg.mouse.get_pressed()[0]:
                self.pressed = True
            elif self.pressed:  # Mouse was released over the button.
                self.pressed = False
                return True
        else:
            self.pressed = False
        return False

    def draw(self, screen: pg.Surface, font: pg.Font, text: str, color=Color.WHITE):
        if self.hover:
            color = Color.CYAN
        if self.pressed:
            color = Color.GREEN
        text_surf = font.render(text, True, color, Color.BLACK)
        self.rect.width = text_surf.width + 20
        self.rect.centerx = screen.get_rect().centerx  # noqa
        self.rect.centery = screen.get_rect().centery + self.y_offset  # noqa
        pg.draw.rect(screen, Color.BLACK, self.rect, 0, 15)
        pg.draw.rect(screen, color, self.rect, 2, 15)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))


class ThrustParticle(utils.Particle):
    def __init__(self, pos: Sequence[float], vel: Sequence[float]):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa
        self.radius = random.randint(3, 5)
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
    def __init__(self, pos: Sequence[float], vel: Sequence[float], owner: "GameObject"):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa
        self.owner = owner

    def update(self, dt: float, *args, **kwargs) -> bool:
        if self.pos.length_squared() > kwargs["arena_radius"] ** 2:
            return False
        for game_object in kwargs["game_objects"]:
            if game_object is self.owner:
                continue
            if self.pos.distance_squared_to(game_object.pos) < game_object.radius ** 2:
                game_object.health -= BULLET_DAMAGE
                if game_object.health > 0:
                    kwargs["sounds"].play(ASTEROID_HIT_SOUND)
                game_object.last_hit = pg.time.get_ticks()
                return False
        self.pos += self.vel * dt
        return True

    def draw_pos(self, image: pg.Surface) -> Sequence[float]:
        return self.pos - (PLAYER_BULLET_RADIUS, PLAYER_BULLET_RADIUS)

    def cache_lookup(self) -> Hashable:
        return Color.GREEN


class DebrisParticle(utils.Particle):
    def __init__(self, pos: Sequence[float], vel: Sequence[float], color):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa
        self.color = color
        self.radius = random.randint(2, 4)
        self.start_time = pg.time.get_ticks()
        self.life_time = random.randint(350, 500)

    def update(self, dt: float, *args, **kwargs) -> bool:
        if pg.time.get_ticks() - self.start_time >= self.life_time:
            return False
        self.pos += self.vel * dt
        return True

    def draw_pos(self, image: pg.Surface) -> Sequence[float]:
        return self.pos - (self.radius, self.radius)

    def cache_lookup(self) -> Hashable:
        return self.radius, self.color


class GameObject:
    def __init__(self, pos: Sequence[float], polygons, color, radius: int = 20, max_health: int = 10, vel=(0, 0)):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa
        self.angle = 0
        self.polygons = polygons
        self.color = color
        self.radius = radius
        self.health = max_health
        self.last_hit = 0

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.pos += self.vel * dt
        if self.pos.length_squared() > arena_radius ** 2:
            self.pos.scale_to_length(arena_radius)
            self.vel = self.vel.reflect(self.pos) * ARENA_BOUNCE
        for go in objects:
            if go is self:
                continue
            if self.pos.distance_squared_to(go.pos) < (self.radius + go.radius) ** 2:
                # Decrease health if i-frames allow.
                ticks = pg.time.get_ticks()
                if ticks - self.last_hit >= BOUNCE_I_FRAMES:
                    self.last_hit = ticks
                    self.health -= BOUNCE_DAMAGE
                if ticks - go.last_hit >= BOUNCE_I_FRAMES:
                    go.last_hit = ticks
                    go.health -= BOUNCE_DAMAGE
                # Play sound if player.
                if self is kwargs["p"] or go is kwargs["p"]:
                    sounds.play(ASTEROID_HIT_SOUND)
                # Move self away so they are no longer colliding.
                unstick_vector = self.pos - go.pos
                unstick_vector.scale_to_length(self.radius + go.radius - self.pos.distance_to(go.pos))
                self.pos += unstick_vector
                # Bounce the objects.
                tangent_vector = pg.Vector2(go.pos.y - self.pos.y, -(go.pos.x - self.pos.x)).normalize()
                rel_vel = self.vel - go.vel
                vel = rel_vel - tangent_vector * (rel_vel * tangent_vector)
                self.vel -= vel
                go.vel += vel
        return True

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
            # Sometimes lighting falls outside range, so we clamp it again to [0, 1].
            color = darken(self.color, pg.math.clamp(lighting, 0, 1))
            # Lighten the color for the flash animation when taking damage.
            if pg.time.get_ticks() - self.last_hit < DAMAGE_FLASH_MS:
                color = lighten(color, 0.5)
            # Draw the solid face.
            pg.draw.polygon(screen, color, draw_points)
            # Draw the outline.
            pg.draw.aalines(screen, self.color, True, draw_points)


class Asteroid(GameObject):
    def __init__(self, pos: Sequence[float], polygons, color, turn_speed, radius, vel=(0, 0), hp: int = 10):
        super().__init__(pos, polygons, color, radius, vel=vel)
        self.health = hp
        self.turn_speed = turn_speed

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        if self.health <= 0:
            for _ in range(40):
                vel_vector = utils.polar_vector(-random.randint(60, 120), random.randrange(360))
                kwargs["d"].add(DebrisParticle(self.pos, vel_vector, self.color))
            sounds.play(ASTEROID_BREAK_SOUND)
            return False
        self.angle += self.turn_speed * dt
        self.angle %= 360
        super().update(dt, arena_radius, objects, sounds, **kwargs)
        return True


class Player(GameObject):
    def __init__(self, pos: Sequence[float], polygons, color):
        super().__init__(pos, polygons, color, PLAYER_RADIUS)
        self.acc = pg.Vector2()
        self.thrusting = False
        self.thrust_pos = self.pos + pg.Vector2(PLAYER_THRUSTER_POS).rotate(self.angle)
        self.gun_pos = self.pos + pg.Vector2(PLAYER_GUN_POS).rotate(self.angle)
        self.last_fire = 0
        self.dead = False

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        if self.dead:
            return True
        if self.health <= 0:
            for _ in range(40):
                vel_vector = utils.polar_vector(-random.randint(60, 120), random.randrange(360))
                kwargs["d"].add(DebrisParticle(self.pos, vel_vector, self.color))
            sounds.play(ASTEROID_BREAK_SOUND)
            self.dead = True
            self.thrusting = False
        self.thrust_pos = self.pos + pg.Vector2(PLAYER_THRUSTER_POS).rotate(self.angle)
        self.gun_pos = self.pos + pg.Vector2(PLAYER_GUN_POS).rotate(self.angle)
        if self.thrusting:
            self.acc.from_polar((-PLAYER_THRUST_ACC, self.angle + 90))
        else:
            self.acc = pg.Vector2()
        self.vel += self.acc * dt
        super().update(dt, arena_radius, objects, sounds, **kwargs)
        return True

    def draw(self, screen: pg.Surface, light_source: Sequence[float], camera: Sequence[float]):
        if not self.dead:
            super().draw(screen, light_source, camera)


class EnemyShip(GameObject):
    def __init__(self, pos: Sequence[float], polygons, color, radius, hp: int, target: GameObject):
        super().__init__(pos, polygons, color, radius)
        self.health = hp
        self.target = target
        self.acc = pg.Vector2()

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        if self.health <= 0:
            for _ in range(40):
                vel_vector = utils.polar_vector(-random.randint(60, 120), random.randrange(360))
                kwargs["d"].add(DebrisParticle(self.pos, vel_vector, self.color))
            sounds.play(ASTEROID_BREAK_SOUND)
            return False
        self.angle = pg.Vector2().angle_to(self.target.pos - self.pos) + 90
        self.acc = self.target.pos - self.pos
        self.acc.scale_to_length(ENEMY_THRUST_ACC)
        self.vel += self.acc * dt
        super().update(dt, arena_radius, objects, sounds, **kwargs)
        return True
