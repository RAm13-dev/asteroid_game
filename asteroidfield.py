import random

import pygame

from asteroid import Asteroid
from constants import (
    ASTEROID_DIFFICULTY_RAMP_SECONDS,
    ASTEROID_KINDS,
    ASTEROID_MAX_DIFFICULTY_MULTIPLIER,
    ASTEROID_MAX_RADIUS,
    ASTEROID_MIN_RADIUS,
    ASTEROID_ROTATION_MAX,
    ASTEROID_ROTATION_MIN,
    ASTEROID_SPAWN_RATE_SECONDS,
    ASTEROID_SPEED_MAX,
    ASTEROID_SPEED_MIN,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class AsteroidField(pygame.sprite.Sprite):
    """Spawns asteroids at random edges and ramps difficulty over time."""
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        # Track spawn timing and total elapsed play time.
        self.spawn_timer = 0.0
        self.elapsed_time = 0.0

    def spawn(self, radius, position, velocity):
        """Create a new asteroid with the requested size and velocity."""
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt):
        """Advance timers and spawn new asteroids based on difficulty."""
        self.spawn_timer += dt
        self.elapsed_time += dt

        # Ramp difficulty over time to increase pressure.
        difficulty_multiplier = min(
            1 + (self.elapsed_time / ASTEROID_DIFFICULTY_RAMP_SECONDS),
            ASTEROID_MAX_DIFFICULTY_MULTIPLIER,
        )
        # Higher difficulty means more frequent spawns.
        spawn_rate = ASTEROID_SPAWN_RATE_SECONDS / difficulty_multiplier

        if self.spawn_timer > spawn_rate:
            self.spawn_timer = 0
            edge = random.choice(self.edges)
            # Randomize speed within bounds, then scale by difficulty.
            speed = random.randint(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
            velocity = edge[0] * (speed * difficulty_multiplier)
            # Introduce a slight rotation for variety.
            velocity = velocity.rotate(
                random.randint(ASTEROID_ROTATION_MIN, ASTEROID_ROTATION_MAX)
            )
            position = edge[1](random.uniform(0, 1))
            # Choose asteroid size variant based on defined kinds.
            kind = random.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)

    
