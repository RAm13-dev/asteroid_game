import pygame

import random

from asteroid import Asteroid

from constants import (
    ASTEROID_DIFFICULTY_RAMP_SECONDS,
    ASTEROID_KINDS,
    ASTEROID_MAX_DIFFICULTY_MULTIPLIER,
    ASTEROID_MAX_RADIUS,
    ASTEROID_MIN_RADIUS,
    ASTEROID_SPAWN_RATE_SECONDS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)





class AsteroidField(pygame.sprite.Sprite):

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

                self.spawn_timer = 0.0
                self.elapsed_time = 0.0
                self.difficulty_multiplier = 1.0
                self.spawn_rate = ASTEROID_SPAWN_RATE_SECONDS



        def spawn(self, radius, position, velocity):

                asteroid = Asteroid(position.x, position.y, radius)

                asteroid.velocity = velocity
            
        def update(self, dt):

            self.elapsed_time += dt
            ramp_progress = min(
                self.elapsed_time / ASTEROID_DIFFICULTY_RAMP_SECONDS,
                1.0,
            )
            self.difficulty_multiplier = min(
                1.0 + ramp_progress * (ASTEROID_MAX_DIFFICULTY_MULTIPLIER - 1.0),
                ASTEROID_MAX_DIFFICULTY_MULTIPLIER,
            )
            self.spawn_rate = ASTEROID_SPAWN_RATE_SECONDS / self.difficulty_multiplier

            self.spawn_timer += dt

            if self.spawn_timer > self.spawn_rate:

                self.spawn_timer = 0
                edge = random.choice(self.edges)

                speed = random.randint(40, 100)

                velocity = edge[0] * speed

                velocity = velocity.rotate(random.randint(-30, 30))
                velocity = velocity * self.difficulty_multiplier

                position = edge[1](random.uniform(0, 1))

                kind = random.randint(1, ASTEROID_KINDS)

                self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)








   

    

   

    

    

   

    
