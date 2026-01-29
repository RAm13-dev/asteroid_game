import sys
import asteroidfield
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_LIVES,
    SCORE_SMALL_ASTEROID, SCORE_MEDIUM_ASTEROID, SCORE_LARGE_ASTEROID,
    BLUR_SCALE,
)
from logger import log_state
from player import Player
from asteroid import Asteroid
from shot import Shot
from asteroidfield import AsteroidField
from logger import log_event

def get_asteroid_score(radius):
    """Calculate score based on asteroid size"""
    if radius <= 20:
        return SCORE_SMALL_ASTEROID
    elif radius <= 40:
        return SCORE_MEDIUM_ASTEROID
    else:
        return SCORE_LARGE_ASTEROID

def draw_ui(screen, lives, score, font):
    """Draw UI elements (lives, score)"""
    # Draw lives
    lives_text = font.render(f"Lives: {lives}", True, "white")
    screen.blit(lives_text, (10, 10))
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, "white")
    screen.blit(score_text, (10, 40))

def draw_game_over(screen, score, font, big_font):
    """Draw game over screen"""
    screen.fill("black")
    
    game_over_text = big_font.render("GAME OVER", True, "white")
    score_text = font.render(f"Final Score: {score}", True, "white")
    restart_text = font.render("Press SPACE to restart or ESC to quit", True, "white")
    
    # Center the text
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
    
    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()

def draw_pause(screen, font):
    """Draw pause screen overlay"""
    pause_text = font.render("PAUSED - Press P to continue", True, "white")
    pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    # Draw semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill("black")
    screen.blit(overlay, (0, 0))
    screen.blit(pause_text, pause_rect)

def apply_soft_blur(surface):
    """Apply a lightweight blur by downscaling and upscaling the surface."""
    if not hasattr(pygame, "transform") or not hasattr(pygame.transform, "smoothscale"):
        return surface
    width, height = surface.get_size()
    scaled_size = (max(1, int(width * BLUR_SCALE)), max(1, int(height * BLUR_SCALE)))
    if scaled_size == (width, height):
        return surface
    scaled = pygame.transform.smoothscale(surface, scaled_size)
    return pygame.transform.smoothscale(scaled, (width, height))

def render_scene(target_surface, drawable, player):
    target_surface.fill("black")
    for obj in drawable:
        obj.draw(target_surface)
    player.draw(target_surface)

def reset_game(updatable):
    """Reset all game objects and return new game state"""
    # Clear all sprites
    for sprite in list(updatable):
        sprite.kill()
    
    # Create new game objects
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()
    
    return player, asteroid_field

def main():
    print("Starting Asteroids with pygame version: " + pygame.version.ver)
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    frame_buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    # Initialize font
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)
    
    # Game state
    shots = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    
    # Set up sprite containers
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)
    
    # Initialize game
    player, asteroid_field = reset_game(updatable)
    lives = PLAYER_LIVES
    score = 0
    paused = False
    game_over = False
    
    while True:
        log_state()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        # Restart game
                        player, asteroid_field = reset_game(updatable)
                        lives = PLAYER_LIVES
                        score = 0
                        game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        return
                elif event.key == pygame.K_p:
                    paused = not paused
        
        if game_over:
            draw_game_over(screen, score, font, big_font)
            continue
        
        if paused:
            # Render game in background, then overlay pause text
            render_scene(frame_buffer, drawable, player)
            blurred = apply_soft_blur(frame_buffer)
            screen.blit(blurred, (0, 0))
            draw_ui(screen, lives, score, font)
            draw_pause(screen, font)
            pygame.display.flip()
            clock.tick(60)
            continue
        
        # Calculate delta time
        dt = clock.tick(60) / 1000
        
        # Update game objects
        updatable.update(dt)
        
        # Check collisions
        for asteroid in list(asteroids):
            # Check player collision (only if not invincible)
            if not player.is_invincible() and asteroid.collides_with(player):
                log_event("player_hit")
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    # Respawn player
                    player.respawn()
            
            # Check shot collisions
            for shot in list(shots):
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    # Award points
                    score += get_asteroid_score(asteroid.radius)
                    shot.kill()
                    asteroid.split()
                    break
        
        # Render
        render_scene(frame_buffer, drawable, player)
        blurred = apply_soft_blur(frame_buffer)
        screen.blit(blurred, (0, 0))
        
        # Draw UI
        draw_ui(screen, lives, score, font)
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
