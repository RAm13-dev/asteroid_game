import random

import pygame

from assets import load_sprite
from circleshape import CircleShape
from constants import (
    ASTEROID_MIN_RADIUS,
    ASTEROID_ROTATION_MAX,
    ASTEROID_ROTATION_MIN,
    ASTEROID_SPLIT_SPEED_MAX,
    ASTEROID_SPLIT_SPEED_MIN,
)
from logger import log_event

class Asteroid(CircleShape):

    def __init__(self, x, y, radius):
       super().__init__(x, y, radius)
       self.rotation = random.uniform(0, 360)
       self.rotation_speed = random.uniform(ASTEROID_ROTATION_MIN, ASTEROID_ROTATION_MAX)
       self._sprite = load_sprite("asteroid", self.radius * 2)
       self._rotation_cache = {}
    
    def draw(self, screen):
        """Render the asteroid with a sprite."""
        sprite = self._get_rotated_sprite()
        if hasattr(screen, "blit"):
            rect = sprite.get_rect(center=self.position)
            screen.blit(sprite, rect)
    
    def update(self, dt):
        """Move the asteroid and wrap it around the screen edges."""
        self.position += self.velocity * dt
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360
        self.wrap_position()

    def _get_rotated_sprite(self):
        angle = int(self.rotation) % 360
        if angle in self._rotation_cache:
            return self._rotation_cache[angle]
        if hasattr(pygame, "transform") and hasattr(pygame.transform, "rotate"):
            rotated = pygame.transform.rotate(self._sprite, angle)
        else:
            rotated = self._sprite
        self._rotation_cache[angle] = rotated
        return rotated
    
    def split(self):
        """Split an asteroid into two smaller ones with randomized speed."""
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        else:
            log_event("asteroid_split")
            angle = random.uniform(20, 50)
            split_speed_multiplier = random.uniform(
                ASTEROID_SPLIT_SPEED_MIN,
                ASTEROID_SPLIT_SPEED_MAX,
            )
            vel_p = self.velocity.rotate(angle)
            vel_n = self.velocity.rotate(-angle)
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            asteroid_p = Asteroid(self.position.x, self.position.y, new_radius)
            asteroid_n = Asteroid(self.position.x, self.position.y, new_radius)
            asteroid_p.velocity = vel_p * split_speed_multiplier
            asteroid_n.velocity = vel_n * split_speed_multiplier
