# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 09:35:41 2025
@author: gatou
"""

import pygame
from assets import Terrain, Castle, Shell, Cloud, DT, generate_stars  

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

# --- Setup Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Artillery Duel")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

# %% --- Environnment Variables ---
# Generate 5 clouds and 20 stars
stars= generate_stars(20, SCREEN_WIDTH, SCREEN_HEIGHT)
clouds = [Cloud(SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(5)]
# Simple terrain as a list of Y-values
terrain = Terrain([SCREEN_WIDTH,SCREEN_HEIGHT  ])
  
# --- Create Players ---
player1 = Castle(100, terrain.y[100], 
                 image_path='pix/pixil-frame20.png', flipped=False, initial_angle=45)
player2 = Castle(700, terrain.y[700], 
                 image_path='pix/pixil-frame20.png', flipped=True, initial_angle=135)
players = [player1, player2]

# Projectile - active_shell variable TODO
active_shell = None

# Game state
current_player = 0
running = True

# %% --- - - - - -  Event Handling ---
while running: #  --- Main Game Loop ---
# Get the current and other player for convenience
    active_player = players[current_player]
    other_player = players[(current_player + 1) % 2]
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
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
                active_shell = active_player.fire()

    # %% - - - - -- Game Logic --- - - - - - 
    if active_shell:
        # Apply gravity and drag .... One time step at a time
        (t,u,v,x,y) = active_shell.update()
        collision_status = active_shell.check_collision(terrain, other_player.rect, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        if collision_status:
            if collision_status == 'HIT_PLAYER':
                other_player.take_damage(20) # Deal damage
                print(f"Player {current_player + 1} hits! Other player health: {other_player.health}")
                # # Check for win
                # if other_player.health <= 0:
                #     game_state = "GAME_OVER"
                #     winner = f"Player {current_player + 1} Wins!"
                    # its turn is over.
            elif collision_status == 'HIT_TERRAIN':   
                print("Hit ground!")
            active_shell = None # Destroy the shell
            
            if True: # game_state == "PLAYING":
                # Switch turns
                current_player = (current_player + 1) % 2
                

    # %% --- Drawing ---
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
        # Draw the line
        active_player.draw_aiming_vector(screen)
    
    if active_shell:
        active_shell.draw(screen)

    # Draw UI (Angle, Power)
    ui_text = f"Player {current_player + 1} | Angle: {active_player.angle} | Power: {active_player.power}"
    text_surface = font.render(ui_text, True, WHITE)
    screen.blit(text_surface, (10, 10))

    # --- Update Display ---
    pygame.display.flip()
    
    # --- Frame Rate ---
    clock.tick(int(1/DT))

pygame.quit()