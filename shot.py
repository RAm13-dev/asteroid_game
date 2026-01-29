from collections import deque

import pygame

from assets import create_glow_sprite, load_sprite
from circleshape import CircleShape
from constants import SHOT_RADIUS, SHOT_LIFETIME_SECONDS, SHOT_TRAIL_LENGTH, TRAIL_MAX_ALPHA, GLOW_ALPHA

class Shot(CircleShape):

    def __init__(self, x, y):
       super().__init__(x, y, SHOT_RADIUS)
       self.lifetime = SHOT_LIFETIME_SECONDS
       self._sprite = load_sprite("shot", self.radius * 2)
       self._glow = create_glow_sprite(int(self.radius * 6), (140, 220, 255), GLOW_ALPHA)
       self._trail = deque(maxlen=SHOT_TRAIL_LENGTH)
    
    def draw(self, screen):
        if hasattr(screen, "blit"):
            self._draw_trail(screen)
            rect = self._sprite.get_rect(center=self.position)
            screen.blit(self._sprite, rect)
            glow_rect = self._glow.get_rect(center=self.position)
            screen.blit(self._glow, glow_rect)
    
    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        # Wrap around screen edges
        self.wrap_position()
        self._trail.append(self.position.copy())

    def _draw_trail(self, screen):
        if not self._trail or not hasattr(screen, "blit"):
            return
        trail_items = list(self._trail)
        count = len(trail_items)
        for index, pos in enumerate(trail_items):
            alpha = int(TRAIL_MAX_ALPHA * (index + 1) / count)
            trail_sprite = self._sprite.copy()
            if hasattr(trail_sprite, "set_alpha"):
                trail_sprite.set_alpha(alpha)
            rect = trail_sprite.get_rect(center=pos)
            screen.blit(trail_sprite, rect)
              
