#!/usr/bin/env python3
# -*- coding: utf8 -*-
import random
import functools
import sys
from pathlib import Path

import pygame as pg

import utils
import sprites

from colors import Color

APPLICATION_DIRECTORY = Path(__file__, "..").resolve()
SOUND_DIRECTORY = APPLICATION_DIRECTORY / "sounds"

LEFT_MOUSE_BUTTON = 1
WINDOWED_RESOLUTION = pg.Vector2(800, 600)
FPS_CAP = 0
SCREEN_BACKGROUND_COLOR = Color.BLACK
ARENA_RADIUS = 1000
ARENA_EDGE_THICKNESS = 20


def main() -> None:
    pg.init()

    explosion_sound = pg.mixer.Sound(SOUND_DIRECTORY / "explosion.wav")
    fire_sound = pg.mixer.Sound(SOUND_DIRECTORY / "fire_gun.wav")
    asteroid_break_sound = pg.mixer.Sound(SOUND_DIRECTORY / "asteroid_break.wav")

    utils.setup_window("Polybius Rex")
    fullscreen = True
    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)
    clock = pg.time.Clock()
    font = pg.Font(size=24)
    debug = False

    # The center of the arena is the light source, so you can always locate it.
    light_source = (0, 0)

    game_objects = [
        # Set up the level.
        sprites.Asteroid((100, 100), sprites.HEXAGON_TRIANGLES, Color.WHITE, 20, 35),
        sprites.Asteroid((-100, -100), sprites.SQUARE_TRIANGLES, Color.YELLOW, -40, 35),
        sprites.Asteroid((-200, 200), sprites.TRIANGLE_TRIANGLES, Color.MAGENTA, 80, 20),

        # Create and reference the player object.
        player := sprites.Player((0, 0), sprites.PLAYER_POLYGONS, Color.GREEN),
    ]

    # Particle groups.
    make_image = functools.partial(utils.make_circle_image, color=Color.THRUST, trans_color=Color.BLACK)
    thrust_particles = utils.ParticleGroup(utils.ImageCache(make_image), pg.BLEND_ADD)

    def make_bullet_image(color: tuple[int, int, int]) -> pg.Surface:
        return utils.make_circle_image(sprites.PLAYER_BULLET_RADIUS, color, Color.BLACK)

    bullets = utils.ParticleGroup(utils.ImageCache(make_bullet_image))  # noqa

    def make_debris_image(item: tuple[int, tuple[int, int, int]]) -> pg.Surface:
        return utils.make_circle_image(item[0], item[1], Color.BLACK)

    debris_particles = utils.ParticleGroup(utils.ImageCache(make_debris_image))  # noqa

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    if event.mod & pg.KMOD_CTRL:
                        pg.quit()
                        sys.exit()

                if event.key == pg.K_F3:
                    debug = not debug

                if event.key == pg.K_F4:
                    fullscreen = not fullscreen
                    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == LEFT_MOUSE_BUTTON:
                    player.thrusting = True

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == LEFT_MOUSE_BUTTON:
                    player.thrusting = False

        dt = clock.tick(FPS_CAP) / 1000

        # Spawn particles.
        if player.thrusting:
            vel_vector = utils.polar_vector(random.randint(150, 200), player.angle + 90 + random.randint(-15, 15))
            thrust_particles.add(sprites.ThrustParticle(player.thrust_pos, player.vel + vel_vector))

            if pg.time.get_ticks() - player.last_fire >= sprites.PLAYER_FIRE_RATE:
                fire_sound.play()
                player.last_fire = pg.time.get_ticks()
                vel_vector = utils.polar_vector(-sprites.PLAYER_BULLET_SPEED, player.angle + 90)
                bullets.add(sprites.Bullet(player.gun_pos, player.vel + vel_vector))

        # Update objects and particles.
        game_objects = [go for go in game_objects if go.update(dt, ARENA_RADIUS,
                                                               debris=debris_particles, sound=asteroid_break_sound)]

        thrust_particles.update(dt)
        debris_particles.update(dt)
        bullets.update(dt, arena_radius=ARENA_RADIUS, game_objects=game_objects, ex_sound=explosion_sound)

        # Do camera calculations.
        screen_middle = pg.Vector2(screen.size) / 2
        camera = screen_middle - player.pos
        player.angle = pg.Vector2().angle_to(pg.mouse.get_pos() - screen_middle) + 90

        # Draw everything.
        screen.fill(SCREEN_BACKGROUND_COLOR)

        pg.draw.circle(screen, Color.ARENA_EDGE, camera, ARENA_RADIUS, ARENA_EDGE_THICKNESS)

        for game_object in game_objects:
            game_object.draw(screen, light_source, camera)
            if debug:
                pg.draw.circle(screen, Color.CYAN, game_object.pos + camera, game_object.radius, 1)

        thrust_particles.draw(screen, camera)
        debris_particles.draw(screen, camera)
        bullets.draw(screen, camera)

        if debug:
            fps_surf = font.render(f"{clock.get_fps():.2f}", True, Color.WHITE, Color.BLACK)
            screen.blit(fps_surf, (0, screen.height - fps_surf.height))

        pg.display.flip()


if __name__ == '__main__':
    main()
