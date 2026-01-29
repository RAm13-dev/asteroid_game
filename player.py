import pygame
from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS, LINE_WIDTH, PLAYER_TURN_SPEED, PLAYER_SPEED, 
    PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS, 
    PLAYER_INVINCIBILITY_SECONDS, SCREEN_WIDTH, SCREEN_HEIGHT
)
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.cooldown = 0
        self.invincibility = 0.0
    
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen):
        # Flash when invincible (draw every other frame)
        if self.invincibility <= 0 or int(self.invincibility * 10) % 2 == 0:
            pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE] and self.cooldown == 0:
            self.shoot()
            self.cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        
        self.cooldown -= dt
        if self.cooldown < 0:
            self.cooldown = 0
        
        # Update invincibility timer
        if self.invincibility > 0:
            self.invincibility -= dt
            if self.invincibility < 0:
                self.invincibility = 0
        
        # Wrap around screen edges
        self.wrap_position()
    
    def move(self, dt):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self):
        shot = Shot(self.position.x, self.position.y)
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        shot.velocity = direction * PLAYER_SHOOT_SPEED
    
    def is_invincible(self):
        return self.invincibility > 0
    
    def respawn(self):
        """Respawn player at center with invincibility"""
        self.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.velocity = pygame.Vector2(0, 0)
        self.invincibility = PLAYER_INVINCIBILITY_SECONDS
