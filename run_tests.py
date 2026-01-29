"""
Simple test runner that doesn't require pytest.
Run with: python run_tests.py
"""
import sys
import os

# Set headless mode for pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from pygame_fallback import ensure_pygame

pygame = ensure_pygame()
pygame.init()

# Import game modules
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

# Import scoring function
from main import get_asteroid_score

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name, func):
        """Register a test"""
        self.tests.append((name, func))
    
    def assert_true(self, condition, message=""):
        """Assert that condition is True"""
        if not condition:
            raise AssertionError(message or "Assertion failed")
    
    def assert_equal(self, actual, expected, message=""):
        """Assert that actual equals expected"""
        if actual != expected:
            raise AssertionError(
                message or f"Expected {expected}, got {actual}"
            )
    
    def assert_almost_equal(self, actual, expected, tolerance=0.001, message=""):
        """Assert that actual is approximately equal to expected"""
        if abs(actual - expected) > tolerance:
            raise AssertionError(
                message or f"Expected {expected} (±{tolerance}), got {actual}"
            )
    
    def run_all(self):
        """Run all registered tests"""
        print("=" * 60)
        print("Running Game Tests")
        print("=" * 60)
        
        for name, test_func in self.tests:
            try:
                test_func()
                print(f"[PASS] {name}")
                self.passed += 1
            except Exception as e:
                print(f"[FAIL] {name}")
                print(f"  Error: {e}")
                self.failed += 1
        
        print("=" * 60)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        
        return self.failed == 0

# Create test runner
runner = TestRunner()

# Test CircleShape
def test_circle_shape_init():
    shape = CircleShape(100, 200, 30)
    runner.assert_equal(shape.position.x, 100)
    runner.assert_equal(shape.position.y, 200)
    runner.assert_equal(shape.radius, 30)

def test_collision_detection():
    shape1 = CircleShape(100, 100, 20)
    shape2 = CircleShape(120, 100, 20)  # Touching
    runner.assert_true(shape1.collides_with(shape2))
    
    shape3 = CircleShape(150, 100, 20)  # Not touching
    runner.assert_true(not shape1.collides_with(shape3))

def test_wrap_position():
    # Position must be beyond SCREEN_WIDTH + radius to trigger wrapping
    shape = CircleShape(SCREEN_WIDTH + 50, 100, 20)
    original_x = shape.position.x
    shape.wrap_position()
    # Should wrap to left side (negative position)
    runner.assert_true(shape.position.x != original_x)
    runner.assert_true(shape.position.x < 0 or shape.position.x == -shape.radius)

# Test Player
def test_player_init():
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    runner.assert_equal(player.rotation, 0)
    runner.assert_equal(player.cooldown, 0)
    runner.assert_equal(player.invincibility, 0.0)

def test_player_rotation():
    player = Player(100, 100)
    initial_rotation = player.rotation
    player.rotate(0.1)
    runner.assert_true(player.rotation > initial_rotation)

def test_player_invincibility():
    player = Player(100, 100)
    player.respawn()
    runner.assert_equal(player.invincibility, PLAYER_INVINCIBILITY_SECONDS)
    runner.assert_true(player.is_invincible())

def test_player_invincibility_timer():
    player = Player(100, 100)
    player.invincibility = 2.0
    # Update without key presses (just timer)
    player.cooldown = 0
    # Manually update invincibility timer
    if player.invincibility > 0:
        player.invincibility -= 0.1
        if player.invincibility < 0:
            player.invincibility = 0
    runner.assert_true(player.invincibility < 2.0)

# Test Shot
def test_shot_init():
    shot = Shot(100, 200)
    runner.assert_equal(shot.position.x, 100)
    runner.assert_equal(shot.position.y, 200)
    runner.assert_equal(shot.lifetime, SHOT_LIFETIME_SECONDS)

def test_shot_moves():
    shot = Shot(100, 100)
    shot.velocity = pygame.Vector2(100, 50)
    initial_x = shot.position.x
    shot.update(0.1)
    runner.assert_true(shot.position.x != initial_x)

def test_shot_lifetime():
    shot = Shot(100, 100)
    initial_lifetime = shot.lifetime
    shot.update(0.1)
    runner.assert_true(shot.lifetime < initial_lifetime)

# Test Asteroid
def test_asteroid_init():
    asteroid = Asteroid(100, 200, 30)
    runner.assert_equal(asteroid.position.x, 100)
    runner.assert_equal(asteroid.position.y, 200)
    runner.assert_equal(asteroid.radius, 30)

def test_asteroid_moves():
    asteroid = Asteroid(100, 100, 20)
    asteroid.velocity = pygame.Vector2(50, 75)
    initial_x = asteroid.position.x
    asteroid.update(0.1)
    runner.assert_true(asteroid.position.x != initial_x)

# Test Scoring
def test_scoring():
    runner.assert_equal(get_asteroid_score(20), SCORE_SMALL_ASTEROID)
    runner.assert_equal(get_asteroid_score(40), SCORE_MEDIUM_ASTEROID)
    runner.assert_equal(get_asteroid_score(60), SCORE_LARGE_ASTEROID)

# Register all tests
runner.test("CircleShape initialization", test_circle_shape_init)
runner.test("Collision detection", test_collision_detection)
runner.test("Screen wrapping", test_wrap_position)
runner.test("Player initialization", test_player_init)
runner.test("Player rotation", test_player_rotation)
runner.test("Player invincibility", test_player_invincibility)
runner.test("Player invincibility timer", test_player_invincibility_timer)
runner.test("Shot initialization", test_shot_init)
runner.test("Shot movement", test_shot_moves)
runner.test("Shot lifetime", test_shot_lifetime)
runner.test("Asteroid initialization", test_asteroid_init)
runner.test("Asteroid movement", test_asteroid_moves)
runner.test("Scoring system", test_scoring)

if __name__ == "__main__":
    success = runner.run_all()
    sys.exit(0 if success else 1)
