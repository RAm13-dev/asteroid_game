"""
Pytest configuration and fixtures for game tests.
"""
import pytest
import pygame
import os

# Set headless mode for pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame once for all tests"""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def mock_screen():
    """Create a mock screen for drawing tests"""
    return pygame.Surface((1280, 720))
