# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 16:51:18 2024
game of artillery
@author: gatou
"""
# terminal velocity
# theorical range
# hangtime

import pandas as pd
import numpy as np
import random, math
import pygame
import matplotlib.pyplot as plt

G = 55
MU = 0.0005# Units ??
DT = 0.1

GREEN = (0, 150, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Terrain:
    def __init__(self,size):
        # Simple terrain as a list of Y-values
        # slope = [random.randint(-20, 20) for _ in range(SCREEN_WIDTH)]
        
        # terrain = [550 for _ in range(SCREEN_WIDTH) ]
        self.size = size
        self.y =  [550 for _ in range(size[0]) ]
        # for i in range(100,700):
        #      terrain[i] = terrain[i-1] + 0.2* slope[i] + 0.1*slope[i-1] + 0.1*slope[i-2]
         
    def draw(self,screen):
        for x, y in enumerate(self.y):
            pygame.draw.line(screen, GREEN, 
                             (x, y), (x, self.size[1]) 
                             )

class Castle:
    def __init__(self, x_pos, y_pos_on_terrain, image_path, flipped = False , initial_angle = 50):
        """
        Initializes a Player (castle)
        """
        # Load, scale, and flip the image
        try:
            image = pygame.image.load(image_path).convert_alpha()
            width = 40
            height = int(image.get_height() * (width / image.get_width()))
            self.image = pygame.transform.scale(image, (width, height))
            if flipped:
                self.image = pygame.transform.flip(self.image, True, False)
        except pygame.error:
            # Fallback if image fails to load
            print(f"Warning: Could not load {image_path}. Using a placeholder.")
            self.image = pygame.Surface((40, 40))
            self.image.fill((150, 100, 50)) # Brown placeholder

        # Set position and rect
        # We use .midbottom to make it sit perfectly on the terrain
        self.rect = self.image.get_rect(midbottom=(x_pos, y_pos_on_terrain))
        
        # Game attributes
        self.health = 100
        self.angle = initial_angle
        self.power = 50
        
        # Cannon position (relative to the rect's top-left)
        # You'll need to adjust these offsets based on your castle image
        if flipped:
            self.cannon_offset = (5, 20) # (x, y) offset from top-left
        else:
            self.cannon_offset = (35, 20) # (x, y) offset from top-left


class Shell:
    pos = (0, 0)
    active = True
    
    def __init__(self,x_0,y_0,v_0, angle):
        self.df = pd.DataFrame(
                            {'time' : [0],
                             'vel_x': [v_0*math.cos(angle*math.pi/180)],
                             'vel_y': [v_0*math.sin(angle*math.pi/180)],
                             'pos_x': [x_0], 'pos_y' :[y_0] }
                               )

        self.rect = pygame.Rect(int(self.df['pos_x'].iloc[-1]), 
                                int(self.df['pos_y'].iloc[-1]), 
                                5, 5) # Small rect for collision
        
    def trajectory(self):
        # new line
        clock = self.df['time'].iloc[-1]
        vel_x = self.df['vel_x'].iloc[-1]
        vel_y = self.df['vel_y'].iloc[-1]
        pos_x = self.df['pos_x'].iloc[-1]
        pos_y =  self.df['pos_y'].iloc[-1]
        
        if self.active: # to be moved in a collision chec
            while pos_y >= 0: # collision check // active == True
                clock += DT
                vel = np.sqrt(vel_x**2 + vel_y**2)
                vel_x -= MU*vel*vel_x*DT
                vel_y -= (G + MU*vel*vel_y)*DT
                pos_x += vel_x*DT
                pos_y += vel_y*DT
            
                self.df.loc[len(self.df.index)] = [clock, vel_x , vel_y , pos_x , pos_y] 
                
            self.rect.center = (int(pos_x), int(pos_y))
    
    def draw(self, screen):
        """Draws the shell as a simple circle"""
        pygame.draw.circle(screen, WHITE, self.rect.center, 5)

    def check_collision(self, terrain, other_player_rect, screen_width, screen_height):
        """
        Checks for all collisions and returns a status.
        Returns: 'HIT_TERRAIN', 'HIT_PLAYER', 'OFF_SCREEN', or None
        """
        pass
        # x_int = int(self.x)
        
        # # Check terrain collision
        # if 0 <= x_int < screen_width and self.y >= terrain[x_int]:
        #     return 'HIT_TERRAIN'
            
        # # Check other player collision
        # if self.rect.colliderect(other_player_rect):
        #     return 'HIT_PLAYER'
        
        # # Check off-screen
        # if self.x < 0 or self.x >= screen_width or self.y > screen_height:
        #     return 'OFF_SCREEN'
    
    def plot(self, ax = None):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(demo.df['pos_x'], demo.df['pos_y'])

        ax.set(xlabel='distance', ylabel='distance',
               title='Shell trajectory')
        ax.grid()
        plt.show()
        return ax
        
    def hit(self, world): # collision check
        pass


if __name__ == '__main__':
    demo= Shell(0,0,200,45)
    demo.trajectory()
    print(demo.df['time'])
    ax = demo.plot()





