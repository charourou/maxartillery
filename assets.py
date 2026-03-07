# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 16:51:18 2024
game of artillery
@author: gatou
"""
# terminal velocity
# theorical range
# hangtime

import random, math, pygame
import matplotlib.pyplot as plt

G = 55
MU = 0.0005# Units ??
DT = 0.05

GREEN = (0, 150, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# 8-Bit Palette
MIDNIGHT_BLUE = (20, 20, 60)   # Dark Night Sky
GRASS_GREEN = (100, 200, 50)   # Bright 8-bit grass
DIRT_BROWN = (100, 50, 0)      # Dark earth
STAR_COLOR = (200, 200, 255)   # Slightly blueish stars

BLOCK_SIZE = 5

class Terrain:
    def __init__(self,size):
        # Simple terrain as a list of Y-values
        self.size = size
        y = []
        current_height = random.choice([500,450,550])
        slope = [random.choice([0,1]),random.choice([0,1])]
        
        for x in range(0, size[0], BLOCK_SIZE):
            
            if x<110 or x> size[0]-110:
                move = 0
            elif x < size[0]/2 and slope[0]:
                move = random.choice([-BLOCK_SIZE, -2*BLOCK_SIZE, 0])
            elif x > size[0]/2 and slope[1]:
                move = random.choice([2*BLOCK_SIZE, 0, BLOCK_SIZE])
            else:
                move = random.choice([-BLOCK_SIZE, 0, BLOCK_SIZE])
                
                
            # Keep terrain within screen bounds
            if current_height + move > size[1] - 50: 
                move = -BLOCK_SIZE # Force up if too low
            elif current_height + move < size[1] - 300:
                move = BLOCK_SIZE  # Force down if too high
       
            current_height += move     
            # Append this height for every pixel in the block
            for _ in range(BLOCK_SIZE):
                if len(y) < size[0]: # Safety check
                    y.append(current_height)            
        
        self.y =  y
        if random.choice([True,False]): # 50 / 50 chance of reverse
            self.y.reverse() 
        # mask for burnt    
        self.burnt = [0]*size[0] 
         
    def draw(self,screen):
        for x, y in enumerate(self.y): # Draw the dirt (Brown) from y to the bottom of screen
            pygame.draw.line(screen, DIRT_BROWN, 
                             (x, y), (x, self.size[1]) 
                             )
            if self.burnt[x] == 0:
                pygame.draw.line(screen, GRASS_GREEN, (x, y), (x, y + 3*BLOCK_SIZE))
                
    def destroy(self, impact_x, radius = 20):
        """Creates a semi-circular crater at the impact point"""
        
        start_x = max(0, int(impact_x - radius))
        end_x = min(self.size[0], int(impact_x + radius))

        for x in range(start_x, end_x):
            dist_x = abs(x - impact_x)
            # TODO : include the y-dimension in the dist_x calculation
            if dist_x < radius:
                depth = math.sqrt(radius**2 - dist_x**2)
                
                # Push the ground "down" (increase Y value)
                self.y[x] += depth
                self.y[x] = min(self.size[1], self.y[x])
                self.burnt[x] = 1


def generate_stars(num_stars, screen_width, screen_height):
    """Creates a list of (x, y) positions for stars"""
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height - 200) # Keep stars out of the lowest ground
        stars.append((x, y))
    return stars
    

class Cloud:
    def __init__(self, screen_width, screen_height, wind = 0):
        """Initialize a cloud with random size and position"""
        self.width = random.randint(50, 100)
        self.height = random.randint(20, 40)
        
        # Start at a random x , Random y in the top 1/3rd of the screen
        self.x = random.randint(0, screen_width)
        self.y = random.randint(20, screen_height // 3)
        
        # Random speed with wind affecting the result
        self.wind_change(wind)
        # Screen boundaries for resetting
        self.screen_w = screen_width

    def wind_change(self, wind = 0):
        # Random speed with wind affecting the result
        self.speed = int(wind/10)*random.uniform(0.2, 0.8)
        
    def update(self, wind = 0):
        """Move the cloud right"""
        self.x += self.speed
        
        # If cloud moves off screen to the right, wrap to the left
        if self.x > self.screen_w and self.speed > 0:
            self.x = -self.width
            # Optional: Randomize Y again when it resets
            self.y = random.randint(20, self.screen_w // 3)
        # If cloud moves off screen to the right, wrap to the left
        if self.x < 0 and self.speed <0 :
            self.x = self.screen_w + self.width
            self.y = random.randint(20, self.screen_w // 3)   

    def draw(self, screen):
        """Draws the shadow first, then the cloud"""
        shadow_rect = (self.x + 4, self.y + 4, self.width, self.height)
        pygame.draw.ellipse(screen, STAR_COLOR, shadow_rect)
        # Draw Main Body (WHITE)
        body_rect = (self.x, self.y, self.width, self.height)
        pygame.draw.ellipse(screen, WHITE, body_rect)        

class Castle:
    health = 100
    power = 50
    def __init__(self, x_pos, y_pos, image_path, flipped = False , initial_angle = 50):
        """ Initializes a Player (castle)"""
        # Load, scale, and flip the image
        try:
            image = pygame.image.load(image_path).convert_alpha()
            width = 40
            height = int(image.get_height() * (width / image.get_width()))
            self.image = pygame.transform.scale(image, (width, height))
            if flipped:
                self.image = pygame.transform.flip(self.image, True, False)
        except pygame.error:
            print(f"Warning: Could not load {image_path}. Using a placeholder.")
            self.image = pygame.Surface((40, 40))
            self.image.fill((150, 100, 50)) # Brown placeholder

        # Set position and rect. We use .midbottom to make it sit perfectly on the terrain
        self.rect = self.image.get_rect(midbottom=(x_pos, y_pos))
        
        # Game attributes
        self.angle = initial_angle
        self.flipped = flipped
        
        # Cannon position (relative to the rect's top-left)
        if flipped:
            self.cannon_offset = (5, 12) # (x, y) offset from top-left
        else:
            self.cannon_offset = (35, 12) # (x, y) offset from top-left

    def get_cannon_pos(self):
        """Returns the absolute (x, y) screen position of the cannon's tip"""
        x = self.rect.left + self.cannon_offset[0]
        y = self.rect.top + self.cannon_offset[1]
        return (x, y)

    def update_angle(self, amount):
        """Changes the angle, clamping it between 0 and 180 degrees"""
        if self.flipped:
            self.angle -= amount
            self.angle = max(90, min(180, self.angle))
        else:
            self.angle += amount
            self.angle = max(0, min(90, self.angle))

    def update_power(self, amount):
        """Changes the power, clamping it between 0 and 100"""
        if self.flipped:
            self.power -= amount
        else:
            self.power += amount
        self.power = max(0, min(100, self.power))

    def fire(self, wind = 0):
        """
        Creates and returns a new Shell object based on
        the player's current angle and power.
        """
        power_scale = 800 # A scaling factor
        v_0 = math.sqrt(self.power*power_scale)
        start_pos = self.get_cannon_pos()
        
        return Shell(start_pos[0], start_pos[1], v_0, self.angle, wind)

    def take_damage(self, u,v, wind = 0):
        ''' damage on impact as a direct hit '''
        vel = math.sqrt((u+wind)**2+v**2)
        amount = max(10,min(20*vel/300,20))
        amount = int(amount)
        self.health -= amount
        print(f"Velocity on impact {vel:.0f}")
        return amount

    def draw(self, screen):
        """Draws the player's castle to the screen with the BLIT function"""
        screen.blit(self.image, self.rect)

    def draw_aiming_vector(self, screen):
        """Draws the white line indicating aim"""
        start_pos = self.get_cannon_pos()
        angle_rad = math.radians(self.angle)
        
        end_x = start_pos[0] + (self.power * math.cos(angle_rad))
        end_y = start_pos[1] - (self.power * math.sin(angle_rad)) # Negative for Y-axis
        
        # TODO Changing color
        pygame.draw.line(screen, (255, 255, 0), start_pos, (int(end_x), int(end_y)), 4)

class Shell:
    clock = 0
    def __init__(self,x_0,y_0,v_0, angle, wind = 0):
        ''' velocity is in the frame of the wind gust'''
        self.pos_x, self.pos_y =  x_0, y_0
        self.vel_x = v_0*math.cos(angle*math.pi/180) - wind
        self.vel_y = v_0*math.sin(angle*math.pi/180)

        self.rect = pygame.Rect(int(self.pos_x), int(self.pos_y), 5, 5) # Small rect for collision
        self.x_list, self.y_list = [x_0], [y_0] # storage
        
    def update(self, wind = 0):
        vel = math.sqrt(self.vel_x**2 + self.vel_y**2)
        #update
        self.clock += DT
        self.pos_x += (self.vel_x + wind)*DT
        self.pos_y -= self.vel_y*DT  
        self.vel_x -= MU*vel*self.vel_x*DT
        self.vel_y -= (G + MU*vel*self.vel_y)*DT

        # new lines
        self.rect.center = (self.pos_x,self.pos_y )
        self.x_list.append(self.pos_x)
        self.y_list.append(self.pos_y)
        
        return (self.clock, self.vel_x , self.vel_y , self.pos_x , self.pos_y)
        
    def trajectory(self, wind = 0):
        # Index(['time', 'vel_x', 'vel_y', 'pos_x', 'pos_y'], dtype='object')
        pos_y = self.df['pos_y'].iloc[-1]
        while pos_y >= 0: # collision check // active == True
            self.update()
            pos_y = self.df['pos_y'].iloc[-1]
             
    def draw(self, screen):
        """Draws the shell as a simple circle"""
        pygame.draw.circle(screen, WHITE, self.rect.center, 5)
        n = min(10,len(self.x_list))
        for i in range(n):
            x, y = self.x_list[-i-1], self.y_list[-i-1] 
            pygame.draw.circle(screen, WHITE, (x,y), 1)

    def check_collision(self, terrain, other_player_rect, screen_width, screen_height):
        """
        Returns: 'HIT_TERRAIN', 'HIT_PLAYER', 'OFF_SCREEN', or None
        """
        x_int, y_int = self.rect.center
        
        # Check terrain collision
        if 0 <= x_int < screen_width and y_int >= terrain.y[x_int]:
            return 'HIT_TERRAIN'
            
        # Check other player collision
        if self.rect.colliderect(other_player_rect):
            return 'HIT_PLAYER'
        
        # Check off-screen
        if x_int < 0 or x_int >= screen_width or y_int > screen_height:
            return 'OFF_SCREEN'
    
    def plot(self, ax = None):
        ''' Experimental method to draw the trajectory'''
        if ax is None:
            fig, ax = plt.subplots()
        
        ax.plot(demo.df['pos_x'], demo.df['pos_y'])

        ax.set(xlabel='distance', ylabel='distance',
               title='Shell trajectory')
        ax.grid()
        ax.axis('equal')
        plt.show()
        return ax
        
class Explosion:
    radius, max_radius = 1, 30
    color_core = (255, 255, 0) # Yellow
    color_edge = (255, 0, 0)   # Red
    
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.active = True
        
    def update(self):
        self.radius += 2
        if self.radius > self.max_radius:
            self.active = False

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.color_edge, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, self.color_core, (int(self.x), int(self.y)), int(self.radius * 0.7))

class FloatingText:
    color=(255, 50, 50)
    timer = int(2/DT) # Persist for 1 second
    def __init__(self, x, y, text):
        self.x, self.y = x, y 
        # assumption text is number
        self.text = str(int(text))
        
    def update(self):
        self.y -= 2        # Move upward speed
        self.timer -= 1
            
    def draw(self, screen, font):
        if self.timer >0 :
            text_surf = font.render(self.text, True, self.color)
            screen.blit(text_surf, (self.x, self.y))

if __name__ == '__main__':
    demo= Shell(0,0,300,70)
    demo.trajectory()
    print(demo.df['time'])
    ax = demo.plot()





