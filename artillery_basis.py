# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 09:35:41 2025
@author: gatou
"""

import pygame
from assets import Terrain 
import math, random
import numpy as np

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.1

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# --- Setup Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Artillery Duel")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

# --- Game Variables ---
# Simple terrain as a list of Y-values
terrain = Terrain([SCREEN_WIDTH,SCREEN_HEIGHT  ])

    
    
    
# Player setup
player1 = {'x': 100, 'y': terrain.y[100] - 20, 'color': (255, 0, 0), 'angle': 45, 'power': 50, 'health': 100}
player2 = {'x': 700, 'y': terrain.y[700] - 20, 'color': (0, 0, 255), 'angle': 135, 'power': 50, 'health': 100}
players = [player1, player2]

# Projectile
shell = {'x': 0, 'y': 0, 'vel_x': 0, 'vel_y': 0, 'active': False}

# Game state
current_player = 0
running = True

# --- Main Game Loop ---
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- Player Input (Only if shell is NOT active) ---
        if not shell['active'] and event.type == pygame.KEYDOWN:
            active_player = players[current_player]
            
            if event.key == pygame.K_UP:
                active_player['angle'] += 1
            if event.key == pygame.K_DOWN:
                active_player['angle'] -= 1
            if event.key == pygame.K_RIGHT:
                active_player['power'] += 1
            if event.key == pygame.K_LEFT:
                active_player['power'] -= 1
                
            # Clamp values
            active_player['power'] = max(0, min(100, active_player['power']))
            
            if event.key == pygame.K_SPACE:
                
                # --- FIRE ---
                angle_rad = math.radians(active_player['angle'])
                power = active_player['power'] / 5.0 # Scale power
                
                shell['vel_x'] = power * math.cos(angle_rad)
                shell['vel_y'] = -power * math.sin(angle_rad) # Use negative sin
                
                shell['x'] = active_player['x']
                shell['y'] = active_player['y']
                shell['active'] = True

    # - - - - -- Game Logic --- - - - - - 
    if shell['active']:
        # Apply gravity
        shell['vel_y'] += GRAVITY
        
        # Update position
        shell['x'] += shell['vel_x']
        shell['y'] += shell['vel_y']
        
        # Collision checking (simplified)
        shell_x_int = int(shell['x'])
        
        # Check terrain collision
        if shell_x_int >= 0 and shell_x_int < SCREEN_WIDTH and shell['y'] >= terrain.y[shell_x_int]:
            shell['active'] = False
            print("Hit ground!")
            current_player = (current_player + 1) % 2 # Switch turn

        # Check other player collision (TODO)
        # ... check if shell rect hits other player rect ...
        # if hit:
        #    other_player['health'] -= 10
        #    shell['active'] = False
        #    current_player = (current_player + 1) % 2

        # Check off-screen
        if shell['x'] < 0 or shell['x'] > SCREEN_WIDTH or shell['y'] > SCREEN_HEIGHT:
            shell['active'] = False
            print("Missed!")
            current_player = (current_player + 1) % 2 # Switch turn

    # --- Drawing ---
    screen.fill(BLACK) # Clear screen with a "sky" color

    # Draw terrain
    terrain.draw(screen)

    # --- Draw Aiming Vector (NEW CODE) ---
    if not shell['active']:
        # Get the current player
        active_player = players[current_player]
        
        # Get the player's center
        start_x = active_player['x']
        start_y = active_player['y']
        
        # Get angle and power
        angle_rad = math.radians(active_player['angle'])
        line_length = active_player['power'] # Use power for the line length
        
        # Calculate the end point
        end_x = start_x + (line_length * math.cos(angle_rad))
        end_y = start_y - (line_length * math.sin(angle_rad)) # Use negative sin for inverted Y-axis
        
        # Draw the line
        pygame.draw.line(screen, WHITE, (start_x, start_y), (int(end_x), int(end_y)), 2)


    # Draw players
    for player in players:
        pygame.draw.rect(screen, player['color'], (player['x'] - 10, player['y'], 20, 20))
        
    # Draw shell
    if shell['active']:
        pygame.draw.circle(screen, WHITE, (int(shell['x']), int(shell['y'])), 5)

    # ... draw UI ...
    
    # --- Update Display ---
    pygame.display.flip()



    # Draw players
    for player in players:
        pygame.draw.rect(screen, player['color'], (player['x'] - 10, player['y'], 20, 20)) # Draw a simple tank
        
    # Draw shell
    if shell['active']:
        pygame.draw.circle(screen, WHITE, (int(shell['x']), int(shell['y'])), 5)

    # Draw UI (Angle, Power)
    ui_text = f"Player {current_player + 1} | Angle: {players[current_player]['angle']} | Power: {players[current_player]['power']}"
    text_surface = font.render(ui_text, True, WHITE)
    screen.blit(text_surface, (10, 10))

    # --- Update Display ---
    pygame.display.flip()
    
    # --- Frame Rate ---
    clock.tick(60)

pygame.quit()