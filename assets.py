from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pygame

SPRITES_DIR = Path(__file__).resolve().parent / "assets" / "sprites"
_SPRITE_CACHE: Dict[Tuple[str, Tuple[int, int] | None], pygame.Surface] = {}


def _surface_size(size: int | Tuple[int, int] | None) -> Tuple[int, int] | None:
    if size is None:
        return None
    if isinstance(size, int):
        return (size, size)
    return size


def _create_placeholder(size: Tuple[int, int]) -> pygame.Surface:
    try:
        surface = pygame.Surface(size, getattr(pygame, "SRCALPHA", 0))
    except TypeError:
        surface = pygame.Surface(size)
    if hasattr(surface, "fill"):
        surface.fill((255, 255, 255, 255))
    return surface


def _load_from_disk(name: str) -> pygame.Surface | None:
    if not hasattr(pygame, "image") or not hasattr(pygame.image, "load"):
        return None
    for ext in ("png", "webp"):
        path = SPRITES_DIR / f"{name}.{ext}"
        if path.exists():
            try:
                image = pygame.image.load(str(path))
                if hasattr(image, "convert_alpha"):
                    image = image.convert_alpha()
                return image
            except Exception:
                return None
    return None


def load_sprite(name: str, size: int | Tuple[int, int] | None = None) -> pygame.Surface:
    target_size = _surface_size(size)
    cache_key = (name, target_size)
    if cache_key in _SPRITE_CACHE:
        return _SPRITE_CACHE[cache_key]

    image = _load_from_disk(name)
    if image is None:
        placeholder_size = target_size or (1, 1)
        image = _create_placeholder(placeholder_size)

    if target_size is not None and hasattr(pygame, "transform"):
        if hasattr(pygame.transform, "smoothscale"):
            image = pygame.transform.smoothscale(image, target_size)
        elif hasattr(pygame.transform, "scale"):
            image = pygame.transform.scale(image, target_size)
        else:
            image = _create_placeholder(target_size)
    elif target_size is not None and hasattr(image, "size"):
        image = _create_placeholder(target_size)

    _SPRITE_CACHE[cache_key] = image
    return image
