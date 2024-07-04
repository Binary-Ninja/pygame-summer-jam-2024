#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys

import pygame as pg

import utils
import sprites

from colors import Color

LEFT_MOUSE_BUTTON = 1
WINDOWED_RESOLUTION = pg.Vector2(800, 600)
FPS_CAP = 0
SCREEN_BACKGROUND_COLOR = Color.BLACK
PLAYER_THRUST = 500


def main() -> None:
    pg.init()

    utils.setup_window("Hyper Hexagon")
    fullscreen = True
    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)
    clock = pg.time.Clock()
    font = pg.Font(size=24)

    # The center of the arena is the light source, so you can always locate it.
    light_source = (0, 0)

    game_objects = [
        # Set up the level.
        sprites.Asteroid((100, 100), sprites.HEXAGON_TRIANGLES, Color.WHITE, 20),
        sprites.Asteroid((0, 0), sprites.SQUARE_TRIANGLES, Color.YELLOW, -40),

        # Create and reference the player object.
        player := sprites.Player((0, 0), sprites.PLAYER_POLYGONS, Color.GREEN)
    ]

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

                if event.key == pg.K_F4:
                    fullscreen = not fullscreen
                    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == LEFT_MOUSE_BUTTON:
                    player.acc.from_polar((-PLAYER_THRUST, player.angle + 90))

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == LEFT_MOUSE_BUTTON:
                    player.acc.scale_to_length(0)

        dt = clock.tick(FPS_CAP) / 1000

        for game_object in game_objects:
            game_object.update(dt)

        # Do camera calculations.
        screen_middle = pg.Vector2(screen.size) / 2
        camera = screen_middle - player.pos
        player.angle = pg.Vector2().angle_to(pg.mouse.get_pos() - screen_middle) + 90

        screen.fill(SCREEN_BACKGROUND_COLOR)

        for game_object in game_objects:
            game_object.draw(screen, light_source, camera)

        fps_surf = font.render(f"{clock.get_fps():.2f}", True, Color.WHITE, Color.BLACK)
        screen.blit(fps_surf, (0, screen.height - fps_surf.height))

        pg.display.flip()


if __name__ == '__main__':
    main()
