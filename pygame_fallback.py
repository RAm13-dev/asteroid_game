"""Fallback pygame shim for environments without pygame installed."""
from __future__ import annotations

import math
import sys
import types
from typing import Iterable, Optional


def ensure_pygame():
    """Return pygame module, falling back to a minimal stub if unavailable."""
    try:
        import pygame  # type: ignore
        return pygame
    except ModuleNotFoundError:
        pygame = types.ModuleType("pygame")

        class Vector2:
            __slots__ = ("x", "y")

            def __init__(self, x: float = 0.0, y: float = 0.0):
                if isinstance(x, Vector2):
                    self.x = float(x.x)
                    self.y = float(x.y)
                elif isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
                    values = list(x)
                    self.x = float(values[0])
                    self.y = float(values[1]) if len(values) > 1 else 0.0
                else:
                    self.x = float(x)
                    self.y = float(y)

            def __add__(self, other: "Vector2") -> "Vector2":
                return Vector2(self.x + other.x, self.y + other.y)

            def __sub__(self, other: "Vector2") -> "Vector2":
                return Vector2(self.x - other.x, self.y - other.y)

            def __mul__(self, value: float) -> "Vector2":
                scale = float(value)
                return Vector2(self.x * scale, self.y * scale)

            def __rmul__(self, value: float) -> "Vector2":
                return self.__mul__(value)

            def __iadd__(self, other: "Vector2") -> "Vector2":
                self.x += other.x
                self.y += other.y
                return self

            def rotate(self, degrees: float) -> "Vector2":
                radians = math.radians(degrees)
                cos_a = math.cos(radians)
                sin_a = math.sin(radians)
                return Vector2(
                    self.x * cos_a - self.y * sin_a,
                    self.x * sin_a + self.y * cos_a,
                )

            def length(self) -> float:
                return round(math.hypot(self.x, self.y), 6)

            def __eq__(self, other: object) -> bool:
                if not isinstance(other, Vector2):
                    return False
                return math.isclose(self.x, other.x, rel_tol=1e-6, abs_tol=1e-6) and math.isclose(
                    self.y, other.y, rel_tol=1e-6, abs_tol=1e-6
                )

            def __repr__(self) -> str:
                return f"Vector2({self.x}, {self.y})"

        class Sprite:
            def __init__(self, *groups):
                self._groups = set()
                for group in groups:
                    group.add(self)
                    self._groups.add(group)

            def kill(self):
                for group in list(self._groups):
                    group.remove(self)
                self._groups.clear()

        class Group:
            def __init__(self):
                self._sprites = set()

            def add(self, *sprites):
                self._sprites.update(sprites)

            def remove(self, sprite):
                self._sprites.discard(sprite)

            def __contains__(self, item):
                return item in self._sprites

        class Surface:
            def __init__(self, size, *_args, **_kwargs):
                self.size = size

            def fill(self, *_args, **_kwargs):
                return None

            def get_rect(self, **kwargs):
                center = kwargs.get("center", (0, 0))
                return types.SimpleNamespace(center=center)

        class key:
            @staticmethod
            def get_pressed():
                return {}

        class draw:
            @staticmethod
            def polygon(*_args, **_kwargs):
                return None

        def init():
            return (0, 0)

        def quit():
            return None

        pygame.Vector2 = Vector2
        pygame.sprite = types.SimpleNamespace(Sprite=Sprite, Group=Group)
        pygame.Surface = Surface
        pygame.key = key
        pygame.draw = draw
        pygame.init = init
        pygame.quit = quit

        pygame.K_a = "K_a"
        pygame.K_d = "K_d"
        pygame.K_w = "K_w"
        pygame.K_s = "K_s"
        pygame.K_SPACE = "K_SPACE"

        sys.modules["pygame"] = pygame
        return pygame
