# This file holds useful utility functions and classes.

from pathlib import Path
import sys

import pygame as pg

from typing import Optional, Sequence


def load_image(filename: str | Path, convert: bool = True, alpha: bool = False) -> pg.Surface:
    """Load and return a ``Surface`` object from the given filename.

    The arguments ``convert`` and ``alpha`` specify whether to convert the surface to display format via
    ``Surface.convert()`` and ``Surface.convert_alpha()``, respectively. If ``convert`` is ``False``, ``alpha``
    has no effect.
    """
    image = pg.image.load(filename)
    if convert:
        if alpha:
            return image.convert_alpha()
        return image.convert()
    return image


def setup_window(title: str, icon_path: Optional[str | Path] = None, big_icon_path: Optional[str | Path] = None):
    """Set the window title and icon image from an image file.

    If ``big_icon_path`` is provided, it will be used when running on macOS.
    """
    pg.display.set_caption(title)
    if big_icon_path and sys.platform == "darwin":
        icon_image = load_image(big_icon_path, False)
        pg.display.set_icon(icon_image)
    elif icon_path:
        icon_image = load_image(icon_path, False)
        pg.display.set_icon(icon_image)


def create_display(size: Sequence[float], fullscreen: bool, flags: int = 0) -> pg.Surface:
    """Toggle the display to and from fullscreen. Fullscreen resolution is the display size."""
    if fullscreen:
        return pg.display.set_mode((0, 0), pg.FULLSCREEN | flags)
    return pg.display.set_mode(size, flags)  # noqa
