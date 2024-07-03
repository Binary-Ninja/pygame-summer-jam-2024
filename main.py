#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys

import pygame as pg

import utils
import sprites

from colors import Color


WINDOWED_RESOLUTION = pg.Vector2(800, 600)
FPS_CAP = 0
SCREEN_BACKGROUND_COLOR = Color.BLACK


def main() -> None:
    pg.init()

    utils.setup_window("Hyper Hexagon")
    fullscreen = False
    screen = utils.create_display(WINDOWED_RESOLUTION, fullscreen)
    clock = pg.time.Clock()
    font = pg.Font(size=24)

    asteroid = sprites.Asteroid(WINDOWED_RESOLUTION / 2)

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

        dt = clock.tick(FPS_CAP) / 1000

        asteroid.update(dt)

        screen.fill(SCREEN_BACKGROUND_COLOR)

        asteroid.draw(screen, pg.mouse.get_pos())

        fps_surf = font.render(f"{clock.get_fps():.2f}", True, Color.WHITE, Color.BLACK)
        screen.blit(fps_surf, (0, screen.height - fps_surf.height))

        pg.display.flip()


if __name__ == '__main__':
    main()
