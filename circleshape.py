import pygame
import math
# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        # must override
        pass

    def update(self, dt):
        # must override
        pass
    def collides_with(self, other):
        x1 = self.position.x
        y1 = self.position.y

        x2 = other.position.x
        y2 = other.position.y

        dx = x2 - x1
        dy = y2 - y1

        distance = math.sqrt(dx*dx + dy*dy)

        return distance <= self.radius + other.radius
