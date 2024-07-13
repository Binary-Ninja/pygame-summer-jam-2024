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

DRONE_POLYGON = (
    (0, -10),
    (2, -2),
    (10, 0),
    (2, 2),
    (0, 10),
    (-2, 2),
    (-10, 0),
    (-2, -2),
)

PLAYER_THRUSTER_POS = (0, 10)
PLAYER_GUN_POS = (0, -20)

PLAYER_BULLET_RADIUS = 5
PLAYER_BULLET_SPEED = 500
PLAYER_FIRE_RATE = 500
DRONE_FIRE_RATE = 1000
PLAYER_BULLET_DAMAGE = 1

ENEMY_BULLET_RADIUS = 5
ENEMY_BULLET_SPEED = 500
ENEMY_FIRE_RATE = 1000
ENEMY_BULLET_DAMAGE = 1

RUNNER_RUN_DISTANCE = 400
GUNNER_GUN_DISTANCE = 300
POWERUP_SUCK_DISTANCE = 200

ARENA_BOUNCE = 0.6

BIG_BULLET_RADIUS = 10
BIG_BULLET_DAMAGE = 2
BIG_BULLET_SPEED = 1000
BIG_PLAYER_FIRE_RATE = 200
RAPIDFIRE_RADIUS = 3
MAX_SHIELD = 10
SHIELD_BONUS = 2

LASER_DAMAGE = 1
BOUNCE_DAMAGE = 1
BOUNCE_I_FRAMES = 250
DAMAGE_FLASH_MS = 250

ASTEROID_HIT_SOUND = "explosion.wav"
PLAYER_HIT_SOUND = "player_hit.wav"
ASTEROID_BREAK_SOUND = "asteroid_break.wav"
FIRE_GUN_SOUND = "fire_gun.wav"
SHIELD_HIT_SOUND = "shield_hit.wav"
ENEMY_FIRE_GUN_SOUND = "enemy_gun.wav"
PLAYER_DEATH_SOUND = "player_death.wav"
POWERUP_SOUND = "power_up.wav"


class ObjectShape(enum.Enum):
    DRONE = enum.auto()
    TRIANGLE = enum.auto()
    SQUARE = enum.auto()
    HEXAGON = enum.auto()
    OCTAGON = enum.auto()
    PLAYER = enum.auto()
    POWER_UP = enum.auto()


SHAPE_SCORES = {
    ObjectShape.DRONE: 2,
    ObjectShape.TRIANGLE: 3,
    ObjectShape.SQUARE: 4,
    ObjectShape.HEXAGON: 6,
    ObjectShape.OCTAGON: 8,
    ObjectShape.PLAYER: 0,
    ObjectShape.POWER_UP: 0,
}

RANDOM_SHAPES = (ObjectShape.TRIANGLE, ObjectShape.SQUARE, ObjectShape.HEXAGON, ObjectShape.OCTAGON,
                 ObjectShape.SQUARE, ObjectShape.HEXAGON)


class ObjectType(enum.Enum):
    POWER_UP = enum.auto()
    PLAYER_DRONE = enum.auto()
    ENEMY_DRONE = enum.auto()
    ASTEROID = enum.auto()
    ORBITER = enum.auto()
    RUNNER = enum.auto()
    CHASER = enum.auto()
    GUNNER = enum.auto()
    PLAYER = enum.auto()


def get_types(wave: int) -> Sequence[ObjectType]:
    # First two waves have only basic enemies.
    if wave <= 2:
        return ObjectType.ASTEROID, ObjectType.ORBITER
    # Then we introduce some runners.
    if wave <= 5:
        return ObjectType.ASTEROID, ObjectType.ORBITER, ObjectType.RUNNER
    # Now for some chasers.
    if wave <= 7:
        return ObjectType.ASTEROID, ObjectType.ORBITER, ObjectType.RUNNER, ObjectType.CHASER
    # Then all of them.
    return RANDOM_TYPES


class PowerUpType(enum.Enum):
    # Ship upgrades.
    HEALTH = enum.auto()
    THRUST = enum.auto()
    PHASE = enum.auto()
    # Bullet upgrades.
    BULLET_DAMAGE = enum.auto()
    RAPID_FIRE = enum.auto()
    BULLET_SPEED = enum.auto()
    # Drone upgrades.
    DRONE = enum.auto()
    BULLET_DRONES = enum.auto()
    # Only drops from gunners.
    LASER = enum.auto()
    # Only drops if enemy was shielded.
    SHIELD = enum.auto()
    SHIELD_DRONE = enum.auto()


BASIC_POWERUPS = (
    PowerUpType.HEALTH,
    PowerUpType.THRUST,
)

BETTER_POWERUPS = (
    PowerUpType.RAPID_FIRE,
    PowerUpType.BULLET_DAMAGE,
    PowerUpType.DRONE,
)

BEST_POWERUPS = (
    PowerUpType.PHASE,
    PowerUpType.BULLET_SPEED,
    PowerUpType.BULLET_DRONES,
)

RANDOM_POWERUPS = (
    PowerUpType.BULLET_DAMAGE,
    PowerUpType.RAPID_FIRE,
    PowerUpType.HEALTH,
    PowerUpType.THRUST,
    PowerUpType.SHIELD,
    PowerUpType.DRONE,
    PowerUpType.BULLET_DRONES,
    PowerUpType.SHIELD_DRONE,
    PowerUpType.PHASE,
    PowerUpType.LASER,
    PowerUpType.BULLET_SPEED,
)

DROP_RATE = {
    ObjectType.POWER_UP: 0,
    ObjectType.PLAYER: 0,
    ObjectType.PLAYER_DRONE: 0,
    ObjectType.ENEMY_DRONE: 0,
    ObjectType.ASTEROID: 0.1,
    ObjectType.ORBITER: 0.2,
    ObjectType.RUNNER: 0.5,
    ObjectType.CHASER: 0.5,
    ObjectType.GUNNER: 1,
}

LOOT: dict[ObjectType, Sequence[PowerUpType]] = {
    ObjectType.POWER_UP: [],
    ObjectType.PLAYER: [],
    ObjectType.PLAYER_DRONE: [],
    ObjectType.ENEMY_DRONE: [],
    ObjectType.ASTEROID: BASIC_POWERUPS,
    ObjectType.ORBITER: BASIC_POWERUPS + BETTER_POWERUPS,
    ObjectType.RUNNER: BASIC_POWERUPS + BETTER_POWERUPS + BEST_POWERUPS,
    ObjectType.CHASER: BETTER_POWERUPS + BEST_POWERUPS,
    ObjectType.GUNNER: (PowerUpType.BULLET_DAMAGE, PowerUpType.RAPID_FIRE,
                        PowerUpType.BULLET_SPEED, PowerUpType.BULLET_DRONES,
                        PowerUpType.LASER,
                        ),
}


PLAYER_FACTION = (ObjectType.PLAYER, ObjectType.PLAYER_DRONE)
ENEMY_MARKERS = (ObjectType.ASTEROID, ObjectType.ORBITER, ObjectType.RUNNER, ObjectType.CHASER, ObjectType.GUNNER)
ENEMY_FACTION = ENEMY_MARKERS + (ObjectType.ENEMY_DRONE,)


TYPE_SCORES = {
    ObjectType.POWER_UP: 0,
    ObjectType.PLAYER: 0,
    ObjectType.PLAYER_DRONE: 0,
    ObjectType.ENEMY_DRONE: 1,
    ObjectType.ASTEROID: 1,
    ObjectType.ORBITER: 2,
    ObjectType.RUNNER: 3,
    ObjectType.CHASER: 4,
    ObjectType.GUNNER: 5,
}


RANDOM_TYPES = (ObjectType.ASTEROID, ObjectType.ORBITER, ObjectType.RUNNER, ObjectType.CHASER, ObjectType.GUNNER)


POLYGONS = {
    ObjectShape.DRONE: DRONE_POLYGONS,
    ObjectShape.TRIANGLE: TRIANGLE_TRIANGLES,
    ObjectShape.SQUARE: SQUARE_TRIANGLES,
    ObjectShape.HEXAGON: HEXAGON_TRIANGLES,
    ObjectShape.OCTAGON: OCTAGON_TRIANGLES,
    ObjectShape.PLAYER: PLAYER_POLYGONS,
    ObjectShape.POWER_UP: PLAYER_POLYGONS,
}

RADII = {
    ObjectShape.DRONE: 12,
    ObjectShape.TRIANGLE: 15,
    ObjectShape.SQUARE: 30,
    ObjectShape.HEXAGON: 35,
    ObjectShape.OCTAGON: 55,
    ObjectShape.PLAYER: 10,
    ObjectShape.POWER_UP: 12,
}

HEALTH = {
    ObjectShape.DRONE: 2,
    ObjectShape.TRIANGLE: 3,
    ObjectShape.SQUARE: 4,
    ObjectShape.HEXAGON: 6,
    ObjectShape.OCTAGON: 8,
    ObjectShape.PLAYER: 10,
    ObjectShape.POWER_UP: 1,
}

THRUST = {
    ObjectShape.DRONE: 250,
    ObjectShape.TRIANGLE: 150,
    ObjectShape.SQUARE: 150,
    ObjectShape.HEXAGON: 100,
    ObjectShape.OCTAGON: 50,
    ObjectShape.PLAYER: 500,
    ObjectShape.POWER_UP: 200,
}

COLORS = {
    ObjectType.PLAYER: Color.GREEN,
    ObjectType.PLAYER_DRONE: Color.CYAN,
    ObjectType.ENEMY_DRONE: Color.MAGENTA,
    ObjectType.ASTEROID: Color.WHITE,
    ObjectType.ORBITER: Color.YELLOW,
    ObjectType.RUNNER: Color.BLUE,
    ObjectType.GUNNER: Color.ORANGE,
    ObjectType.CHASER: Color.RED,
    ObjectType.POWER_UP: Color.BLACK,
}


def darken(color: tuple[int, int, int] | pg.Color, amount: float) -> pg.Color:
    return pg.Color(color).lerp(Color.BLACK, amount)


def lighten(color: tuple[int, int, int] | pg.Color, amount: float) -> pg.Color:
    return pg.Color(color).lerp(Color.WHITE, amount)


def centroid(points: Sequence[Sequence[float]]) -> tuple[float, float]:
    return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)


class Button:
    def __init__(self, y_offset: int, height: int = 45):
        self.y_offset = y_offset
        self.rect = pg.Rect(0, 0, 0, height)
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
    def __init__(self, pos: Sequence[float], vel: Sequence[float], big: bool = False):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa
        self.radius = random.randint(3, 5)
        self.start_time = pg.time.get_ticks()
        self.life_time = random.randint(200, 500 if big else 350)
        self.color = Color.BIG_THRUST if big else Color.THRUST

    def update(self, dt: float, *args, **kwargs) -> bool:
        if pg.time.get_ticks() - self.start_time >= self.life_time:
            return False
        self.pos += self.vel * dt
        return True

    def draw_pos(self, image: pg.Surface) -> Sequence[float]:
        return self.pos - (self.radius, self.radius)

    def cache_lookup(self) -> Hashable:
        return self.radius, self.color


class Bullet(utils.Particle):
    def __init__(self, pos: Sequence[float], vel: Sequence[float], owner: "GameObject", player: "Player"):
        self.pos = pg.Vector2(pos)  # noqa
        self.vel = pg.Vector2(vel)  # noqa
        self.owner = owner
        self.color = owner.color
        self.start_time = pg.time.get_ticks()
        self.life_time = 4000
        if owner.type in PLAYER_FACTION:
            self.color = Color.YELLOW if player.rapid_fire else player.color  # Drones also fire green bullets.
            self.radius = RAPIDFIRE_RADIUS if player.rapid_fire else PLAYER_BULLET_RADIUS
            if player.bullet_damage_up:
                self.radius = BIG_BULLET_RADIUS
                self.color = Color.CYAN
            if player.bullet_speed:
                self.color = Color.WHITE
            self.damage = BIG_BULLET_DAMAGE if player.bullet_damage_up else PLAYER_BULLET_DAMAGE
        else:
            self.radius = ENEMY_BULLET_RADIUS
            self.damage = ENEMY_BULLET_DAMAGE

    def update(self, dt: float, *args, **kwargs) -> bool:
        if pg.time.get_ticks() - self.start_time >= self.life_time:
            return False
        # Despawn outside of arena bounds.
        if self.pos.length_squared() > kwargs["arena_radius"] ** 2:
            return False
        for go in kwargs["game_objects"]:
            # Don't damage those of your faction.
            if self.owner.type in PLAYER_FACTION and go.type in PLAYER_FACTION:
                continue
            if self.owner.type in ENEMY_FACTION and go.type in ENEMY_FACTION:
                continue
            # Collide and deal damage.
            if self.pos.distance_squared_to(go.pos) < (go.radius + self.radius) ** 2:
                if go.type is ObjectType.POWER_UP:
                    go.health = 0
                    self.owner.apply_powerup(go.p_type, kwargs["sounds"], kwargs["game_objects"])
                    return False
                go.health -= self.damage
                go.shield_bypass = True
                if go.health > 0 and go.type is not ObjectType.PLAYER_DRONE:
                    kwargs["sounds"].play(PLAYER_HIT_SOUND if go.type is ObjectType.PLAYER else ASTEROID_HIT_SOUND)
                if go.health <= 0 and self.owner.type in PLAYER_FACTION:
                    bonus = SHIELD_BONUS if go.shield > 0 else 1
                    kwargs["scores"].append(SHAPE_SCORES[go.shape] * TYPE_SCORES[go.type] * bonus)
                go.last_hit = pg.time.get_ticks()
                return False
        self.pos += self.vel * dt
        return True

    def draw_pos(self, image: pg.Surface) -> Sequence[float]:
        return self.pos - (self.radius, self.radius)

    def cache_lookup(self) -> Hashable:
        return self.radius, self.color


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


class NebulaParticle(utils.Particle):
    def __init__(self):
        self.pos = pg.Vector2()
        self.radius = random.randint(1, 3)
        self.vel = utils.random_vector(self.radius * 500, 500)
        self.color = Color.BLACK

    def update(self, dt: float, *args, **kwargs) -> bool:
        # Despawn when outside of arena.
        if self.pos.length_squared() > kwargs["arena_radius"] ** 2:
            return False
        # Transparent at arena center, full white at arena edge.
        self.color = tuple(pg.Color(Color.BLACK).lerp(Color.WHITE, self.pos.length() / kwargs["arena_radius"]))
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
        self.shield_bypass = False
        self.shield = 0
        self.be_silent = False

    def apply_powerup(self, type_: PowerUpType, sounds, objects):
        # Could possibly add certain powerup abilities to enemies, but very unlikely.
        pass

    def on_screen(self, screen, camera):
        return screen.get_rect().inflate(20, 20).collidepoint(self.pos + camera)

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        if self.health <= 0 and self.type is not ObjectType.PLAYER:
            if self.type is not ObjectType.POWER_UP:
                if not self.be_silent:
                    for _ in range(40):
                        vel_vector = utils.polar_vector(-random.randint(60, 120), random.randrange(360))
                        kwargs["d"].add(DebrisParticle(self.pos, vel_vector, self.color))
                    if self.on_screen(kwargs["s"], kwargs["c"]) or self.shield_bypass:
                        sounds.play(ASTEROID_BREAK_SOUND)
                # Spawn powerups if not a drone.
                if self.type in ENEMY_FACTION and self.type is not ObjectType.ENEMY_DRONE:
                    if random.random() > DROP_RATE[self.type]:
                        loot = LOOT[self.type]
                        if self.shield:
                            loot += (PowerUpType.SHIELD, PowerUpType.SHIELD_DRONE)
                        objects.append(PowerUp(self.pos, self.vel, random.choice(loot)))
            return False
        self.pos += self.vel * dt
        if self.pos.length_squared() > arena_radius ** 2:
            if kwargs["e"]:
                self.pos.scale_to_length(-arena_radius)
            else:
                self.pos.scale_to_length(arena_radius)
                self.vel = self.vel.reflect(self.pos) * ARENA_BOUNCE
        # Get hit by the laser.
        player = kwargs["p"]
        ticks = pg.time.get_ticks()
        if self.type in ENEMY_FACTION and player.thrusting and player.laser:
            p2 = utils.polar_vector(arena_radius * 2, player.angle - 90)  # The laser spans the entire arena.
            if utils.collide_circle_line(player.pos, p2, self.pos, self.radius + 10):
                self.shield = 0  # Lasers destroy shields.
                if ticks - self.last_hit >= BOUNCE_I_FRAMES:
                    self.last_hit = ticks
                    self.shield_bypass = True  # Play break sound offscreen.
                    self.health -= LASER_DAMAGE
                    sounds.play(ASTEROID_HIT_SOUND)
        # Collide with other objects.
        for go in objects:
            if go is self:
                continue
            if self.pos.distance_squared_to(go.pos) < (self.radius + go.radius) ** 2:
                # Don't collide with powerups.
                if go.type is ObjectType.POWER_UP:
                    continue
                # Apply powerups.
                if self.type is ObjectType.POWER_UP:
                    if go.type in PLAYER_FACTION:
                        player.apply_powerup(self.p_type, sounds, objects)  # noqa
                        return False
                    continue
                # Don't collide if phasing.
                if self is player and self.phase and self.thrusting:  # noqa
                    continue
                # Player and player drones don't collide.
                if self.type in PLAYER_FACTION and go.type in PLAYER_FACTION:
                    continue
                # Enemy drones don't collide with enemies.
                if self.type is ObjectType.ENEMY_DRONE and go.type in ENEMY_FACTION:
                    continue
                # Enemies don't collide with enemy drones.
                if self.type in ENEMY_FACTION and go.type is ObjectType.ENEMY_DRONE:
                    continue
                # Don't collide with a dead or phasing player.
                if self.type in ENEMY_FACTION and go.type is ObjectType.PLAYER:
                    if player.dead or (player.phase and player.thrusting):
                        continue
                # Decrease health if i-frames allow.
                if ticks - self.last_hit >= BOUNCE_I_FRAMES:
                    self.shield_bypass = False
                    self.last_hit = ticks
                    if self.shield > 0:
                        self.shield -= 1
                    else:
                        self.health -= BOUNCE_DAMAGE
                if ticks - go.last_hit >= BOUNCE_I_FRAMES:
                    go.shield_bypass = False
                    go.last_hit = ticks
                    if go.shield > 0:
                        go.shield -= 1
                    else:
                        go.health -= BOUNCE_DAMAGE
                # Play sound if player.
                if self is player or go is player:
                    sounds.play(SHIELD_HIT_SOUND if player.shield > 0 else PLAYER_HIT_SOUND)
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
        # Detect if under damage flash effect.
        flash_effect = pg.time.get_ticks() - self.last_hit < DAMAGE_FLASH_MS
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
            if flash_effect and (self.shield <= 0 or self.shield_bypass):
                color = lighten(color, 0.25)
            # Draw the solid face.
            pg.draw.polygon(screen, color, draw_points)
            # Draw the outline.
            pg.draw.aalines(screen, self.color, True, draw_points)
        # Draw the shield.
        if self.shield > 0:
            width = 2
            color = pg.Color(Color.SHIELD_EMPTY_COLOR).lerp(Color.SHIELD_FULL_COLOR, self.shield / MAX_SHIELD)
            if flash_effect and not self.shield_bypass:
                width = 4
                color = Color.WHITE
            pg.draw.circle(screen, color, self.pos + camera, self.radius + 10, width)  # noqa


class Asteroid(GameObject):
    def __init__(self, pos: Sequence[float], shape: ObjectShape):
        super().__init__(pos, shape, ObjectType.ASTEROID, utils.random_vector(350))
        self.turn_speed = random.randint(-100, 100)

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.angle += self.turn_speed * dt
        self.angle %= 360
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class PowerUp(GameObject):
    def __init__(self, pos: Sequence[float], vel: Sequence[float], type_: PowerUpType):
        super().__init__(pos, ObjectShape.POWER_UP, ObjectType.POWER_UP, vel)
        self.p_type = type_
        self.acc = pg.Vector2()

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        player_pos = kwargs["p"].pos
        if self.pos.distance_squared_to(player_pos) < POWERUP_SUCK_DISTANCE ** 2:
            self.acc = player_pos - self.pos  # noqa
            self.acc.scale_to_length(THRUST[self.shape])
            self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)

    def draw(self, screen: pg.Surface, light_source: Sequence[float], camera: Sequence[float]):
        color = Color.WHITE
        radius = 2
        if self.p_type is PowerUpType.LASER:
            color = Color.RED
            p = 7
            p1, p2 = (-p, -p), (p, p)
            pg.draw.line(screen, color, self.pos + camera + p1, self.pos + camera + p2, 3)  # noqa
            p1, p2 = (-p, p), (p, -p)
            pg.draw.line(screen, color, self.pos + camera + p1, self.pos + camera + p2, 3)  # noqa
            p1, p2 = (0, -p), (0, p)
            pg.draw.line(screen, color, self.pos + camera + p1, self.pos + camera + p2, 3)  # noqa
            p1, p2 = (-p, 0), (p, 0)
            pg.draw.line(screen, color, self.pos + camera + p1, self.pos + camera + p2, 3)  # noqa
        if self.p_type is PowerUpType.HEALTH:
            color = Color.GREEN
            pg.draw.polygon(screen, color, [self.pos + p + camera for p in HP_POLYGON])  # noqa
        if self.p_type is PowerUpType.THRUST:
            color = Color.ORANGE
            pg.draw.polygon(screen, color, [self.pos + p + camera for p in HP_POLYGON])  # noqa
        if self.p_type is PowerUpType.PHASE:
            color = Color.CYAN
            pg.draw.polygon(screen, color, [self.pos + p + camera for p in HP_POLYGON])  # noqa
        if self.p_type is PowerUpType.SHIELD:
            color = Color.BLUE
            pg.draw.polygon(screen, color, [self.pos + p + camera for p in HP_POLYGON])  # noqa
        if self.p_type is PowerUpType.DRONE:
            color = Color.CYAN
            pg.draw.polygon(screen, color, [self.pos + p + camera for p in DRONE_POLYGON])  # noqa
        if self.p_type is PowerUpType.SHIELD_DRONE:
            color = Color.BLUE
            pg.draw.polygon(screen, color, [self.pos + p + camera for p in DRONE_POLYGON])  # noqa
        if self.p_type is PowerUpType.BULLET_DRONES:
            color = Color.GREEN
            pg.draw.polygon(screen, color, [self.pos + p + camera for p in DRONE_POLYGON])  # noqa
        if self.p_type is PowerUpType.BULLET_DAMAGE:
            color = Color.CYAN
            pg.draw.circle(screen, color, self.pos + camera, PLAYER_BULLET_RADIUS)  # noqa
        if self.p_type is PowerUpType.RAPID_FIRE:
            color = Color.YELLOW
            pg.draw.circle(screen, color, self.pos + camera, RAPIDFIRE_RADIUS)  # noqa
        if self.p_type is PowerUpType.BULLET_SPEED:
            color = Color.WHITE
            pg.draw.circle(screen, color, self.pos + camera, PLAYER_BULLET_RADIUS)  # noqa
        pg.draw.circle(screen, color, self.pos + camera, self.radius, radius)  # noqa


class Orbiter(GameObject):
    def __init__(self, pos: Sequence[float], shape: ObjectShape):
        self.target = utils.random_vector(500)
        vel = (pg.Vector2(self.target) - pos).rotate(random.choice((90, -90)))  # noqa
        vel.scale_to_length(random.randrange(int(vel.length())))
        super().__init__(pos, shape, ObjectType.ORBITER, vel)
        self.acc = pg.Vector2()
        self.turn_speed = random.randint(-100, 100)

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
        vel = (target.pos - pos).rotate(random.choice((90, -90)))  # noqa
        vel.scale_to_length(random.randrange(int(vel.length())))
        super().__init__(pos, shape, ObjectType.RUNNER, vel)
        self.acc = pg.Vector2()
        self.target = target

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.angle = pg.Vector2().angle_to(self.target.pos - self.pos) + 90
        if self.pos.distance_squared_to(self.target.pos) < RUNNER_RUN_DISTANCE ** 2:
            self.acc = self.pos - self.target.pos
            self.acc.scale_to_length(THRUST[self.shape])
            self.vel += self.acc * dt
        else:
            self.acc = self.target.pos - self.pos
            self.acc.scale_to_length(THRUST[self.shape])
            self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class Gunner(GameObject):
    def __init__(self, pos: Sequence[float], shape: ObjectShape, target: GameObject):
        super().__init__(pos, shape, ObjectType.GUNNER)
        self.acc = pg.Vector2()
        self.target = target
        self.last_fire = 0

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        self.angle = pg.Vector2().angle_to(self.target.pos - self.pos) + 90
        if self.pos.distance_squared_to(self.target.pos) < GUNNER_GUN_DISTANCE ** 2:
            self.acc = self.pos - self.target.pos
            self.acc.scale_to_length(THRUST[self.shape])
            self.vel += self.acc * dt
            if pg.time.get_ticks() - self.last_fire >= ENEMY_FIRE_RATE:
                sounds.play(ENEMY_FIRE_GUN_SOUND)
                self.last_fire = pg.time.get_ticks()
                vel_vector = utils.polar_vector(-ENEMY_BULLET_SPEED, self.angle + 90)
                gun_pos = self.target.pos - self.pos
                gun_pos.scale_to_length(self.radius)
                kwargs["b"].add(Bullet(self.pos + gun_pos, self.vel + vel_vector, self, kwargs["p"]))
        else:
            self.acc = self.target.pos - self.pos
            self.acc.scale_to_length(THRUST[self.shape])
            self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)


class Drone(GameObject):
    def __init__(self, owner: GameObject):
        pos = owner.pos + utils.random_vector(100, 50)
        vel = (owner.pos - pos).rotate(random.choice((90, -90)))
        vel.scale_to_length(random.randint(50, 200))
        t = ObjectType.PLAYER_DRONE if owner.type in PLAYER_FACTION else ObjectType.ENEMY_DRONE
        super().__init__(pos, ObjectShape.DRONE, t, vel)
        self.acc = pg.Vector2()
        self.turn_speed = random.randint(-100, 100)
        self.owner = owner
        self.bullets = False
        self.last_fire = 0

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        # Convert to player drone if enemy owner was killed.
        if self.type is ObjectType.ENEMY_DRONE and self.owner.health <= 0:
            self.owner = kwargs["p"]
            self.type = ObjectType.PLAYER_DRONE
            self.color = COLORS[self.type]
            # Reset turn speed for some visual flair.
            self.turn_speed = random.randint(-100, 100)
        # Rotate and orbit owner.
        self.angle += self.turn_speed * dt
        self.angle %= 360
        self.acc = self.owner.pos - self.pos
        self.acc.scale_to_length(THRUST[self.shape])
        self.vel += self.acc * dt
        # Fire bullets.
        if self.bullets and self.owner.thrusting and not self.owner.laser:
            fire_rate = PLAYER_FIRE_RATE if self.owner.rapid_fire else DRONE_FIRE_RATE
            if pg.time.get_ticks() - self.last_fire >= fire_rate:
                self.last_fire = pg.time.get_ticks()
                speed = -BIG_BULLET_SPEED if self.owner.bullet_speed else -PLAYER_BULLET_SPEED
                vel_vector = utils.polar_vector(speed, self.owner.angle + 90)
                kwargs["b"].add(Bullet(self.pos, self.vel + vel_vector, self, self.owner))
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
        # Powerup trackers.
        self.bullet_damage_up = 0
        self.rapid_fire = 0
        self.bullet_speed = 0
        self.big_thrust = 0.0
        self.phase = 0.0
        self.laser = 0.0

    def apply_powerup(self, type_: PowerUpType, sounds, objects):
        d_count = 1
        if type_ is PowerUpType.HEALTH:
            self.health += 1
        if type_ is PowerUpType.SHIELD:
            self.shield = MAX_SHIELD
        if type_ is PowerUpType.SHIELD_DRONE:
            d_count = 0
            for go in objects:
                if go.type is ObjectType.PLAYER_DRONE:
                    go.shield = MAX_SHIELD
                    d_count += 1
        if type_ is PowerUpType.DRONE:
            objects.append(Drone(self))
        if type_ is PowerUpType.BULLET_DAMAGE:
            self.bullet_damage_up = 50
        if type_ is PowerUpType.BULLET_SPEED:
            self.bullet_speed = 50
        if type_ is PowerUpType.RAPID_FIRE:
            self.rapid_fire = 200
        if type_ is PowerUpType.THRUST:
            self.big_thrust = 10.0
        if type_ is PowerUpType.PHASE:
            self.phase = 10.0
        if type_ is PowerUpType.BULLET_DRONES:
            d_count = 0
            for go in objects:
                if go.type is ObjectType.PLAYER_DRONE:
                    go.bullets = True
                    go.color = COLORS[self.type]
                    d_count += 1
        if type_ is PowerUpType.LASER:
            self.laser = 2.0
        # Don't play sounds if it is a drone powerup and you have no drones.
        if d_count:
            sounds.play(POWERUP_SOUND)

    def decrease_bullet_pups(self):
        self.bullet_damage_up = max(0, self.bullet_damage_up - 1)
        self.rapid_fire = max(0, self.rapid_fire - 1)
        self.bullet_speed = max(0, self.bullet_speed - 1)

    def update(self, dt: float, arena_radius: int, objects, sounds, **kwargs) -> bool:
        if self.dead:
            return True
        if self.health <= 0:
            for _ in range(40):
                vel_vector = utils.polar_vector(-random.randint(60, 120), random.randrange(360))
                kwargs["d"].add(DebrisParticle(self.pos, vel_vector, self.color))
            sounds.play(PLAYER_DEATH_SOUND)
            self.dead = True
            self.thrusting = False
        self.thrust_pos = self.pos + pg.Vector2(PLAYER_THRUSTER_POS).rotate(self.angle)
        self.gun_pos = self.pos + pg.Vector2(PLAYER_GUN_POS).rotate(self.angle)
        if self.thrusting:
            thrust_mult = 2 if self.big_thrust else 1
            self.acc.from_polar((-THRUST[self.shape] * thrust_mult, self.angle + 90))
            self.big_thrust = max(0.0, self.big_thrust - dt)
            self.phase = max(0.0, self.phase - dt)
            self.laser = max(0.0, self.laser - dt)
            if self.laser:
                pass
            else:
                fire_rate = BIG_PLAYER_FIRE_RATE if self.rapid_fire else PLAYER_FIRE_RATE
                if pg.time.get_ticks() - self.last_fire >= fire_rate:
                    sounds.play(FIRE_GUN_SOUND)
                    self.last_fire = pg.time.get_ticks()
                    speed = -BIG_BULLET_SPEED if self.bullet_speed else -PLAYER_BULLET_SPEED
                    vel_vector = utils.polar_vector(speed, self.angle + 90)
                    kwargs["b"].add(Bullet(self.gun_pos, self.vel + vel_vector, self, self))
                    self.decrease_bullet_pups()
        else:
            self.acc = pg.Vector2()
        self.vel += self.acc * dt
        return super().update(dt, arena_radius, objects, sounds, **kwargs)

    def draw(self, screen: pg.Surface, light_source: Sequence[float], camera: Sequence[float]):
        if not self.dead:
            if self.phase:
                self.color = pg.Color(Color.BLUE).lerp(Color.PHASE_COLOR, self.phase / 10)
                if self.thrusting:
                    self.color = pg.Color((20, 20, 128)).lerp(Color.PHASING_COLOR, self.phase / 10)
            super().draw(screen, light_source, camera)
            self.color = COLORS[self.type]
