import math
import random

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class BackgroundParticle:
    def __init__(self, x, y, radius, color, base_alpha, twinkle_speed, phase):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.base_alpha = base_alpha
        self.twinkle_speed = twinkle_speed
        self.phase = phase

    def update(self, dt, velocity):
        self.x = (self.x + velocity[0] * dt) % SCREEN_WIDTH
        self.y = (self.y + velocity[1] * dt) % SCREEN_HEIGHT
        self.phase = (self.phase + self.twinkle_speed * dt) % (math.tau)

    def draw(self, surface):
        twinkle = 0.65 + 0.35 * math.sin(self.phase)
        alpha = max(0, min(255, int(self.base_alpha * twinkle)))
        if alpha == 0:
            return
        color = (*self.color, alpha)
        pygame.draw.circle(
            surface,
            color,
            (int(self.x), int(self.y)),
            max(1, int(self.radius)),
        )


class BackgroundLayer:
    def __init__(
        self,
        particle_count,
        speed,
        radius_range,
        color_range,
        alpha_range,
        twinkle_speed_range,
        drift=(0.0, 1.0),
    ):
        self.velocity = (drift[0] * speed, drift[1] * speed)
        self.radius_range = radius_range
        self.color_range = color_range
        self.alpha_range = alpha_range
        self.twinkle_speed_range = twinkle_speed_range
        self.particles = [self._make_particle() for _ in range(particle_count)]

    def _rand_color_channel(self, idx):
        return random.randint(self.color_range[0][idx], self.color_range[1][idx])

    def _make_particle(self):
        x = random.uniform(0, SCREEN_WIDTH)
        y = random.uniform(0, SCREEN_HEIGHT)
        radius = random.uniform(*self.radius_range)
        color = (
            self._rand_color_channel(0),
            self._rand_color_channel(1),
            self._rand_color_channel(2),
        )
        base_alpha = random.uniform(*self.alpha_range)
        twinkle_speed = random.uniform(*self.twinkle_speed_range)
        phase = random.uniform(0.0, math.tau)
        return BackgroundParticle(x, y, radius, color, base_alpha, twinkle_speed, phase)

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt, self.velocity)

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


def build_background_layers():
    return [
        BackgroundLayer(
            particle_count=180,
            speed=12.0,
            radius_range=(0.6, 1.6),
            color_range=((180, 200, 220), (220, 230, 255)),
            alpha_range=(110, 170),
            twinkle_speed_range=(0.4, 0.9),
            drift=(0.0, 1.0),
        ),
        BackgroundLayer(
            particle_count=120,
            speed=24.0,
            radius_range=(1.2, 2.4),
            color_range=((160, 180, 200), (210, 235, 255)),
            alpha_range=(120, 190),
            twinkle_speed_range=(0.6, 1.2),
            drift=(0.05, 1.0),
        ),
        BackgroundLayer(
            particle_count=60,
            speed=36.0,
            radius_range=(3.0, 6.0),
            color_range=((80, 100, 140), (140, 170, 210)),
            alpha_range=(70, 130),
            twinkle_speed_range=(0.3, 0.7),
            drift=(0.1, 1.0),
        ),
    ]
