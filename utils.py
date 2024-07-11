# This file holds useful utility functions and classes.

from pathlib import Path
import sys

import pygame as pg

from typing import Optional, Sequence, Callable, Hashable, Iterable


class Sounds:
    def __init__(self, sound_folder: Path, muted: bool = False):
        self.muted = muted
        self.sounds: dict[str, pg.mixer.Sound] = {}
        for path in sound_folder.iterdir():
            if path.is_file():
                self.sounds[path.name] = pg.mixer.Sound(path)

    def play(self, sound: str):
        if not self.muted:
            self.sounds[sound].play()


def polar_vector(length: float, angle: float) -> pg.Vector2:
    """Return a Vector2 with the given length and angle in degrees."""
    vec = pg.Vector2()
    vec.from_polar((length, angle))
    return vec


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


def make_circle_image(radius: int, color: Sequence[int], trans_color: Optional[Sequence[int]] = None) -> pg.Surface:
    """Create and return an image with a colored circle and an optional color key.

    The surface size is ``(radius*2,radius*2)``.
    """
    image = pg.Surface((radius * 2, radius * 2))
    pg.draw.circle(image, color, (radius, radius), radius)  # noqa
    if trans_color is not None:
        image.set_colorkey(trans_color)  # noqa
    return image


class ImageCache:
    def __init__(self, make_image_func: Callable[[Hashable], pg.Surface]):
        self.cache: dict[Hashable, pg.Surface] = {}
        self.make_image = make_image_func

    def __len__(self) -> int:
        return len(self.cache)

    @property
    def size(self) -> int:
        return len(self)

    def clear_cache(self):
        self.cache: dict[Hashable, pg.Surface] = {}

    def get_image(self, item: Hashable) -> pg.Surface:
        if item not in self.cache:
            self.cache[item] = self.make_image(item)
        return self.cache[item]


class Particle:
    def update(self, dt: float, *args, **kwargs) -> bool:  # noqa
        """Return False when particle should be removed."""
        return True

    def draw_pos(self, image: pg.Surface) -> Sequence[float]:
        raise NotImplementedError

    def cache_lookup(self) -> Hashable:  # noqa
        return 1


class ParticleGroup:
    def __init__(self, image_cache: ImageCache, blend: int = pg.BLENDMODE_NONE,
                 particles: Optional[list[Particle]] = None):
        self.particles: list[Particle] = particles if particles is not None else []
        self.image_cache = image_cache
        self.blend = blend

    def __len__(self) -> int:
        return len(self.particles)

    @property
    def size(self) -> int:
        return len(self)

    def add(self, particles: Particle | Iterable[Particle]):
        if isinstance(particles, Particle):
            self.particles.append(particles)
        else:
            self.particles.extend(particles)

    def update(self, dt: float, *args, **kwargs):
        self.particles = [p for p in self.particles if p.update(dt, *args, **kwargs)]

    def _get_draw_tuple(self, p: Particle, camera: pg.Vector2) -> tuple[pg.Surface, Sequence[float]]:
        image = self.image_cache.get_image(p.cache_lookup())
        return image, p.draw_pos(image) + camera

    def draw(self, screen: pg.Surface, camera: pg.Vector2, blend: int = pg.BLENDMODE_NONE):
        screen.fblits([self._get_draw_tuple(p, camera) for p in self.particles], blend if blend else self.blend)  # noqa
