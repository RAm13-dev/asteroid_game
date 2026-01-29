import random

import pygame


class Particle(pygame.sprite.Sprite):
    def __init__(
        self,
        position,
        velocity,
        lifetime,
        color,
        alpha,
        size,
    ):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.lifetime = float(lifetime)
        self._max_lifetime = max(self.lifetime, 0.001)
        self.color = color
        self.alpha = int(alpha)
        self.size = int(size)
        self._base_surface = self._build_surface()

    def _build_surface(self):
        try:
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        except TypeError:
            surface = pygame.Surface((self.size * 2, self.size * 2))
        if hasattr(pygame, "draw") and hasattr(pygame.draw, "circle"):
            pygame.draw.circle(
                surface,
                (*self.color, 255),
                (self.size, self.size),
                self.size,
            )
        return surface

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
        if not hasattr(screen, "blit") or self.lifetime <= 0:
            return
        fade = max(self.lifetime / self._max_lifetime, 0.0)
        surface = self._base_surface.copy()
        if hasattr(surface, "set_alpha"):
            surface.set_alpha(int(self.alpha * fade))
        rect = surface.get_rect(center=self.position)
        screen.blit(surface, rect)


class ParticleBurst(pygame.sprite.Sprite):
    def __init__(
        self,
        position,
        count,
        speed_range,
        life_range,
        size_range,
        color,
        alpha,
    ):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.position = pygame.Vector2(position)
        self.count = int(count)
        self.speed_range = speed_range
        self.life_range = life_range
        self.size_range = size_range
        self.color = color
        self.alpha = alpha
        self._spawned = False

    def update(self, dt):
        if self._spawned:
            return
        self._spawned = True
        for _ in range(self.count):
            angle = random.uniform(0, 360)
            speed = random.uniform(*self.speed_range)
            velocity = pygame.Vector2(speed, 0).rotate(angle)
            lifetime = random.uniform(*self.life_range)
            size = random.randint(*self.size_range)
            Particle(
                position=self.position,
                velocity=velocity,
                lifetime=lifetime,
                color=self.color,
                alpha=self.alpha,
                size=size,
            )
        self.kill()
