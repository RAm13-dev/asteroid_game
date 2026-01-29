from constants import LINE_WIDTH, SHOT_RADIUS, SHOT_LIFETIME_SECONDS
from circleshape import CircleShape
import pygame

class Shot(CircleShape):

    def __init__(self, x, y):
       super().__init__(x, y, SHOT_RADIUS)
       self.lifetime = SHOT_LIFETIME_SECONDS
    
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
    
    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        # Wrap around screen edges
        self.wrap_position()
              
