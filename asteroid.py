from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from circleshape import CircleShape
from logger import log_event
import pygame
import random

class Asteroid(CircleShape):

    def __init__(self, x, y, radius):
       super().__init__(x, y, radius)
    
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
    def update(self, dt):
        self.position += self.velocity * dt
    def split(self):
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        else:
            log_event("asteroid_split")
            angle = random.uniform(20, 50)
            vel_p = self.velocity.rotate(angle)
            vel_n = self.velocity.rotate(-angle)
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            asteroid_p = Asteroid(self.position.x, self.position.y, new_radius)
            asteroid_n = Asteroid(self.position.x, self.position.y, new_radius)
            asteroid_p.velocity = vel_p * 1.2
            asteroid_n.velocity = vel_n * 1.2

