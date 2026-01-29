from constants import (
    LINE_WIDTH,
    ASTEROID_MIN_RADIUS,
    ASTEROID_SPLIT_SPEED_MIN,
    ASTEROID_SPLIT_SPEED_MAX,
)
from circleshape import CircleShape
from logger import log_event
import pygame
import random

class Asteroid(CircleShape):

    def __init__(self, x, y, radius):
       super().__init__(x, y, radius)
    
    def draw(self, screen):
        """Render the asteroid as a simple outlined circle."""
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
    
    def update(self, dt):
        """Move the asteroid and wrap it around the screen edges."""
        self.position += self.velocity * dt
        self.wrap_position()
    
    def split(self):
        """Split an asteroid into two smaller ones with randomized speed."""
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        log_event("asteroid_split")
        angle = random.uniform(20, 50)
        vel_p = self.velocity.rotate(angle)
        vel_n = self.velocity.rotate(-angle)
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        asteroid_p = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid_n = Asteroid(self.position.x, self.position.y, new_radius)
        speed_multiplier = random.uniform(
            ASTEROID_SPLIT_SPEED_MIN,
            ASTEROID_SPLIT_SPEED_MAX,
        )
        asteroid_p.velocity = vel_p * speed_multiplier
        asteroid_n.velocity = vel_n * speed_multiplier
