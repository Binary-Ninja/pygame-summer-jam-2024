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
FONT_PATH = APPLICATION_DIRECTORY / "Kenney_Future_Narrow.ttf"
FIRE_GUN_SOUND = "fire_gun.wav"

LEFT_MOUSE_BUTTON = 1
WINDOWED_RESOLUTION = pg.Vector2(800, 600)
FPS_CAP = 0
SCREEN_BACKGROUND_COLOR = Color.BLACK

ARENA_RADIUS = 1000
ARENA_EDGE_THICKNESS = 20
SCORE_MULTIPLIER = 1
PLAYER_DAMAGE_FLASH_MS = 200


def main() -> None:
    pg.init()

    sounds = utils.Sounds(SOUND_DIRECTORY, False)

    utils.setup_window("Polybius Rex")
    fullscreen = True
    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)
    clock = pg.time.Clock()
    font = pg.Font(FONT_PATH, 24)
    debug = False
    paused = True
    score = 0
    wave = 1
    death_timer = 0

    # Create the pause menu buttons.
    resume_button = sprites.Button(-200)
    sounds_button = sprites.Button(-100)
    fullscreen_button = sprites.Button(0)
    debug_button = sprites.Button(100)
    quit_button = sprites.Button(200)

    # The center of the arena is the light source, so you can always locate it.
    light_source = (0, 0)

    game_objects = [
        # Set up the level.
        sprites.Asteroid((100, 100), sprites.HEXAGON_TRIANGLES, Color.WHITE,
                         20, 35, (40, -20), 12),
        sprites.Asteroid((-100, -100), sprites.SQUARE_TRIANGLES, Color.YELLOW,
                         -40, 35, (-10, -50), 8),
        sprites.Asteroid((-200, 200), sprites.TRIANGLE_TRIANGLES, Color.MAGENTA,
                         80, 20, (10, 10), 4),

        # Create and reference the player object.
        player := sprites.Player((0, 0), sprites.PLAYER_POLYGONS, Color.GREEN),

        # Create the enemies.
        sprites.EnemyShip((0, -400), sprites.TRIANGLE_TRIANGLES, Color.RED, 20, 10, player),
    ]
    # Make menu button say "PLAY" instead of "RESUME".
    player.dead = True

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

                if event.key == pg.K_ESCAPE:
                    paused = not paused
                    if not paused and player.dead:
                        player.health = 10
                        player.dead = False
                        player.pos = pg.Vector2()
                        player.vel = pg.Vector2()

                if event.key == pg.K_F3:
                    debug = not debug

                if event.key == pg.K_F4:
                    fullscreen = not fullscreen
                    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)

                if event.key == pg.K_m:
                    sounds.muted = not sounds.muted

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == LEFT_MOUSE_BUTTON and not player.dead:
                    player.thrusting = True

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == LEFT_MOUSE_BUTTON:
                    player.thrusting = False

        # Tick the clock.
        dt = clock.tick(FPS_CAP) / 1000

        # Update the game state.
        if not paused:
            # Increase score.
            score += SCORE_MULTIPLIER * dt

            # Increase death timer.
            if player.dead:
                death_timer += dt
                if death_timer > 2:
                    death_timer = 0
                    paused = True

            # Spawn particles.
            if player.thrusting:
                vel_vector = utils.polar_vector(random.randint(150, 200), player.angle + 90 + random.randint(-15, 15))
                thrust_particles.add(sprites.ThrustParticle(player.thrust_pos, player.vel + vel_vector))

                if pg.time.get_ticks() - player.last_fire >= sprites.PLAYER_FIRE_RATE:
                    sounds.play(FIRE_GUN_SOUND)
                    player.last_fire = pg.time.get_ticks()
                    vel_vector = utils.polar_vector(-sprites.PLAYER_BULLET_SPEED, player.angle + 90)
                    bullets.add(sprites.Bullet(player.gun_pos, player.vel + vel_vector, player))

            # Update game objects.
            ngo = [go for go in game_objects if go.update(dt, ARENA_RADIUS, game_objects, sounds,
                                                          d=debris_particles, p=player)]
            # Use a temporary variable to avoid iterating while removing objects (during collision code).
            game_objects = ngo

            # Update particles.
            thrust_particles.update(dt)
            debris_particles.update(dt)
            bullets.update(dt, arena_radius=ARENA_RADIUS, game_objects=game_objects, sounds=sounds)
        # Update the menu.
        else:
            if resume_button.update():
                paused = False
                if player.dead:
                    player.health = 10
                    player.dead = False
                    player.pos = pg.Vector2()
                    player.vel = pg.Vector2()
            if sounds_button.update():
                sounds.muted = not sounds.muted
            if fullscreen_button.update():
                fullscreen = not fullscreen
                screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)
            if debug_button.update():
                debug = not debug
            if quit_button.update():
                pg.quit()
                sys.exit()

        # Update the camera.
        screen_middle = pg.Vector2(screen.size) / 2
        camera = screen_middle - player.pos

        # Rotate the player to face the mouse.
        if not paused:
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

        # Draw player damage flash.
        hp_color = Color.GREEN
        if pg.time.get_ticks() - player.last_hit < PLAYER_DAMAGE_FLASH_MS:
            hp_color = Color.WHITE
            flash_surf = pg.Surface(screen.size)
            flash_surf.fill(Color.DAMAGE_FLASH)
            screen.blit(flash_surf, (0, 0), special_flags=pg.BLEND_ADD)

        # Draw HUD.
        score_surf = font.render(f"SCORE: {int(score)}", True, Color.WHITE)
        screen.blit(score_surf, score_surf.get_rect(centerx=screen.get_rect().centerx))

        wave_text = f"WAVE {wave}: {len(game_objects) - 1} POLYBOIDS REMAINING"
        wave_surf = font.render(wave_text, True, Color.WHITE)
        screen.blit(wave_surf, wave_surf.get_rect(right=screen.width))

        hp_surf = font.render("SHIP", True, Color.WHITE)
        screen.blit(hp_surf, (0, 0))
        for i in range(player.health):
            points = [pg.Vector2((hp_surf.width + 10) + (i * 15), hp_surf.height / 2) + p for p in sprites.HP_POLYGON]
            pg.draw.polygon(screen, hp_color, points)

        if paused:
            resume_button.draw(screen, font, " (ESC) PLAY" if player.dead else " (ESC) RESUME")
            sounds_button.draw(screen, font, f" (M) SOUNDS: {"OFF" if sounds.muted else "ON"}")
            fullscreen_button.draw(screen, font, f" (F4) FULLSCREEN: {"ON" if fullscreen else "OFF"}")
            debug_button.draw(screen, font, f" (F3) DEBUG: {"ON" if debug else "OFF"}")
            quit_button.draw(screen, font, " (CTRL+Q) QUIT", Color.RED)
            help_surf = font.render("MOUSE TO MOVE AND FIRE", True, Color.WHITE)
            screen.blit(help_surf, help_surf.get_rect(centerx=screen.get_rect().centerx, bottom=screen.height))

        if debug:
            fps_surf = font.render(f"{clock.get_fps():.2f}", True, Color.WHITE, Color.BLACK)
            screen.blit(fps_surf, (0, screen.height - fps_surf.height))

        pg.display.flip()


if __name__ == '__main__':
    main()
