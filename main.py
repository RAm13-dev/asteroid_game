import math
import os
import asteroidfield
import pygame
import audio
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_LIVES,
    SCORE_SMALL_ASTEROID, SCORE_MEDIUM_ASTEROID, SCORE_LARGE_ASTEROID,
    BLUR_SCALE,
    PARTICLE_BURST_ALPHA,
    PARTICLE_BURST_COLOR,
    PARTICLE_BURST_COUNT,
    PARTICLE_BURST_LIFE_RANGE,
    PARTICLE_BURST_SIZE_RANGE,
    PARTICLE_BURST_SPEED_RANGE,
)
from background import build_background_layers
from explosion import Explosion
from logger import log_state
from particles import Particle, ParticleBurst
from player import Player
from asteroid import Asteroid
from shot import Shot
from asteroidfield import AsteroidField
from logger import log_event

# Add your custom assets here:
# - Font: assets/fonts/PressStart2P-Regular.ttf (or update HUD_FONT_PATH)
# - Icons: assets/icons/heart.png and assets/icons/shield.png (PNG/SVG->PNG)
HUD_FONT_PATH = os.path.join("assets", "fonts", "PressStart2P-Regular.ttf")
HEART_ICON_PATH = os.path.join("assets", "icons", "heart.png")
SHIELD_ICON_PATH = os.path.join("assets", "icons", "shield.png")

def make_heart_icon(size):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    color = (255, 72, 92, 255)
    radius = int(size * 0.28)
    pygame.draw.circle(surface, color, (int(size * 0.35), int(size * 0.35)), radius)
    pygame.draw.circle(surface, color, (int(size * 0.65), int(size * 0.35)), radius)
    points = [
        (int(size * 0.18), int(size * 0.38)),
        (int(size * 0.82), int(size * 0.38)),
        (int(size * 0.5), int(size * 0.9)),
    ]
    pygame.draw.polygon(surface, color, points)
    return surface

def make_shield_icon(size):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    fill = (0, 120, 200, 200)
    outline = (0, 200, 255, 255)
    points = [
        (int(size * 0.5), int(size * 0.08)),
        (int(size * 0.85), int(size * 0.2)),
        (int(size * 0.8), int(size * 0.65)),
        (int(size * 0.5), int(size * 0.92)),
        (int(size * 0.2), int(size * 0.65)),
        (int(size * 0.15), int(size * 0.2)),
    ]
    pygame.draw.polygon(surface, fill, points)
    pygame.draw.polygon(surface, outline, points, width=2)
    return surface

def get_asteroid_score(radius):
    """Calculate score based on asteroid size"""
    if radius <= 20:
        return SCORE_SMALL_ASTEROID
    elif radius <= 40:
        return SCORE_MEDIUM_ASTEROID
    else:
        return SCORE_LARGE_ASTEROID

def smooth_value(current, target, dt, speed=8.0):
    """Smoothly interpolate values over time."""
    if current == target:
        return current
    blend = 1 - math.exp(-speed * dt)
    return current + (target - current) * blend

def draw_hud(screen, hud_surface, lives, score, font, small_font, icons, shield_active):
    """Draw HUD panel elements on a separate layer."""
    hud_surface.fill((0, 0, 0, 0))
    panel_rect = pygame.Rect(20, 20, 320, 120)
    pygame.draw.rect(hud_surface, (12, 16, 26, 180), panel_rect, border_radius=12)
    pygame.draw.rect(hud_surface, (120, 180, 255, 200), panel_rect, width=2, border_radius=12)

    score_label = small_font.render("Score", True, (190, 210, 255))
    score_value = font.render(f"{int(score):,}", True, "white")
    hud_surface.blit(score_label, (panel_rect.x + 16, panel_rect.y + 12))
    hud_surface.blit(score_value, (panel_rect.x + 16, panel_rect.y + 34))

    health_label = small_font.render("Health", True, (255, 200, 200))
    health_value = font.render(f"{int(lives)}", True, "white")
    hud_surface.blit(health_label, (panel_rect.x + 16, panel_rect.y + 72))
    hud_surface.blit(health_value, (panel_rect.x + 16, panel_rect.y + 92))

    heart_icon, shield_icon = icons
    icon_y = panel_rect.y + 88
    icon_x = panel_rect.x + 120
    for i in range(max(0, int(lives))):
        hud_surface.blit(heart_icon, (icon_x + i * 26, icon_y))

    shield_alpha = 255 if shield_active else 80
    shield_icon = shield_icon.copy()
    shield_icon.set_alpha(shield_alpha)
    hud_surface.blit(shield_icon, (panel_rect.right - 40, panel_rect.y + 12))

    screen.blit(hud_surface, (0, 0))

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

def render_scene(target_surface, drawable, player, background_layers):
    target_surface.fill("black")
    for layer in background_layers:
        layer.draw(target_surface)
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
    audio.init_audio()
    audio.play_music()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    frame_buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    hud_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    # Initialize font (drop your custom TTF into HUD_FONT_PATH)
    font_path = HUD_FONT_PATH if os.path.exists(HUD_FONT_PATH) else None
    hud_font = pygame.font.Font(font_path, 28)
    hud_small_font = pygame.font.Font(font_path, 16)
    font = pygame.font.Font(font_path, 32)
    big_font = pygame.font.Font(font_path, 64)

    if os.path.exists(HEART_ICON_PATH) and os.path.exists(SHIELD_ICON_PATH):
        heart_icon = pygame.image.load(HEART_ICON_PATH).convert_alpha()
        shield_icon = pygame.image.load(SHIELD_ICON_PATH).convert_alpha()
        heart_icon = pygame.transform.smoothscale(heart_icon, (22, 22))
        shield_icon = pygame.transform.smoothscale(shield_icon, (24, 24))
        hud_icons = (heart_icon, shield_icon)
    else:
        # Fallback to simple vector icons until you add PNGs.
        hud_icons = (make_heart_icon(22), make_shield_icon(24))
    
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
    Particle.containers = (updatable, drawable)
    ParticleBurst.containers = updatable
    Explosion.containers = (updatable, drawable)
    
    # Initialize game
    player, asteroid_field = reset_game(updatable)
    background_layers = build_background_layers()
    lives = PLAYER_LIVES
    score = 0
    displayed_lives = float(lives)
    displayed_score = float(score)
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
                        audio.play_sound("ui")
                        player, asteroid_field = reset_game(updatable)
                        lives = PLAYER_LIVES
                        score = 0
                        game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        return
                elif event.key == pygame.K_p:
                    audio.play_sound("ui")
                    paused = not paused
        
        if game_over:
            draw_game_over(screen, score, font, big_font)
            continue
        
        if paused:
            # Render game in background, then overlay pause text
            render_scene(frame_buffer, drawable, player, background_layers)
            blurred = apply_soft_blur(frame_buffer)
            screen.blit(blurred, (0, 0))
            draw_hud(screen, hud_surface, displayed_lives, displayed_score, hud_font, hud_small_font, hud_icons, player.is_invincible())
            draw_pause(screen, font)
            pygame.display.flip()
            clock.tick(60)
            continue
        
        # Calculate delta time
        dt = clock.tick(60) / 1000
        
        # Update game objects
        updatable.update(dt)
        for layer in background_layers:
            layer.update(dt)
        
        # Check collisions
        for asteroid in list(asteroids):
            # Check player collision (only if not invincible)
            if not player.is_invincible() and asteroid.collides_with(player):
                log_event("player_hit")
                audio.play_sound("hit")
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
                    audio.play_sound("explode")
                    # Award points
                    score += get_asteroid_score(asteroid.radius)
                    impact_position = asteroid.position.copy()
                    impact_size = max(24, int(asteroid.radius * 2.4))
                    Explosion(impact_position, impact_size)
                    ParticleBurst(
                        position=impact_position,
                        count=PARTICLE_BURST_COUNT,
                        speed_range=PARTICLE_BURST_SPEED_RANGE,
                        life_range=PARTICLE_BURST_LIFE_RANGE,
                        size_range=PARTICLE_BURST_SIZE_RANGE,
                        color=PARTICLE_BURST_COLOR,
                        alpha=PARTICLE_BURST_ALPHA,
                    )
                    shot.kill()
                    asteroid.split()
                    break

        displayed_lives = smooth_value(displayed_lives, lives, dt, speed=10.0)
        displayed_score = smooth_value(displayed_score, score, dt, speed=6.0)
        
        # Render
        render_scene(frame_buffer, drawable, player, background_layers)
        blurred = apply_soft_blur(frame_buffer)
        screen.blit(blurred, (0, 0))
        
        # Draw UI
        draw_hud(screen, hud_surface, displayed_lives, displayed_score, hud_font, hud_small_font, hud_icons, player.is_invincible())
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
