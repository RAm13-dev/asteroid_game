from collections import deque

import pygame
from assets import create_glow_sprite, load_sprite
import audio
from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS,
    PLAYER_TURN_SPEED,
    PLAYER_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_INVINCIBILITY_SECONDS,
    PLAYER_TRAIL_LENGTH,
    TRAIL_MAX_ALPHA,
    GLOW_ALPHA,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.cooldown = 0
        self.invincibility = 0.0
        self._thrusting = False
        self._sprite = load_sprite("player", self.radius * 2)
        self._engine_glow = create_glow_sprite(int(self.radius * 2.4), (120, 200, 255), GLOW_ALPHA)
        self._rotation_cache = {}
        self._trail = deque(maxlen=PLAYER_TRAIL_LENGTH)
    
    def triangle(self):
        forward = pygame.Vector2(0, -1).rotate(self.rotation)
        right = pygame.Vector2(0, -1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen):
        # Flash when invincible (draw every other frame)
        if self.invincibility <= 0 or int(self.invincibility * 10) % 2 == 0:
            self._draw_trail(screen)
            sprite = self._get_rotated_sprite()
            if hasattr(screen, "blit"):
                rect = sprite.get_rect(center=self.position)
                screen.blit(sprite, rect)
                self._draw_engine_glow(screen)

    def _get_rotated_sprite(self, angle=None):
        angle = int(self.rotation if angle is None else angle) % 360
        if angle in self._rotation_cache:
            return self._rotation_cache[angle]
        if hasattr(pygame, "transform") and hasattr(pygame.transform, "rotate"):
            rotated = pygame.transform.rotate(self._sprite, angle)
        else:
            rotated = self._sprite
        self._rotation_cache[angle] = rotated
        return rotated
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def update(self, dt):
        keys = pygame.key.get_pressed()

        if self._key_pressed(keys, pygame.K_a):
            self.rotate(-dt)
        if self._key_pressed(keys, pygame.K_d):
            self.rotate(dt)
        self._thrusting = False
        if self._key_pressed(keys, pygame.K_w):
            self.move(dt)
            self._thrusting = True
        if self._key_pressed(keys, pygame.K_s):
            self.move(-dt)
            self._thrusting = True
        if self._key_pressed(keys, pygame.K_SPACE) and self.cooldown == 0:
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
        self._trail.append((self.position.copy(), self.rotation))

    @staticmethod
    def _key_pressed(keys, key):
        if keys is None:
            return False
        if hasattr(keys, "get"):
            return keys.get(key, False)
        return bool(keys[key])
    
    def move(self, dt):
        unit_vector = pygame.Vector2(0, -1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self):
        shot = Shot(self.position.x, self.position.y)
        direction = pygame.Vector2(0, -1).rotate(self.rotation)
        shot.velocity = direction * PLAYER_SHOOT_SPEED
        audio.play_sound("shoot")
    
    def is_invincible(self):
        return self.invincibility > 0
    
    def respawn(self):
        """Respawn player at center with invincibility"""
        self.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.velocity = pygame.Vector2(0, 0)
        self.invincibility = PLAYER_INVINCIBILITY_SECONDS

    def _draw_trail(self, screen):
        if not self._trail or not hasattr(screen, "blit"):
            return
        trail_items = list(self._trail)
        count = len(trail_items)
        for index, (pos, angle) in enumerate(trail_items):
            alpha = int(TRAIL_MAX_ALPHA * (index + 1) / count)
            sprite = self._get_rotated_sprite(angle)
            trail_sprite = sprite.copy()
            if hasattr(trail_sprite, "set_alpha"):
                trail_sprite.set_alpha(alpha)
            rect = trail_sprite.get_rect(center=pos)
            screen.blit(trail_sprite, rect)

    def _draw_engine_glow(self, screen):
        if not self._thrusting or not hasattr(screen, "blit"):
            return
        forward = pygame.Vector2(0, -1).rotate(self.rotation)
        glow_pos = self.position - forward * (self.radius * 0.9)
        rect = self._engine_glow.get_rect(center=glow_pos)
        screen.blit(self._engine_glow, rect)
