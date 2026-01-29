# Game Tests

This directory contains comprehensive tests for the Asteroids game.

## Running Tests

### Option 1: Simple Test Runner (No Dependencies)
```bash
python run_tests.py
```
This runs basic tests without requiring pytest.

### Option 2: Full Pytest Suite

#### Install Dependencies
```bash
pip install pytest
# or
uv sync  # (pytest is in pyproject.toml)
```

#### Run All Tests
```bash
pytest test_game.py test_integration.py -v
```

### Run Specific Test File
```bash
pytest test_game.py -v
pytest test_integration.py -v
```

### Run Specific Test Class
```bash
pytest test_game.py::TestPlayer -v
```

### Run Specific Test
```bash
pytest test_game.py::TestPlayer::test_rotation -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html test_game.py test_integration.py
```

## Test Structure

### `test_game.py`
Unit tests for individual game components:
- **TestCircleShape**: Tests for base shape class (collision, wrapping)
- **TestPlayer**: Tests for player mechanics (movement, rotation, shooting, invincibility)
- **TestShot**: Tests for shot behavior (movement, lifetime, despawning)
- **TestAsteroid**: Tests for asteroid behavior (movement, splitting)
- **TestGameMechanics**: Tests for game rules (scoring, collisions)
- **TestIntegration**: Integration tests for multiple systems

### `test_integration.py`
Integration tests for complete game flows:
- **TestGameFlow**: Tests complete gameplay scenarios
- **TestGameBalance**: Tests game balance and constants

## What's Tested

✅ Collision detection  
✅ Screen wrapping for all objects  
✅ Player movement and rotation  
✅ Shooting mechanics and cooldown  
✅ Shot lifetime and despawning  
✅ Asteroid splitting  
✅ Invincibility system  
✅ Scoring system  
✅ Game balance constants  

## Notes

- Tests run in headless mode (no display required)
- Pygame is initialized once per test session
- Some tests use mocking to isolate components
- Integration tests verify complete game flows
