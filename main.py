#!/usr/bin/env python3
# -*- coding: utf8 -*-
import random
import enum
import math
import functools
import sys
from pathlib import Path

import pygame as pg

import utils
import sprites
from sprites import ObjectType

from colors import Color

APPLICATION_DIRECTORY = Path(__file__, "..").resolve()
SOUND_DIRECTORY = APPLICATION_DIRECTORY / "sounds"
FONT_PATH = APPLICATION_DIRECTORY / "Kenney_Future_Narrow.ttf"

LEFT_MOUSE_BUTTON = 1
MIDDLE_MOUSE_BUTTON = 2
RIGHT_MOUSE_BUTTON = 3

GAME_TITLE = "POLYBOIDS"
WINDOWED_RESOLUTION = pg.Vector2(800, 600)
CURSOR_RADIUS = 7
FPS_CAP = 0

MIN_ARENA_EDGE_THICKNESS = 3
ARENA_EDGE_THICKNESS = 10
ARENA_PULSE_MULTIPLIER = 1
ARENA_COLOR_MULTIPLIER = 0.5


class IndicatorStatus(enum.Enum):
    NEVER = enum.auto()
    ALWAYS = enum.auto()
    EMPTY = enum.auto()


INDICATOR_LINE = "OFFSCREEN MARKERS:"
INDICATORS = (IndicatorStatus.NEVER, IndicatorStatus.EMPTY, IndicatorStatus.ALWAYS)
INDICATOR_TEXT = {
    IndicatorStatus.NEVER: "           NEVER SHOW",
    IndicatorStatus.ALWAYS: "         SHOW ALWAYS",
    IndicatorStatus.EMPTY: "WHEN NO ENEMIES IN VIEW",
}
MAX_INDICATOR_SENSE = 2000


def main() -> None:
    pg.init()

    sounds = utils.Sounds(SOUND_DIRECTORY, False)

    utils.setup_window(GAME_TITLE, "window_icon.png")
    fullscreen = True
    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)
    clock = pg.time.Clock()
    font = pg.Font(FONT_PATH, 24)
    big_font = pg.Font(FONT_PATH, 48)
    title_text_surf = big_font.render(GAME_TITLE, True, Color.WHITE)
    wave_clear_surf = big_font.render("WAVE CLEAR", True, Color.WHITE)
    cursor = pg.cursors.Cursor((CURSOR_RADIUS, CURSOR_RADIUS),
                               utils.make_circle_image(CURSOR_RADIUS, Color.WHITE, Color.BLACK, 3))
    pg.mouse.set_cursor(cursor)

    arena_radius = 1000
    debug = False
    effects = True
    show_indicators = IndicatorStatus.ALWAYS
    force_show_indicators = False
    edge_portal = False
    paused = True
    score = 0
    wave = 1
    death_timer = 0
    wave_timer = 0
    enemies_left = 0
    restart_game = False
    new_wave = False
    new_wave_image = big_font.render(f"WAVE {wave}", True, Color.WHITE)
    show_new_wave_image = 0

    arena_pulse = 0
    arena_color = 0
    pulse = 0

    # Create the pause menu buttons.
    resume_button = sprites.Button(-160)
    sounds_button = sprites.Button(-100)
    indicator_button = sprites.Button(-30, 70)
    color_button = sprites.Button(40)
    edge_button = sprites.Button(100)
    fullscreen_button = sprites.Button(160)
    quit_button = sprites.Button(220)

    # The center of the arena is the light source, so you can always locate it.
    light_source = (0, 0)

    # Create and reference the player object.
    game_objects = [player := sprites.Player((0, 0))]
    # Make menu button say "PLAY" instead of "RESUME".
    player.dead = True

    # Particle groups.
    make_image = functools.partial(utils.make_circle_image, color=Color.THRUST, trans_color=Color.BLACK)
    thrust_particles = utils.ParticleGroup(utils.ImageCache(make_image), pg.BLEND_ADD)

    def make_bullet_image(c: tuple[int, int, int]) -> pg.Surface:
        return utils.make_circle_image(sprites.PLAYER_BULLET_RADIUS, c, Color.BLACK)

    bullets = utils.ParticleGroup(utils.ImageCache(make_bullet_image))  # noqa

    def make_debris_image(item: tuple[int, tuple[int, int, int]]) -> pg.Surface:
        return utils.make_circle_image(item[0], item[1], Color.BLACK)

    debris_particles = utils.ParticleGroup(utils.ImageCache(make_debris_image))  # noqa

    def make_nebula_image(item: tuple[int, tuple[int, int, int]]) -> pg.Surface:
        return utils.make_circle_image(item[0], item[1], Color.BLACK)

    nebula_particles = utils.ParticleGroup(utils.ImageCache(make_nebula_image), pg.BLEND_ADD)  # noqa

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

                if event.key == pg.K_ESCAPE or event.key == pg.K_SPACE:
                    paused = not paused
                    if not paused and player.dead:
                        restart_game = True

                if event.key == pg.K_F3:
                    debug = not debug

                if event.key == pg.K_F4:
                    fullscreen = not fullscreen
                    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == LEFT_MOUSE_BUTTON and not player.dead:
                    player.thrusting = True

                # Spawn enemies in debug mode.
                if event.button == MIDDLE_MOUSE_BUTTON and not paused and debug:
                    player.shield = sprites.MAX_SHIELD
                    game_objects.append(o := sprites.Drone(player))
                    o.shield = sprites.MAX_SHIELD

                if event.button == RIGHT_MOUSE_BUTTON:
                    force_show_indicators = True

                if event.button == RIGHT_MOUSE_BUTTON and not paused and debug:
                    world_coords = event.pos - camera + (random.randrange(20), random.randrange(20))  # noqa
                    game_objects.append(sprites.PowerUp(world_coords, (0, 0), random.choice(sprites.RANDOM_POWERUPS)))
                    shape = random.choice(sprites.RANDOM_SHAPES)
                    t = random.choice(sprites.RANDOM_TYPES)
                    t = None
                    d = random.random() + 0
                    o = None
                    if t is ObjectType.ASTEROID:
                        game_objects.append(o := sprites.Asteroid(world_coords, shape))
                    if t is ObjectType.ORBITER:
                        game_objects.append(o := sprites.Orbiter(world_coords, shape))
                    if t is ObjectType.RUNNER:
                        game_objects.append(o := sprites.Runner(world_coords, shape, player))
                    if t is ObjectType.CHASER:
                        game_objects.append(o := sprites.Chaser(world_coords, shape, player))
                    if t is ObjectType.GUNNER:
                        game_objects.append(o := sprites.Gunner(world_coords, shape, player))
                    if o:
                        o.shield = sprites.MAX_SHIELD if random.random() > 0.5 else 0
                    if o is not None and d > 0.5:
                        for _ in range(random.randint(2, 6)):
                            game_objects.append(d := sprites.Drone(o))
                            d.shield = sprites.MAX_SHIELD if random.random() > 0.8 else 0

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == LEFT_MOUSE_BUTTON:
                    player.thrusting = False

                if event.button == RIGHT_MOUSE_BUTTON:
                    force_show_indicators = False

        # Tick the clock.
        dt = clock.tick(FPS_CAP) / 1000

        # Update the game state.
        if not paused:
            # Restart the game.
            if restart_game:
                restart_game = False
                death_timer = 0
                score = 0
                wave = 1
                new_wave_image = big_font.render(f"WAVE {wave}", True, Color.WHITE)
                show_new_wave_image = pg.time.get_ticks()
                new_wave = True
                # Delete remaining particles.
                thrust_particles.clear()
                debris_particles.clear()
                bullets.clear()
                # Clear other objects.
                game_objects = [player]
                # Reset player.
                player.health = sprites.HEALTH[player.shape]
                player.dead = False
                player.pos = pg.Vector2()
                player.vel = pg.Vector2()

            # Set up a new wave.
            if new_wave:
                new_wave = False
                arena_radius = 900 + (wave * 100)
                for _ in range(2 + wave):
                    pos = utils.random_vector(arena_radius, 500)
                    shape = random.choice(sprites.RANDOM_SHAPES)
                    if wave < 3:
                        type_sequence = (ObjectType.ASTEROID, ObjectType.ORBITER)
                    elif wave < 5:
                        type_sequence = (ObjectType.ASTEROID, ObjectType.ORBITER, ObjectType.RUNNER)
                    elif wave < 7:
                        type_sequence = (ObjectType.ASTEROID, ObjectType.ORBITER, ObjectType.RUNNER, ObjectType.CHASER)
                    elif wave < 9:
                        type_sequence = (ObjectType.ASTEROID, ObjectType.ORBITER,
                                         ObjectType.ASTEROID, ObjectType.ORBITER,
                                         ObjectType.RUNNER, ObjectType.CHASER)
                    elif wave < 11:
                        type_sequence = (ObjectType.ASTEROID, ObjectType.ORBITER,
                                         ObjectType.ASTEROID, ObjectType.ORBITER,
                                         ObjectType.RUNNER, ObjectType.CHASER,
                                         ObjectType.GUNNER)
                    else:
                        type_sequence = sprites.RANDOM_TYPES
                    t = random.choice(type_sequence)
                    s = random.random() * wave > 5
                    d = random.random() * wave > 7
                    o = None
                    if t is ObjectType.ASTEROID:
                        game_objects.append(o := sprites.Asteroid(pos, shape))
                    if t is ObjectType.ORBITER:
                        game_objects.append(o := sprites.Orbiter(pos, shape))
                    if t is ObjectType.RUNNER:
                        game_objects.append(o := sprites.Runner(pos, shape, player))
                    if t is ObjectType.CHASER:
                        game_objects.append(o := sprites.Chaser(pos, shape, player))
                    if t is ObjectType.GUNNER:
                        game_objects.append(o := sprites.Gunner(pos, shape, player))
                    if o and s:
                        o.shield = sprites.MAX_SHIELD
                    if o and d:
                        for _ in range(random.randint(1, 5)):
                            game_objects.append(d := sprites.Drone(o))
                            if random.random() > 0.8:
                                d.shield = sprites.MAX_SHIELD

            # Increase death timer.
            if player.dead:
                death_timer += dt
                # If player has been dead for two seconds, pause the game.
                if death_timer > 2:
                    paused = True

            # Update arena pulse.
            arena_color += ARENA_COLOR_MULTIPLIER * dt
            arena_pulse += ARENA_PULSE_MULTIPLIER * dt
            pulse = pg.math.remap(-1, 1, 0, 1, math.sin(arena_pulse))

            # Spawn particles.
            if effects:
                nebula_particles.add(sprites.NebulaParticle())
            if player.thrusting:
                vel_vector = utils.polar_vector(random.randint(150, 200),
                                                player.angle + 90 + random.randint(-15, 15))
                thrust_particles.add(sprites.ThrustParticle(player.thrust_pos, player.vel + vel_vector))

            # Update game objects.
            game_objects = [go for go in game_objects if go.update(dt, arena_radius, game_objects, sounds,
                                                                   d=debris_particles, p=player, s=screen, c=camera,
                                                                   b=bullets, e=edge_portal)]
            # Count remaining enemies.
            enemies_left = len([go for go in game_objects if go.type in sprites.ENEMY_FACTION])

            # Increase wave timer.
            if not enemies_left and not player.dead:
                wave_timer += dt
                # If player has won for two seconds, set up the next wave.
                if wave_timer > 2:
                    wave_timer = 0
                    wave += 1
                    new_wave_image = big_font.render(f"WAVE {wave}", True, Color.WHITE)
                    show_new_wave_image = pg.time.get_ticks()
                    new_wave = True
                    # Delete remaining particles.
                    thrust_particles.clear()
                    debris_particles.clear()
                    bullets.clear()
                    # Reset player.
                    player.pos = pg.Vector2()
                    player.vel = pg.Vector2()
                    player.acc = pg.Vector2()
                    player.thrusting = False
                    # Reset player drones.
                    for go in game_objects:
                        if go.type is ObjectType.PLAYER_DRONE:
                            go.pos = player.pos + utils.random_vector(100, 50)
                            go.vel = (player.pos - go.pos).rotate(random.choice((90, -90)))
                            go.vel.scale_to_length(random.randint(50, 200))
                            go.acc = pg.Vector2()
                            go.turn_speed = random.randint(-100, 100)
                        # Delete all the leftover powerups.
                        if go.type is ObjectType.POWER_UP:
                            go.health = 0

            # Update particles.
            if effects:
                nebula_particles.update(dt, arena_radius=arena_radius)
            thrust_particles.update(dt)
            debris_particles.update(dt)
            # Update bullets and add scoring.
            scores = []
            bullets.update(dt, arena_radius=arena_radius, game_objects=game_objects, sounds=sounds, scores=scores)
            score += sum(scores)
        # Update the menu.
        else:
            # Update the buttons.
            if resume_button.update():
                paused = False
                if player.dead:
                    restart_game = True
            if sounds_button.update():
                sounds.muted = not sounds.muted
                if not sounds.muted:
                    sounds.play("fire_gun.wav")
            if indicator_button.update():
                show_indicators = INDICATORS[(INDICATORS.index(show_indicators) + 1) % len(INDICATORS)]
            if color_button.update():
                effects = not effects
            if edge_button.update():
                edge_portal = not edge_portal
            if fullscreen_button.update():
                fullscreen = not fullscreen
                screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)
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

        # Fill the screen.
        if effects:
            int_color = int(arena_color)
            color1 = Color.ARENA_COLORS[int_color % len(Color.ARENA_COLORS)]
            color2 = Color.ARENA_COLORS[(int_color + 1) % len(Color.ARENA_COLORS)]
            screen.fill(pg.Color(color1).lerp(color2, arena_color - int_color))
            # Draw the nebula particles.
            nebula_particles.draw(screen, camera)
        else:
            screen.fill(Color.ARENA_COLOR)

        # Draw the arena boundary.
        if effects:
            color = pg.Color(Color.ARENA_EDGE).lerp(Color.BRIGHT_ARENA_EDGE, pulse)
            thickness = int(pg.math.lerp(ARENA_EDGE_THICKNESS, MIN_ARENA_EDGE_THICKNESS, pulse))
            pg.draw.circle(screen, color, camera, arena_radius, thickness)
        else:
            pg.draw.circle(screen, Color.ARENA_EDGE, camera, arena_radius, ARENA_EDGE_THICKNESS)

        # Draw the game objects.
        enemies_not_on_screen = []
        for go in game_objects:
            # Detect offscreen enemies.
            if go.type in sprites.ENEMY_FACTION and not go.on_screen(screen, camera):
                enemies_not_on_screen.append(go)
            # Draw the game object.
            go.draw(screen, light_source, camera)
            # Draw the collision circles.
            if debug:
                pg.draw.circle(screen, Color.CYAN, go.pos + camera, go.radius, 1)

        # Draw the particles.
        debris_particles.draw(screen, camera)
        thrust_particles.draw(screen, camera)
        bullets.draw(screen, camera)

        # Draw offscreen enemy indicators.
        # Indicators are triangles that point towards the enemy.
        # This essentially creates a minimap for the player to locate the remaining enemies.
        # It also provides useful info like whether the enemy is approaching and how fast it is going.
        if not player.dead and ((show_indicators is not IndicatorStatus.NEVER) or force_show_indicators):
            # Show the indicators if they should always be shown or if there are no enemies on screen.
            if show_indicators is IndicatorStatus.ALWAYS or \
                    len(enemies_not_on_screen) == enemies_left or force_show_indicators:
                for go in enemies_not_on_screen:
                    draw_vec = go.pos - player.pos
                    # The triangle is filled if the enemy is approaching, hollow otherwise.
                    width = 2 if (draw_vec * (go.vel - player.vel)) > 0 else 0
                    # The triangle is further away if the enemy is further away.
                    # Using a hard limit instead of scaling by arena radius provides more useful info.
                    # Enemies outside the max sensor range will have their indicators darkened.
                    if draw_vec.length_squared() > MAX_INDICATOR_SENSE ** 2:
                        offset = 200
                        color = sprites.darken(go.color, 0.5)
                    else:
                        offset = pg.math.remap(0, MAX_INDICATOR_SENSE ** 2, 25, 200,
                                               draw_vec.length_squared())
                        color = go.color
                    draw_vec.scale_to_length(offset)
                    # Create the two other points to make an equilateral triangle.
                    v1 = draw_vec.rotate(210)
                    v1.scale_to_length(15)
                    v2 = draw_vec.rotate(-210)
                    v2.scale_to_length(15)
                    # Center the triangle point in the screen.
                    draw_vec += screen_middle
                    # Draw the enemy indicator.
                    pg.draw.polygon(screen, color, (v1 + draw_vec, draw_vec, v2 + draw_vec), width)

        # Draw player damage flash.
        flash_hp = False
        if (pg.time.get_ticks() - player.last_hit < sprites.DAMAGE_FLASH_MS and
                (player.shield_bypass or player.shield <= 0)):
            flash_hp = True
            flash_surf = pg.Surface(screen.size)
            flash_surf.fill(Color.DAMAGE_FLASH)
            screen.blit(flash_surf, (0, 0), special_flags=pg.BLEND_ADD)

        # Draw wave clear image.
        if not paused and wave_timer > 0:
            screen.blit(wave_clear_surf, wave_clear_surf.get_rect(centerx=screen.get_rect().centerx, y=150))

        # Draw new wave image.
        if pg.time.get_ticks() - show_new_wave_image < 2000 and not paused:
            screen.blit(new_wave_image, new_wave_image.get_rect(centerx=screen.get_rect().centerx, y=150))

        # Draw HUD.
        score_surf = font.render(f"SCORE: {int(score)}", True, Color.WHITE)
        screen.blit(score_surf, score_surf.get_rect(centerx=screen.get_rect().centerx, top=25))

        wave_surf = font.render(f"WAVE {wave}", True, Color.WHITE)
        screen.blit(wave_surf, wave_surf.get_rect(centerx=screen.get_rect().centerx))

        plural = "S" if enemies_left != 1 else ""
        plural2 = "S" if enemies_left == 1 else ""
        wave_surf = font.render(f"{enemies_left} POLYBOID{plural} REMAIN{plural2}", True, Color.WHITE)
        screen.blit(wave_surf, wave_surf.get_rect(right=screen.width))

        # Draw ship health.
        hp_surf = font.render("SHIP", True, Color.WHITE)
        screen.blit(hp_surf, (0, 0))
        hp_color = Color.GREEN
        for i in range(player.health):
            if i >= 15:
                hp_color = Color.CYAN
            if i >= 30:
                hp_color = Color.WHITE
            points = [pg.Vector2((hp_surf.width + 10) + ((i % 15) * 15), hp_surf.height / 2) + p
                      for p in sprites.HP_POLYGON]
            pg.draw.polygon(screen, Color.RED if flash_hp else hp_color, points)

        # Draw menu buttons.
        if paused:
            screen.blit(title_text_surf, title_text_surf.get_rect(centerx=screen.get_rect().centerx, y=50))
            resume_button.draw(screen, font, " (SPACE) PLAY" if player.dead else " (SPACE) RESUME")
            sounds_button.draw(screen, font, f" SOUNDS: {"OFF" if sounds.muted else "ON"}")
            edge_button.draw(screen, font, f"ARENA EDGE: {"PORTAL" if edge_portal else "BOUNCE"}")
            indicator_button.draw(screen, font, f"{INDICATOR_LINE}\n{INDICATOR_TEXT[show_indicators]}")
            color_button.draw(screen, font, f" ARENA EFFECTS: {"ON" if effects else "OFF"}")
            fullscreen_button.draw(screen, font, f" (F4) FULLSCREEN: {"ON" if fullscreen else "OFF"}")
            quit_button.draw(screen, font, " (CTRL+Q) QUIT", Color.RED)
            help_surf = font.render("MOUSE TO MOVE, LEFT CLICK TO FIRE AND THRUST", True, Color.WHITE)
            screen.blit(help_surf, help_surf.get_rect(centerx=screen.get_rect().centerx, bottom=screen.height - 25))
            help_surf = font.render("RIGHT CLICK TO VIEW OFFSCREEN MARKERS", True, Color.WHITE)
            screen.blit(help_surf, help_surf.get_rect(centerx=screen.get_rect().centerx, bottom=screen.height))

        if debug:
            fps_surf = font.render(f"{nebula_particles.size}\n{clock.get_fps():.2f}", True, Color.WHITE, Color.BLACK)
            screen.blit(fps_surf, (0, screen.height - fps_surf.height))

        pg.display.flip()


if __name__ == '__main__':
    main()
