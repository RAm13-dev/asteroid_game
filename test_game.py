"""
Comprehensive test suite for the Asteroids game.
Run with: pytest test_game.py -v
"""
import pytest
import pygame
import math
from unittest.mock import Mock, patch, MagicMock

# Initialize pygame for testing (headless mode)
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

from circleshape import CircleShape
from player import Player
from asteroid import Asteroid
from shot import Shot
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_RADIUS, ASTEROID_MIN_RADIUS,
    PLAYER_SPEED, PLAYER_TURN_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_INVINCIBILITY_SECONDS, SHOT_LIFETIME_SECONDS,
    SCORE_SMALL_ASTEROID, SCORE_MEDIUM_ASTEROID, SCORE_LARGE_ASTEROID
)


class TestCircleShape:
    """Tests for the base CircleShape class"""
    
    def test_initialization(self):
        """Test that CircleShape initializes correctly"""
        shape = CircleShape(100, 200, 30)
        assert shape.position.x == 100
        assert shape.position.y == 200
        assert shape.radius == 30
        assert shape.velocity.x == 0
        assert shape.velocity.y == 0
    
    def test_collision_detection(self):
        """Test collision detection between two shapes"""
        shape1 = CircleShape(100, 100, 20)
        shape2 = CircleShape(120, 100, 20)  # 20 units away, touching
        
        assert shape1.collides_with(shape2) == True
        
        shape3 = CircleShape(150, 100, 20)  # 50 units away, not touching
        assert shape1.collides_with(shape3) == False
    
    def test_wrap_position_right_edge(self):
        """Test wrapping when object goes off right edge"""
        shape = CircleShape(SCREEN_WIDTH + 10, 100, 20)
        shape.wrap_position()
        assert shape.position.x == -20  # Should wrap to left side
    
    def test_wrap_position_left_edge(self):
        """Test wrapping when object goes off left edge"""
        shape = CircleShape(-10, 100, 20)
        shape.wrap_position()
        assert shape.position.x == SCREEN_WIDTH + 20  # Should wrap to right side
    
    def test_wrap_position_bottom_edge(self):
        """Test wrapping when object goes off bottom edge"""
        shape = CircleShape(100, SCREEN_HEIGHT + 10, 20)
        shape.wrap_position()
        assert shape.position.y == -20  # Should wrap to top
    
    def test_wrap_position_top_edge(self):
        """Test wrapping when object goes off top edge"""
        shape = CircleShape(100, -10, 20)
        shape.wrap_position()
        assert shape.position.y == SCREEN_HEIGHT + 20  # Should wrap to bottom
    
    def test_wrap_position_no_wrap_needed(self):
        """Test that wrapping doesn't change position when on screen"""
        shape = CircleShape(100, 100, 20)
        original_x = shape.position.x
        original_y = shape.position.y
        shape.wrap_position()
        assert shape.position.x == original_x
        assert shape.position.y == original_y


class TestPlayer:
    """Tests for the Player class"""
    
    def test_initialization(self):
        """Test player initialization"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        assert player.rotation == 0
        assert player.cooldown == 0
        assert player.invincibility == 0.0
        assert player.radius == PLAYER_RADIUS
    
    def test_rotation(self):
        """Test player rotation"""
        player = Player(100, 100)
        initial_rotation = player.rotation
        dt = 0.1
        
        player.rotate(dt)
        expected_rotation = initial_rotation + PLAYER_TURN_SPEED * dt
        assert abs(player.rotation - expected_rotation) < 0.001
    
    def test_move_forward(self):
        """Test player movement forward"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.rotation = 0  # Facing up (negative Y)
        initial_y = player.position.y
        dt = 0.1
        
        player.move(dt)
        # Should move forward (negative Y direction when rotation is 0)
        assert player.position.y < initial_y
    
    def test_move_backward(self):
        """Test player movement backward"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.rotation = 0
        initial_y = player.position.y
        dt = 0.1
        
        player.move(-dt)  # Negative dt for backward
        # Should move backward (positive Y direction)
        assert player.position.y > initial_y
    
    def test_shoot_creates_shot(self):
        """Test that shooting creates a shot"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.rotation = 0
        
        # Mock Shot class to track creation
        shots_created = []
        original_shot_init = Shot.__init__
        
        def mock_shot_init(self, x, y):
            shots_created.append((x, y))
            original_shot_init(self, x, y)
        
        with patch.object(Shot, '__init__', mock_shot_init):
            player.shoot()
            assert len(shots_created) == 1
            assert shots_created[0][0] == player.position.x
            assert shots_created[0][1] == player.position.y
    
    def test_shoot_cooldown(self):
        """Test that shooting has a cooldown"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.cooldown = 0
        
        # Mock pygame.key.get_pressed to simulate spacebar
        with patch('pygame.key.get_pressed', return_value={pygame.K_SPACE: True}):
            with patch('pygame.K_a', False), patch('pygame.K_d', False), \
                 patch('pygame.K_w', False), patch('pygame.K_s', False):
                player.update(0.01)
                assert player.cooldown > 0
    
    def test_invincibility_after_respawn(self):
        """Test that player gets invincibility after respawn"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.respawn()
        assert player.invincibility == PLAYER_INVINCIBILITY_SECONDS
        assert player.is_invincible() == True
    
    def test_invincibility_timer_decreases(self):
        """Test that invincibility timer decreases over time"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.invincibility = 2.0
        dt = 0.1
        
        player.update(dt)
        assert player.invincibility < 2.0
    
    def test_is_invincible(self):
        """Test invincibility check"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        assert player.is_invincible() == False
        
        player.invincibility = 1.0
        assert player.is_invincible() == True
        
        player.invincibility = 0.0
        assert player.is_invincible() == False


class TestShot:
    """Tests for the Shot class"""
    
    def test_initialization(self):
        """Test shot initialization"""
        shot = Shot(100, 200)
        assert shot.position.x == 100
        assert shot.position.y == 200
        assert shot.radius > 0
        assert shot.lifetime == SHOT_LIFETIME_SECONDS
    
    def test_shot_moves(self):
        """Test that shot moves with velocity"""
        shot = Shot(100, 100)
        shot.velocity = pygame.Vector2(100, 50)
        initial_x = shot.position.x
        initial_y = shot.position.y
        dt = 0.1
        
        shot.update(dt)
        assert shot.position.x != initial_x
        assert shot.position.y != initial_y
    
    def test_shot_despawns_after_lifetime(self):
        """Test that shot despawns after lifetime expires"""
        shot = Shot(100, 100)
        shot.lifetime = 0.1
        dt = 0.15
        
        # Mock kill method to track if it's called
        shot.kill = Mock()
        shot.update(dt)
        shot.kill.assert_called_once()
    
    def test_shot_lifetime_decreases(self):
        """Test that shot lifetime decreases"""
        shot = Shot(100, 100)
        initial_lifetime = shot.lifetime
        dt = 0.1
        
        shot.update(dt)
        assert shot.lifetime < initial_lifetime


class TestAsteroid:
    """Tests for the Asteroid class"""
    
    def test_initialization(self):
        """Test asteroid initialization"""
        asteroid = Asteroid(100, 200, 30)
        assert asteroid.position.x == 100
        assert asteroid.position.y == 200
        assert asteroid.radius == 30
    
    def test_asteroid_moves(self):
        """Test that asteroid moves with velocity"""
        asteroid = Asteroid(100, 100, 20)
        asteroid.velocity = pygame.Vector2(50, 75)
        initial_x = asteroid.position.x
        initial_y = asteroid.position.y
        dt = 0.1
        
        asteroid.update(dt)
        assert asteroid.position.x != initial_x
        assert asteroid.position.y != initial_y
    
    def test_asteroid_splits_when_large(self):
        """Test that large asteroids split into smaller ones"""
        asteroid = Asteroid(100, 100, ASTEROID_MIN_RADIUS * 2)
        asteroid.velocity = pygame.Vector2(100, 0)
        original_radius = asteroid.radius
        
        # Mock Asteroid.__init__ to track creation
        asteroids_created = []
        original_init = Asteroid.__init__
        
        def mock_init(self, x, y, radius):
            asteroids_created.append((x, y, radius))
            # Don't call original to avoid adding to sprite groups
            CircleShape.__init__(self, x, y, radius)
        
        with patch.object(Asteroid, '__init__', mock_init):
            asteroid.split()
            # Should create 2 new asteroids
            assert len(asteroids_created) == 2
            # Both should be smaller
            for _, _, radius in asteroids_created:
                assert radius < original_radius
    
    def test_asteroid_does_not_split_when_small(self):
        """Test that small asteroids don't split"""
        asteroid = Asteroid(100, 100, ASTEROID_MIN_RADIUS)
        asteroids_created = []
        
        original_init = Asteroid.__init__
        def mock_init(self, x, y, radius):
            asteroids_created.append((x, y, radius))
            # Don't call original to avoid adding to sprite groups
            CircleShape.__init__(self, x, y, radius)
        
        with patch.object(Asteroid, '__init__', mock_init):
            asteroid.split()
            # Should not create new asteroids
            assert len(asteroids_created) == 0


class TestGameMechanics:
    """Tests for game mechanics and scoring"""
    
    def test_score_small_asteroid(self):
        """Test scoring for small asteroids"""
        from main import get_asteroid_score
        score = get_asteroid_score(20)  # Small asteroid
        assert score == SCORE_SMALL_ASTEROID
    
    def test_score_medium_asteroid(self):
        """Test scoring for medium asteroids"""
        from main import get_asteroid_score
        score = get_asteroid_score(40)  # Medium asteroid
        assert score == SCORE_MEDIUM_ASTEROID
    
    def test_score_large_asteroid(self):
        """Test scoring for large asteroids"""
        from main import get_asteroid_score
        score = get_asteroid_score(60)  # Large asteroid
        assert score == SCORE_LARGE_ASTEROID
    
    def test_collision_player_asteroid(self):
        """Test collision detection between player and asteroid"""
        player = Player(100, 100)
        asteroid = Asteroid(110, 100, 20)  # Close enough to collide
        
        assert asteroid.collides_with(player) == True
    
    def test_collision_shot_asteroid(self):
        """Test collision detection between shot and asteroid"""
        shot = Shot(100, 100)
        asteroid = Asteroid(105, 100, 20)  # Close enough to collide
        
        assert asteroid.collides_with(shot) == True
    
    def test_no_collision_when_far_apart(self):
        """Test that objects far apart don't collide"""
        player = Player(100, 100)
        asteroid = Asteroid(500, 500, 20)  # Far apart
        
        assert asteroid.collides_with(player) == False


class TestIntegration:
    """Integration tests for game systems"""
    
    def test_player_shoot_and_hit_asteroid(self):
        """Test complete flow: player shoots, shot hits asteroid"""
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.rotation = 0
        
        # Create shot
        shot = Shot(player.position.x, player.position.y)
        shot.velocity = pygame.Vector2(0, -PLAYER_SPEED)
        
        # Create asteroid in shot path
        asteroid = Asteroid(player.position.x, player.position.y - 50, 30)
        
        # Move shot toward asteroid
        for _ in range(10):
            shot.update(0.01)
            if asteroid.collides_with(shot):
                break
        
        # Should collide
        assert asteroid.collides_with(shot) == True
    
    def test_screen_wrapping_all_objects(self):
        """Test that all objects wrap around screen edges"""
        player = Player(-10, SCREEN_HEIGHT / 2)
        shot = Shot(SCREEN_WIDTH + 10, SCREEN_HEIGHT / 2)
        asteroid = Asteroid(SCREEN_WIDTH / 2, -10, 20)
        
        player.wrap_position()
        shot.wrap_position()
        asteroid.wrap_position()
        
        # All should be wrapped back on screen
        assert player.position.x > 0
        assert shot.position.x < SCREEN_WIDTH
        assert asteroid.position.y > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
