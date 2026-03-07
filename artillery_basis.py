
"""
Created on Wed Nov 12 09:35:41 2025
"""

import pygame
import random
from assets import Terrain, Castle, Shell, Cloud, DT, generate_stars, Explosion 
from assets import FloatingText  

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# 8-Bit Palette
MIDNIGHT_BLUE = (20, 20, 60)   # Dark Night Sky
GRASS_GREEN = (100, 200, 50)   # Bright 8-bit grass
DIRT_BROWN = (100, 50, 0)      # Dark earth
STAR_COLOR = (200, 200, 255)   # Slightly blueish stars

# %% --- Setup Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Artillery Duel")
clock = pygame.time.Clock()

try:
    game_font = pygame.font.Font('res/retro.ttf', 16) 
    large_font = pygame.font.Font('res/retro.ttf', 24)
    title_font = pygame.font.Font('res/retro.ttf', 60)
except FileNotFoundError:   # Try to load the retro font, fallback to system font if missing
    print("Retro font not found, using system font.")
    game_font = pygame.font.SysFont('Consolas', 20, bold=True)
    large_font = pygame.font.SysFont('Consolas', 30, bold=True)
    title_font = pygame.font.SysFont('Consolas', 60)

# %%% Functions
def draw_start_screen(screen):
    """Draws the AgArtillery Intro Screen"""
    screen.fill(MIDNIGHT_BLUE)
    
    # Draw some decorative stars
    for _ in range(50):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        pygame.draw.circle(screen, STAR_COLOR, (x,y), 1)

    # Title Text
    title_surf = title_font.render("Ag-Artillery", True, (255, 50, 50))
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
    screen.blit(title_surf, title_rect)
    # Subtitle Text
    prompt_surf = large_font.render("Press any key to start", True, WHITE)
    prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
    screen.blit(prompt_surf, prompt_rect)

def draw_scoreboard(screen, p1, p2, wind):
    # 1. Draw the Background Panel (Top of screen)
    panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 50)
    pygame.draw.rect(screen, (30, 30, 30), panel_rect) # Dark Grey background
    pygame.draw.line(screen, WHITE, (0, 50), (SCREEN_WIDTH, 50), 3) # White bottom border
    
    # 2. Player 1 Stats (Left)
    p1_text = f"P1: {p1.health}HP"
    p1_surf = game_font.render(p1_text, True, (255, 100, 100)) # Light Red
    screen.blit(p1_surf, (20, 15))
    
    # P1 Angle/Power (Smaller info)
    p1_stats = f"A:{p1.angle} P:{p1.power}"
    stats_surf = game_font.render(p1_stats, True, WHITE)
    screen.blit(stats_surf, (20, 35)) # Slightly below

    # 3. Player 2 Stats (Right)
    p2_text = f"P2: {p2.health}HP"
    p2_surf = game_font.render(p2_text, True, (100, 100, 255)) # Light Blue
    # Calculate x position to align right
    screen.blit(p2_surf, (SCREEN_WIDTH - p2_surf.get_width() - 20, 15))
    
    p2_stats = f"A:{p2.angle} P:{p2.power}"
    stats2_surf = game_font.render(p2_stats, True, WHITE)
    screen.blit(stats2_surf, (SCREEN_WIDTH - stats2_surf.get_width() - 20, 35))

    # 4. Wind Indicator (Center)
    wind_text = f"WIND: {wind}"
    wind_surf = game_font.render(wind_text, True, (200, 200, 200))
    screen.blit(wind_surf, (SCREEN_WIDTH//2 - wind_surf.get_width()//2, 15))

# %%% Environnment Variables ---
# Wind
wind = random.choice(range(-20,30,10))

# Generate 5 clouds and 20 stars
stars= generate_stars(20, SCREEN_WIDTH, SCREEN_HEIGHT)
clouds = [Cloud(SCREEN_WIDTH, SCREEN_HEIGHT, wind) for _ in range(5)]

# Simple terrain as a list of Y-values
terrain = Terrain([SCREEN_WIDTH,SCREEN_HEIGHT  ])
  
# --- Create Players ---
player1 = Castle(100, terrain.y[100], 
                 image_path='pix/pixil-frame20.png', flipped=False, initial_angle=45)
player2 = Castle(700, terrain.y[700], 
                 image_path='pix/pixil-frame20.png', flipped=True, initial_angle=135)
players = [player1, player2]

# Projectile and Effects
active_shell = None
explosions = []
floating_texts = []

# Game state
current_player_index = 0
GAME_STATE = "START" # Options: "START", "PLAYING"
running = True

# %% - - - Event Handling ---
while running: #  --- Main Game Loop ---
# Get the current and other player for convenience
    active_player = players[current_player_index]
    other_player = players[(current_player_index + 1) % 2]
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- INPUT HANDLER: START SCREEN ---
        if GAME_STATE == "START":
            if event.type == pygame.KEYDOWN:
                GAME_STATE = "PLAYING"

        # --- INPUT HANDLER: PLAYING ---
        elif GAME_STATE == "PLAYING":
            # active_player = players[current_player_index]
            # --- Player Input (Only if shell is NOT active) ---
            if event.type == pygame.KEYDOWN and active_shell is None : 
                if event.key == pygame.K_UP:
                    active_player.update_angle(1)
                if event.key == pygame.K_DOWN:
                    active_player.update_angle(-1)
                if event.key == pygame.K_RIGHT:
                    active_player.update_power(1)
                if event.key == pygame.K_LEFT:
                    active_player.update_power(-1)               
                
                if event.key == pygame.K_SPACE:   # --- FIRE ---
                    active_shell = active_player.fire(wind)

    # %% - - - Draw Start Screen
    if GAME_STATE == "START":
        draw_start_screen(screen)

    # %% - - - STATE : PLAYING 
    # %%% - - - Game Logic -
    elif GAME_STATE == "PLAYING":    
        if active_shell:
            # Apply gravity and drag .... One time step at a time
            (t,u,v,x,y) = active_shell.update(wind)
            collision_status = active_shell.check_collision(terrain, other_player.rect, SCREEN_WIDTH, SCREEN_HEIGHT)
            
            if collision_status:
                explosions.append(Explosion(x, y))
                
                if collision_status == 'HIT_PLAYER':
                    damage = other_player.take_damage(u,v,wind) # Deal damage as a function of speed
                    print(f"Player {current_player_index + 1} hits! Other player health: {other_player.health:.0f}")
                    # Create text at the hit player's location. We use "- damage" to show negative loss
                    floating_texts.append(FloatingText(other_player.rect.centerx, other_player.rect.top, 
                                                       -damage)
                                          )
                    # Check for win condition
                    if other_player.health <= 0:
                        GAME_STATE = "GAME_OVER"
                        print(f"Player {current_player_index} wins")

                    # AND change wind after player turn
                    wind = random.choice(range(-100,100,10))
                    for cloud in clouds:
                        cloud.wind_change(wind) # Change the cloud movement
                        
                elif collision_status == 'HIT_TERRAIN':   
                    # TODO print the speed at impact.
                    print(f"Hit ground! Shell hangtime was {t:.2f} seconds")
                    # TODO collision on ground can cause a damage by deflagration 
                    terrain.destroy(x) 
                else:
                    print(f"Out of Bounds! Shell hangtime was {t:.2f} seconds")
                
                if True: 
                    active_shell = None # Destroy the shell after impact
                    current_player_index = (current_player_index + 1) % 2

        
        # %%% - - - Drawing ---
        screen.fill(MIDNIGHT_BLUE) # Clear screen with a "sky" color
        for star in stars:
            pygame.draw.circle(screen, STAR_COLOR, star, 1) 
        for cloud in clouds:
            cloud.update() # Move the cloud
            cloud.draw(screen) # Draw the cloud
        # Draw terrain and players
        terrain.draw(screen)
        player1.draw(screen)
        player2.draw(screen)
    
        # --- Draw Aiming Vector  ---
        if active_shell is None:
            # Draw the arrow
            active_player.draw_aiming_vector(screen)
        
        if active_shell:
            active_shell.draw(screen)
        
        # - - - explosions - - - -    
        for exp in explosions:
            exp.update()
            exp.draw(screen)
        # Remove finished explosions
        explosions = [e for e in explosions if e.active]    
    
        # Draw Floating Texts and Delete Inactive
        for ft in floating_texts:
            ft.update()
            ft.draw(screen, game_font)
        floating_texts = [ft for ft in floating_texts if ft.timer>0]
        
        #    Draw the New Scoreboard
        # (Assuming you have a 'current_wind' variable, pass 0 if not yet implemented)
        draw_scoreboard(screen, player1, player2, wind)
    
    # --- Update Display ---
    pygame.display.flip()
    clock.tick(int(1/DT))

pygame.quit()