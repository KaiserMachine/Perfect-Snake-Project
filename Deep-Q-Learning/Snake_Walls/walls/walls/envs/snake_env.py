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
BROWN = pygame.Color(139, 69, 19)




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
        Returns Boolean indicating if Snake has "eaten" the white food square
        '''
        if self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]:
            return True
        return False
    
    def spawn_wall(self):
        '''
        Spawns a 1x10 vertical wall in the middle
        '''
        #return [self.frame_size_x // 2, self.frame_size_y // 2 - 50]
        wall_pos = []
        for i in range(-3, 3):
            wall_pos.append([self.frame_size_x // 2,  self.frame_size_y // 2 + (i * 10)])
        return wall_pos
    
    def spawn_food(self):
        '''
        Spawns 3 food at random locations on window size
        NOTE: Make sure they never spawn on each other!
        '''
        food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
        # Make sure we don't spawn on a wall!
        # Check pos flag
        check_pos = True
        # While we are checking
        while check_pos:
            # Set check pos to false
            check_pos = False
            # For each block in a wall
            for block in self.wall_pos:
                # If Food pos is equal to a block
                while food_pos == block:
                    # Find a random position
                    food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
                    # Check position again later
                    check_pos = True
        return food_pos


    def item_handler(self):
        if self.eat():
            #print("EATING")
            self.score += 1
            reward = 10
            self.item_spawn = False
            #print("Eating!")
        else:
            self.snake_body.pop()
            reward = 0

        if not self.item_spawn:
            #print("WHY?")
            self.food_pos = self.spawn_food()

        self.item_spawn = True
  
        #if reward != 0:
            #print("REWARD:", reward)

        return reward

    def update_game_state(self):
        self.game_window.fill(BLACK)
        # Draw Wall
        for pos in self.wall_pos:
            pygame.draw.rect(self.game_window, BROWN, pygame.Rect(pos[0], pos[1], 10, 10))
        
        # Draw Snake
        for pos in self.snake_body:
            pygame.draw.rect(self.game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

        # Draw Food
        pygame.draw.rect(self.game_window, WHITE, pygame.Rect(self.food_pos[0], self.food_pos[1], 10, 10))

    def get_image_array_from_game(self):
        img = array3d(display.get_surface())
        img = np.swapaxes(img, 0, 1)
        return img

    def game_over(self, reward):
        # TOUCH BOX
        if self.snake_pos[0] < 0 or self.snake_pos[0] > self.frame_size_x-10:
            return -10, True
        if self.snake_pos[1] < 0 or self.snake_pos[1] > self.frame_size_y-10:
            return -10, True

        # TOUCH SELF
        for block in self.snake_body[1:]:
            if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                return -10, True

        # TOUCH WALL
        for block in self.wall_pos:
            if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                return -10, True

        # LONGER THAN ALLOTED TIME
        if self.steps >= 1000:
            return 0, True
        
        return reward, False



    def reset(self):
        self.game_window.fill(BLACK)
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
        self.wall_pos = self.spawn_wall()
        self.food_pos = self.spawn_food()        

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
