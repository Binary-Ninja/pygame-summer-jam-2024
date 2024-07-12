# This file holds game objects.

import random
import enum

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

DRONE_1 = 20
DRONE_2 = 5
DRONE_POLYGONS = (
    ((-DRONE_2, -DRONE_2), (0, -DRONE_1), (DRONE_2, -DRONE_2)),
    ((DRONE_2, -DRONE_2), (DRONE_1, 0), (DRONE_2, DRONE_2)),
    ((DRONE_2, DRONE_2), (0, DRONE_1), (-DRONE_2, DRONE_2)),
    ((-DRONE_2, DRONE_2), (-DRONE_1, 0), (-DRONE_2, -DRONE_2)),
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

OCT_1 = 60
OCT_2 = 42
OCTAGON_TRIANGLES = (
    ((0, -OCT_1), (OCT_2, -OCT_2)),
    ((OCT_2, -OCT_2), (OCT_1, 0)),
    ((OCT_1, 0), (OCT_2, OCT_2)),
    ((OCT_2, OCT_2), (0, OCT_1)),
    ((0, OCT_1), (-OCT_2, OCT_2)),
    ((-OCT_2, OCT_2), (-OCT_1, 0)),
    ((-OCT_1, 0), (-OCT_2, -OCT_2)),
    ((-OCT_2, -OCT_2), (0, -OCT_1)),
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
PLAYER_BULLET_RADIUS = 5
PLAYER_BULLET_SPEED = 500
PLAYER_FIRE_RATE = 500

RUNNER_RUN_DISTANCE = 400

ARENA_BOUNCE = 0.8

BULLET_DAMAGE = 1

BOUNCE_DAMAGE = 1
BOUNCE_I_FRAMES = 200
DAMAGE_FLASH_MS = 200

ASTEROID_HIT_SOUND = "explosion.wav"
ASTEROID_BREAK_SOUND = "asteroid_break.wav"


class ObjectShape(enum.Enum):
    DRONE = enum.auto()
    TRIANGLE = enum.auto()
    SQUARE = enum.auto()
    HEXAGON = enum.auto()
    OCTAGON = enum.auto()
    PLAYER = enum.auto()


SHAPE_SCORES = {
    ObjectShape.DRONE: 2,
    ObjectShape.TRIANGLE: 4,
    ObjectShape.SQUARE: 6,
    ObjectShape.HEXAGON: 8,
    ObjectShape.OCTAGON: 12,
    ObjectShape.PLAYER: 0,
}

RANDOM_SHAPES = (ObjectShape.TRIANGLE, ObjectShape.SQUARE, ObjectShape.HEXAGON, ObjectShape.OCTAGON)


class ObjectType(enum.Enum):
    PLAYER_DRONE = enum.auto()
    ENEMY_DRONE = enum.auto()
    ASTEROID = enum.auto()
    ORBITER = enum.auto()
    RUNNER = enum.auto()
    CHASER = enum.auto()
    PLAYER = enum.auto()


PLAYER_FACTION = (ObjectType.PLAYER, ObjectType.PLAYER_DRONE)
ENEMY_FACTION = (ObjectType.ENEMY_DRONE, ObjectType.ASTEROID, ObjectType.ORBITER, ObjectType.RUNNER, ObjectType.CHASER)


TYPE_SCORES = {
    ObjectType.ASTEROID: 1,
    ObjectType.ORBITER: 3,
    ObjectType.RUNNER: 2,
    ObjectType.CHASER: 4,
    ObjectType.ENEMY_DRONE: 1,
    ObjectType.PLAYER: 0,
    ObjectType.PLAYER_DRONE: 0,
}


RANDOM_TYPES = (ObjectType.ASTEROID, ObjectType.ORBITER, ObjectType.RUNNER, ObjectType.CHASER)


POLYGONS = {
    ObjectShape.DRONE: DRONE_POLYGONS,
    ObjectShape.TRIANGLE: TRIANGLE_TRIANGLES,
    ObjectShape.SQUARE: SQUARE_TRIANGLES,
    ObjectShape.HEXAGON: HEXAGON_TRIANGLES,
    ObjectShape.OCTAGON: OCTAGON_TRIANGLES,
    ObjectShape.PLAYER: PLAYER_POLYGONS,
}

RADII = {
    ObjectShape.DRONE: 12,
    ObjectShape.TRIANGLE: 15,
    ObjectShape.SQUARE: 30,
    ObjectShape.HEXAGON: 35,
    ObjectShape.OCTAGON: 55,
    ObjectShape.PLAYER: 10,
}

HEALTH = {
    ObjectShape.DRONE: 2,
    ObjectShape.TRIANGLE: 4,
    ObjectShape.SQUARE: 6,
    ObjectShape.HEXAGON: 8,
    ObjectShape.OCTAGON: 12,
    ObjectShape.PLAYER: 10,
}

THRUST = {
    ObjectShape.DRONE: 250,
    ObjectShape.TRIANGLE: 200,
    ObjectShape.SQUARE: 150,
    ObjectShape.HEXAGON: 100,
    ObjectShape.OCTAGON: 50,
    ObjectShape.PLAYER: 500,
}

COLORS = {
    ObjectType.ASTEROID: Color.WHITE,
    ObjectType.ORBITER: Color.YELLOW,
    ObjectType.RUNNER: Color.ORANGE,
    ObjectType.CHASER: Color.RED,
    ObjectType.ENEMY_DRONE: Color.MAGENTA,
    ObjectType.PLAYER: Color.GREEN,
    ObjectType.PLAYER_DRONE: Color.CYAN,
}


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
        self.damage = BULLET_DAMAGE

    def update(self, dt: float, *args, **kwargs) -> bool:
        # Despawn outside of arena bounds.
        if self.pos.length_squared() > kwargs["arena_radius"] ** 2:
            return False
        for game_object in kwargs["game_objects"]:
            # Don't damage those of your faction.
            if self.owner.type in PLAYER_FACTION and game_object.type in PLAYER_FACTION:
                continue
            if self.owner.type in ENEMY_FACTION and game_object.type in ENEMY_FACTION:
                continue
            # Collide and deal damage.
            if self.pos.distance_squared_to(game_object.pos) < game_object.radius ** 2:
                game_object.health -= self.damage
                if game_object.health > 0:
                    kwargs["sounds"].play(ASTEROID_HIT_SOUND)
                if game_object.health <= 0 and self.owner.type in PLAYER_FACTION:
                    kwargs["scores"].append(SHAPE_SCORES[game_object.shape] * TYPE_SCORES[game_object.type])
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
    def __init__(self, pos: Sequence[float], shape: ObjectShape, type_: ObjectType, vel: Sequence[float] = (0, 0)):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa
        self.angle = 0
        self.shape = shape
        self.type = type_
        self.polygons = POLYGONS[shape]
        self.color = COLORS[type_]
        self.radius = RADII[shape]
        self.health = HEALTH[shape]
        self.last_hit = 0

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        if self.health <= 0 and self.type is not ObjectType.PLAYER:
            for _ in range(40):
                vel_vector = utils.polar_vector(-random.randint(60, 120), random.randrange(360))
                kwargs["d"].add(DebrisParticle(self.pos, vel_vector, self.color))
            if kwargs["s"].get_rect().collidepoint(self.pos + kwargs["c"]):
                sounds.play(ASTEROID_BREAK_SOUND)
            return False
        self.pos += self.vel * dt
        if self.pos.length_squared() > arena_radius ** 2:
            self.pos.scale_to_length(arena_radius)
            self.vel = self.vel.reflect(self.pos) * ARENA_BOUNCE
        for go in objects:
            if go is self:
                continue
            if self.pos.distance_squared_to(go.pos) < (self.radius + go.radius) ** 2:
                # Player and player drones don't collide.
                if self.type in PLAYER_FACTION and go.type in PLAYER_FACTION:
                    continue
                # Enemy drones don't collide with enemies.
                if self.type is ObjectType.ENEMY_DRONE and go.type in ENEMY_FACTION:
                    continue
                # Enemies don't collide with enemy drones.
                if self.type in ENEMY_FACTION and go.type is ObjectType.ENEMY_DRONE:
                    continue
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
    def __init__(self, pos: Sequence[float], shape: ObjectShape):
        super().__init__(pos, shape, ObjectType.ASTEROID, utils.random_vector(350))
        self.turn_speed = random.randint(-100, 100)

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.angle += self.turn_speed * dt
        self.angle %= 360
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class Orbiter(GameObject):
    def __init__(self, pos: Sequence[float], shape: ObjectShape, target: Sequence[float] = (0, 0)):
        vel = (pg.Vector2(target) - pos).rotate(random.choice((90, -90)))  # noqa
        vel.scale_to_length(random.randrange(int(vel.length())))
        super().__init__(pos, shape, ObjectType.ORBITER, vel)
        self.acc = pg.Vector2()
        self.turn_speed = random.randint(-100, 100)
        self.target = target

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.angle += self.turn_speed * dt
        self.angle %= 360
        self.acc = self.target - self.pos  # noqa
        self.acc.scale_to_length(THRUST[self.shape])
        self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class Chaser(GameObject):
    def __init__(self, pos: Sequence[float], shape: ObjectShape, target: GameObject):
        super().__init__(pos, shape, ObjectType.CHASER)
        self.acc = pg.Vector2()
        self.target = target

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.angle = pg.Vector2().angle_to(self.target.pos - self.pos) + 90
        self.acc = self.target.pos - self.pos
        self.acc.scale_to_length(THRUST[self.shape])
        self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class Runner(GameObject):
    def __init__(self, pos: Sequence[float], shape: ObjectShape, target: GameObject):
        super().__init__(pos, shape, ObjectType.RUNNER)
        self.acc = pg.Vector2()
        self.target = target

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.angle = pg.Vector2().angle_to(self.target.pos - self.pos) + 90
        if self.pos.distance_squared_to(self.target.pos) < RUNNER_RUN_DISTANCE ** 2:
            self.acc = self.pos - self.target.pos
            self.acc.scale_to_length(THRUST[self.shape])
            self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class PlayerDrone(GameObject):
    def __init__(self, player: GameObject):
        pos = player.pos + utils.random_vector(100, 50)
        vel = (player.pos - pos).rotate(random.choice((90, -90)))
        vel.scale_to_length(random.randint(50, 200))
        super().__init__(pos, ObjectShape.DRONE, ObjectType.PLAYER_DRONE, vel)
        self.acc = pg.Vector2()
        self.turn_speed = random.randint(-100, 100)
        self.target = player

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.angle += self.turn_speed * dt
        self.angle %= 360
        self.acc = self.target.pos - self.pos
        self.acc.scale_to_length(THRUST[self.shape])
        self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class EnemyDrone(GameObject):
    def __init__(self, enemy: GameObject):
        pos = enemy.pos + utils.random_vector(100, 50)
        vel = (enemy.pos - pos).rotate(random.choice((90, -90)))
        vel.scale_to_length(random.randint(50, 200))
        super().__init__(pos, ObjectShape.DRONE, ObjectType.ENEMY_DRONE, vel)
        self.acc = pg.Vector2()
        self.turn_speed = random.randint(-100, 100)
        self.target = enemy

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        if self.target.health <= 0:
            self.target = kwargs["p"]
        self.angle += self.turn_speed * dt
        self.angle %= 360
        self.acc = self.target.pos - self.pos
        self.acc.scale_to_length(THRUST[self.shape])
        self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class Player(GameObject):
    def __init__(self, pos: Sequence[float]):
        super().__init__(pos, ObjectShape.PLAYER, ObjectType.PLAYER)
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
            self.acc.from_polar((-THRUST[self.shape], self.angle + 90))
        else:
            self.acc = pg.Vector2()
        self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)

    def draw(self, screen: pg.Surface, light_source: Sequence[float], camera: Sequence[float]):
        if not self.dead:
            super().draw(screen, light_source, camera)
