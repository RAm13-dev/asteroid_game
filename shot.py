import pygame

from assets import load_sprite
from circleshape import CircleShape
from constants import SHOT_RADIUS, SHOT_LIFETIME_SECONDS

class Shot(CircleShape):

    def __init__(self, x, y):
       super().__init__(x, y, SHOT_RADIUS)
       self.lifetime = SHOT_LIFETIME_SECONDS
       self._sprite = load_sprite("shot", self.radius * 2)
    
    def draw(self, screen):
        if hasattr(screen, "blit"):
            rect = self._sprite.get_rect(center=self.position)
            screen.blit(self._sprite, rect)
    
    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        # Wrap around screen edges
        self.wrap_position()
              
