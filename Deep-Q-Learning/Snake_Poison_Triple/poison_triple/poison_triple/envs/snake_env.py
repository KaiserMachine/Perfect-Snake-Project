import time

import numpy as np

import gym
from gym import error, spaces, utils
from gym.utils import seeding

import pygame, sys, time, random
from pygame.surfarray import array3d
from pygame import display

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)




class SnakeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(0, 255, shape=(200, 200, 3), dtype=np.uint8)
        self.frame_size_x = 200
        self.frame_size_y = 200
        self.game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_y))
        self.reset()
        self.STEP_LIMIT = 1000
        self.sleep = 0

    def step(self, action):
        scoreholder = self.score
        reward = 0
        self.direction = SnakeEnv.change_direction(action, self.direction)
        self.snake_pos = SnakeEnv.move(self.direction, self.snake_pos)
        self.snake_body.insert(0, list(self.snake_pos))

        reward = self.item_handler()

        self.update_game_state()

        reward, done = self.game_over(reward)

        img = self.get_image_array_from_game()
        info = {"score": self.score}
        self.steps += 1
        time.sleep(self.sleep)
        return img, reward, done, info

    @staticmethod
    def change_direction(action, direction):
        if action == 0 and direction != "DOWN":
            direction = 'UP'
        if action==1 and direction != "UP":
            direction = 'DOWN'
        if action==2 and direction != "RIGHT":
            direction = 'LEFT'
        if action==3 and direction != "LEFT":
            direction = 'RIGHT'
        return direction

    @staticmethod
    def move(direction, snake_pos):
        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10
        return snake_pos


    def eat(self):
        '''
        Returns Boolean indicating if Snake has "eaten" the white food square OR the red poison square
        '''
        for food_pos in self.food_items:
             if self.snake_pos[0] == food_pos[0] and self.snake_pos[1] == food_pos[1]:
                    return True
        return False
    
    def poisoned(self):
        '''
        Returns Boolean indicating if Snake has "eaten" the red poison square
        '''
        for poison_pos in self.poison_items:
             if self.snake_pos[0] == poison_pos[0] and self.snake_pos[1] == poison_pos[1]:
                    return True
        return False
    
    
    def spawn_food(self):
        '''
        Spawns 3 food at random locations on window size
        NOTE: Make sure they never spawn on each other!
        '''
        # Set food_items to null
        food_items = []
        
        # A for loop for 3 iterations
        for i in range(3):
            # Get a random food position
            food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
            # For each item in food_items
            for item in food_items:
                # While item is equal to the food_pos... (Rare event)
                while item == food_pos:
                    # Respawn the food
                    food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
            # Append the food to food_pos
            food_items.append(food_pos)
        
        return food_items

    def spawn_poison(self):
        '''
        Spawns 3 poisons at a random location on window size
        ALSO: Make sure it NEVER spawns on the food!
        '''
        # Set poison items to null
        poison_items = []
        
        # A for loop for 3 iterations
        for i in range(3):
            # Get a random poison position
            poison_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
            # For each item in self.food_items
            for item in self.food_items:
                # While item is equal to the poison_pos... (Rare event)
                while item == poison_pos:
                    # Respawn the poison
                    poison_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
            for item in poison_items:
                # While item is equal to the poison_pos... (Rare event)
                while item == poison_pos:
                    # Respawn the poison
                    poison_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
            
            # Append the poison to poison_pos
            poison_items.append(poison_pos)
            
        return poison_items


    def item_handler(self):
        if self.eat():
            #print("EATING")
            self.score += 1
            reward = 10
            self.item_spawn = False
            #print("Eating!")
        elif self.poisoned():
            if self.score > 0:
                self.score -= 1
            reward = -1
            self.item_spawn = False
            #print("Poisoned!")
        else:
            self.snake_body.pop()
            reward = 0

        if not self.item_spawn:
            #print("WHY?")
            self.food_items = self.spawn_food()
            self.poison_items = self.spawn_poison()
        self.item_spawn = True
  
        #if reward != 0:
            #print("REWARD:", reward)

        return reward

    def update_game_state(self):
        self.game_window.fill(BLACK)
        for pos in self.snake_body:
            pygame.draw.rect(self.game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

        # Draw Food
        for food_pos in self.food_items:
            pygame.draw.rect(self.game_window, WHITE, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

        # Draw Poison
        for poison_pos in self.poison_items:
            pygame.draw.rect(self.game_window, RED, pygame.Rect(poison_pos[0], poison_pos[1], 10, 10))

    def get_image_array_from_game(self):
        img = array3d(display.get_surface())
        img = np.swapaxes(img, 0, 1)
        return img

    def game_over(self, reward):
        if self.snake_pos[0] < 0 or self.snake_pos[0] > self.frame_size_x-10:
            return -10, True
        if self.snake_pos[1] < 0 or self.snake_pos[1] > self.frame_size_y-10:
            return -10, True

        for block in self.snake_body[1:]:
            if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                return -10, True
        if self.steps >= 1000:
            return 0, True
        
        return reward, False



    def reset(self):
        self.game_window.fill(BLACK)
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
        self.food_items = self.spawn_food()        
        self.poison_items = self.spawn_poison()
        self.item_spawn = True

        self.direction = "RIGHT"
        self.change_to = self.direction
        self.score = 0
        self.steps = 0
        img = array3d(display.get_surface())
        img = np.swapaxes(img, 0, 1)
        return img


    def render(self, mode='human'):
        if mode == "human":
            display.update()
            # DELETE IF IT DOESN'T WORK
            #time.sleep(.05)
            
    def close(self):
        pass
