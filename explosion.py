import pygame

from assets import load_sprite_sheet
from constants import (
    EXPLOSION_COLUMNS,
    EXPLOSION_FRAME_SIZE,
    EXPLOSION_FRAME_TIME,
    EXPLOSION_ROWS,
)


_FRAME_CACHE = {}


def _get_frames(size):
    key = int(size)
    if key in _FRAME_CACHE:
        return _FRAME_CACHE[key]
    frames = load_sprite_sheet(
        "explosion",
        (EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_SIZE),
        EXPLOSION_COLUMNS,
        EXPLOSION_ROWS,
    )
    if key != EXPLOSION_FRAME_SIZE:
        scaled = []
        for frame in frames:
            if hasattr(pygame, "transform") and hasattr(pygame.transform, "smoothscale"):
                scaled.append(pygame.transform.smoothscale(frame, (key, key)))
            elif hasattr(pygame, "transform") and hasattr(pygame.transform, "scale"):
                scaled.append(pygame.transform.scale(frame, (key, key)))
            else:
                scaled.append(frame)
        frames = scaled
    _FRAME_CACHE[key] = frames
    return frames


class Explosion(pygame.sprite.Sprite):
    def __init__(self, position, size):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.position = pygame.Vector2(position)
        self.frames = _get_frames(size)
        self.frame_index = 0
        self.elapsed = 0.0

    def update(self, dt):
        if not self.frames:
            self.kill()
            return
        self.elapsed += dt
        while self.elapsed >= EXPLOSION_FRAME_TIME:
            self.elapsed -= EXPLOSION_FRAME_TIME
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
                return

    def draw(self, screen):
        if not self.frames or not hasattr(screen, "blit"):
            return
        frame = self.frames[min(self.frame_index, len(self.frames) - 1)]
        rect = frame.get_rect(center=self.position)
        screen.blit(frame, rect)
