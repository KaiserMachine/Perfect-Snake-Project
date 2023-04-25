# Imports
import math

import pygame, sys, time, random, heapq
from pygame.surfarray import array3d
import os

# Colors to use in the game
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
DARK_BLUE = pygame.Color(0, 0, 125)
YELLOW = pygame.Color(255, 255, 0)

# OPTIONS:

# Determines the seed to use for the game
seed = 11

# Determines whether we draw a grid for each node or not
drawing_grid = False

# PERFECT SEEDS
# USE THIS FOR 8x8!
# ALL PERFECT ON: (6x6), (8x8), (10x10), (20x20)
#random.seed(0)
#random.seed(10)
#random.seed(20)
#random.seed(50)
#random.seed(100)
random.seed(seed)


# Snake Environment Class For The
class SnakeEnv():

    # Initialize everything
    def __init__(self, frame_size_x, frame_size_y, block_size):
        self.frame_size_x = frame_size_x
        self.frame_size_y = frame_size_y
        self.game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
        self.block_size = block_size

        self.reset()

    # Reset the game at the start and set everything up
    def reset(self):
        self.game_window.fill(BLACK)
        self.snake_pos = [self.block_size * 2, 0]
        self.snake_body = [[self.block_size * 2, 0], [self.block_size * 1, 0], [0, 0]]
        self.food_pos = self.spawn_food()
        self.food_spawn = True

        self.direction = "RIGHT"
        self.action = self.direction

        grid_x = self.frame_size_x // self.block_size
        grid_y = self.frame_size_y // self.block_size

        grid = [[0 for _ in range(grid_x)] for _ in range(grid_y)]

        self.skipping_direction = None
        self.skipping_pos = 0
        self.path = self.find_hamiltonian_path((2, grid_y-1), True)

        self.score = 0
        self.steps = 0

    # Change the direction if possible
    def change_direction(self, action, direction):
        if action == "UP" and direction != "DOWN":
            direction = "UP"
        if action == "DOWN" and direction != "UP":
            direction = "DOWN"
        if action == "LEFT" and direction != "RIGHT":
            direction = "LEFT"
        if action == "RIGHT" and direction != "LEFT":
            direction = "RIGHT"

        return direction

    # Move based on direction
    def move(self, direction, snake_pos):
        if direction == "UP":
            snake_pos[1] -= self.block_size
        if direction == "DOWN":
            snake_pos[1] += self.block_size
        if direction == "LEFT":
            snake_pos[0] -= self.block_size
        if direction == "RIGHT":
            snake_pos[0] += self.block_size
        return snake_pos

    # Check if we can spawn the food
    # Outdated really...
    def can_spawn_food(self):
        # Free positions QUick Check!
        for x in range(0, self.frame_size_x, self.block_size):
            for y in range(0, self.frame_size_y, self.block_size):
                if [x, y] not in self.snake_body:
                    return True

        return False

    # Spawn the food
    def spawn_food(self):
        food_pos = [random.randrange(0, (self.frame_size_x // self.block_size)) * self.block_size,
                    random.randrange(0, self.frame_size_y // self.block_size) * self.block_size]
        # Make Sure the food does not spawn on the snake itself!
        check = True
        while check:
            check = False
            for item in self.snake_body:
                if food_pos == item:
                    food_pos = [random.randrange(0, (self.frame_size_x // self.block_size)) * self.block_size,
                                random.randrange(0, self.frame_size_y // self.block_size) * self.block_size]
                    check = True
        return food_pos

    # See if we are going to eat the food
    def eat(self):
        return self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]

    # Human Input (Used to change speed by pressing space for fast or p for slow)
    def human_step(self, event, difficulty):
        # action = None

        # difficulty = 10

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if difficulty == 10:
                    difficulty = 100
                else:
                    difficulty = 10
            if event.key == pygame.K_p:
                if difficulty != 1:
                    difficulty = 1
                else:
                    difficulty = 10

        return difficulty
        # return action

    # Displays the score
    def display_score(self, color, font, size):
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render("Score: " + str(self.score), True, color)

        score_rect = score_surface.get_rect()
        score_rect.midtop = (self.frame_size_x / 10, 15)

        self.game_window.blit(score_surface, score_rect)

    # Checks if we lose the game
    def game_over(self):
        # TOUCH BOX
        if self.snake_pos[0] < 0 or self.snake_pos[0] > self.frame_size_x - self.block_size:
            self.end_game()
        if self.snake_pos[1] < 0 or self.snake_pos[1] > self.frame_size_y - self.block_size:
            self.end_game()

        # BODY
        for block in self.snake_body[1:]:
            if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                self.end_game()

    # Ends the game and displays a win or lose message
    def end_game(self):
        print(self.score)
        message = pygame.font.SysFont('arial', 45)

        message_surface = message.render("GAME HAS ENDED", True, RED)

        if len(snake_env.snake_body) >= (snake_env.frame_size_x // snake_env.block_size) * (snake_env.frame_size_x // snake_env.block_size) :
            message_surface = message.render("YOU WON!", True, GREEN)

        message_rect = message_surface.get_rect()
        message_rect.midtop = (self.frame_size_x / 2, self.frame_size_y / 4)

        self.game_window.fill(BLACK)
        self.game_window.blit(message_surface, message_rect)
        self.display_score(RED, 'TIMES', 20)
        if len(snake_env.snake_body) >= (snake_env.frame_size_x // snake_env.block_size) * (snake_env.frame_size_x // snake_env.block_size):
            self.display_score(GREEN, 'TIMES', 20)
        pygame.display.flip()
        time.sleep(3)
        pygame.quit()
        sys.exit()

    """Hamiltonian Cycle Work!!!"""
    # Finds a Hamiltonian Path and creates it
    def find_hamiltonian_path(self, start, first_time=True):
        # Set Path ID to 0
        self.path_id = 0

        if not first_time:
            return self.premade_path

        # Define the grid based on the size
        grid_x_and_y_dim = self.frame_size_x // self.block_size
        grid = [[1 for _ in range(grid_x_and_y_dim)] for _ in range(grid_x_and_y_dim)]

        # Define the directions to move on the grid
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        direction_names = ["RIGHT", "DOWN", "LEFT", "UP"]

        # Define a function to check if a cell is a valid move
        def is_valid_move(cell, visited):
            x, y = cell
            if not (0 <= x < len(grid) and 0 <= y < len(grid[0])):
                return False
            if grid[x][y] == 0:
                return False
            if cell in visited:
                return False
            return True

        # Define a recursive function to find a Hamiltonian cycle
        def dfs(node, visited, prev_node=None):
            visited.add(node)
            if len(visited) == len(grid) * len(grid[0]):
                # All cells have been visited... check if the last cell is adjacent to the first cell
                if node in grid_adjacents[visited_list[0]]:
                    visited_list.append(visited_list[0])
                    return True
            for dx, dy in directions:
                neighbor = (node[0] + dx, node[1] + dy)
                if is_valid_move(neighbor, visited):
                    visited_list.append(neighbor)
                    if dfs(neighbor, visited, node):
                        return True
                    visited_list.pop()
            visited.remove(node)
            return False

        # Build a dictionary of adjacent nodes for each cell in the grid
        grid_adjacents = {}
        directions_list = []
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                adjacents = []
                for dx, dy in directions:
                    x, y = i + dx, j + dy
                    if is_valid_move((x, y), set()):
                        adjacents.append((x, y))
                        direction_index = directions.index((dx, dy))
                        directions_list.append(direction_names[direction_index])
                grid_adjacents[(i, j)] = adjacents

        # Try to find a Hamiltonian cycle starting from the specified cell
        visited_list = [start]
        if dfs(start, set([start])):
            cycle = visited_list + [visited_list[0]]

            # return directions_list
            path = []

            for i in range(0, len(cycle) - 2):
                cur_move = cycle[i]
                next_move = cycle[i + 1]

                # GOING RIGHT
                if cur_move[0] < next_move[0]:
                    path.append("RIGHT")
                # GOING LEFT
                elif cur_move[0] > next_move[0]:
                    path.append("LEFT")
                # Going UP
                elif cur_move[1] < next_move[1]:
                    path.append("UP")
                # Going DOWN
                elif cur_move[1] > next_move[1]:
                    path.append("DOWN")
                else:
                    print("ERROR! Path has ERROR!")

            # First Time Work
            if first_time:
                # New Cycle needs the be the cycle minus the last two elements (We duplicate 0 twice at the end for some reason?)
                new_cycle = cycle[0:-2]
                path_positions = {}

                # Set an id (0: length of cycle - 1) and apply a coordinate to it
                for i in range(len(new_cycle)):
                    # Create an old pos of the ACTUAL board position and implement that into the path_positions
                    old_pos = new_cycle[i][0] * self.block_size, ((len(grid)-1) - new_cycle[i][1]) * self.block_size

                    # Old Way
                    #path_positions[(new_cycle[i][0], new_cycle[i][1])] = (i, (old_pos))

                    # Get the neighbor nodes for each node
                    possible_neighbors = []

                    possible_neighbors.append((old_pos[0] + self.block_size, old_pos[1]))
                    possible_neighbors.append((old_pos[0] - self.block_size, old_pos[1]))
                    possible_neighbors.append((old_pos[0], old_pos[1] + self.block_size))
                    possible_neighbors.append((old_pos[0], old_pos[1] - self.block_size))

                    neighbors = []

                    for neighbor in possible_neighbors:
                        if neighbor[0] >= 0 and neighbor[0] < self.frame_size_x and neighbor[1] >= 0 and neighbor[1] < self.frame_size_y:
                            neighbors.append(neighbor)
                    # Set up path positions: key = old_pos, values = position in cycle, cycle position
                    path_positions[old_pos] = (i, (new_cycle[i][0], new_cycle[i][1]), neighbors)

                # Set them as part of the snake env
                self.path_positions = path_positions
                self.premade_path = path

            return path

        # No Hamiltonian cycle found
        print("ERROR! No cycle found!")
        return None

    # Enables us to skip paths early in the game
    # Skipping conditions: Tail > 0, Head < Apple Position, Make sure the neighboring node is less than the food pos, but greater than the next pos
    def path_skipping(self):
        # Skip if length of snake body is greater than half the length of the grid
        size_grid_half = (self.frame_size_x // self.block_size) * (self.frame_size_x // self.block_size) // 2
        #print(size_grid_half)
        if len(self.snake_body) >= size_grid_half:
            return None, None
        # Get the path id of and manhattan distance to the food
        food_path_pos, food_path_grid, _ = self.path_positions[tuple(self.food_pos)]
        snake_path_pos, _, snake_path_neighbors = self.path_positions[tuple(self.snake_pos)]
        #print("SPP", snake_path_pos)
        # Make sure the tail is less than the snake path pos before skipping
        tail_path_pos, _, _, = self.path_positions[tuple(self.snake_body[-1])]
        if tail_path_pos < snake_path_pos:
            # See if the neighboring node is less than the food position but greater than the next position
            lowest_distance = math.inf
            lowest_neighbor = None
            lowest_neighbor_pos = 0
            for neighbor in snake_path_neighbors:
                neighbor_path_pos, neighbor_path_grid, _ = self.path_positions[tuple(neighbor)]
                # Check if the neighbor is closer to the food
                if abs(food_path_pos - neighbor_path_pos) < lowest_distance:
                    lowest_neighbor = neighbor
                    lowest_neighbor_pos = neighbor_path_pos
                    lowest_distance = abs(food_path_pos - neighbor_path_pos)
            # If so, go to that position if it does not overtake a position of the tail or body
            #print("LOWEST NEIGHBOR:", lowest_neighbor_pos, "FOOD", food_path_pos)
            # Make sure the lowest neighbor position is greater than the snake path position
            # AND make sure new lowest neighbor pos is less than or equal to food pos!
            if lowest_neighbor_pos > snake_path_pos and lowest_neighbor_pos <= food_path_pos:
                return lowest_neighbor, lowest_neighbor_pos
            else:
                return None, None
        return None, None


# Comment out to choose the map size!
# NOTE: 30x30 does NOT work!

# MAP SIZE
# 30 x 30 (Warning! Very Slow)
#snake_env = SnakeEnv(600, 600, 20)
# 20 x 20
#snake_env = SnakeEnv(500, 500, 25)
# 10 x 10
#snake_env = SnakeEnv(500, 500, 50)
# 8 x 8
#snake_env = SnakeEnv(400, 400, 50)
# 8 x 8 larger
snake_env = SnakeEnv(800, 800, 100)
# 6 x 6
#snake_env = SnakeEnv(600, 600, 100)
# 4 x 4
#snake_env = SnakeEnv(400, 400, 100)

# Difficulty or speed
difficulty = 10

fps_controller = pygame.time.Clock()
check_errors = pygame.init()

# SPRITES
# Apple sprite
apple_img = pygame.image.load(os.path.join("Sprites/apple.png"))
apple_img = pygame.transform.scale(apple_img, (snake_env.block_size, snake_env.block_size))

# Head sprites
head_up_img = pygame.image.load(os.path.join("Sprites/head_up.png"))
head_up_img = pygame.transform.scale(head_up_img, (snake_env.block_size, snake_env.block_size))

head_down_img = pygame.image.load(os.path.join("Sprites/head_down.png"))
head_down_img = pygame.transform.scale(head_down_img, (snake_env.block_size, snake_env.block_size))

head_right_img = pygame.image.load(os.path.join("Sprites/head_right.png"))
head_right_img = pygame.transform.scale(head_right_img, (snake_env.block_size, snake_env.block_size))

head_left_img = pygame.image.load(os.path.join("Sprites/head_left.png"))
head_left_img = pygame.transform.scale(head_left_img, (snake_env.block_size, snake_env.block_size))

# Tail sprites
tail_up_img = pygame.image.load(os.path.join("Sprites/tail_up.png"))
tail_up_img = pygame.transform.scale(tail_up_img, (snake_env.block_size, snake_env.block_size))

tail_down_img = pygame.image.load(os.path.join("Sprites/tail_down.png"))
tail_down_img = pygame.transform.scale(tail_down_img, (snake_env.block_size, snake_env.block_size))

tail_right_img = pygame.image.load(os.path.join("Sprites/tail_right.png"))
tail_right_img = pygame.transform.scale(tail_right_img, (snake_env.block_size, snake_env.block_size))

tail_left_img = pygame.image.load(os.path.join("Sprites/tail_left.png"))
tail_left_img = pygame.transform.scale(tail_left_img, (snake_env.block_size, snake_env.block_size))

# Body Sprites and Corner Sprites
body_left_right_img = pygame.image.load(os.path.join("Sprites/body_left_right.png"))
body_left_right_img = pygame.transform.scale(body_left_right_img, (snake_env.block_size, snake_env.block_size))

body_up_down_img = pygame.image.load(os.path.join("Sprites/body_up_down.png"))
body_up_down_img = pygame.transform.scale(body_up_down_img, (snake_env.block_size, snake_env.block_size))

corner_top_left = pygame.image.load(os.path.join("Sprites/corner_top_left.png"))
corner_top_left = pygame.transform.scale(corner_top_left, (snake_env.block_size, snake_env.block_size))

corner_top_right = pygame.image.load(os.path.join("Sprites/corner_top_right.png"))
corner_top_right = pygame.transform.scale(corner_top_right, (snake_env.block_size, snake_env.block_size))

corner_bottom_left = pygame.image.load(os.path.join("Sprites/corner_bottom_left.png"))
corner_bottom_left = pygame.transform.scale(corner_bottom_left, (snake_env.block_size, snake_env.block_size))

corner_bottom_right = pygame.image.load(os.path.join("Sprites/corner_bottom_right.png"))
corner_bottom_right = pygame.transform.scale(corner_bottom_right, (snake_env.block_size, snake_env.block_size))

pygame.display.set_caption("Snake Game")

# Main Logic
while True:

    # Human Input
    # Used to change difficulty
    for event in pygame.event.get():
        difficulty = snake_env.human_step(event, difficulty)

    # Get the path when we go through the path
    # Set the path if first time running, or choose the old path.
    if snake_env.path_id >= len(snake_env.path):
        start_pos = (snake_env.snake_pos[0], snake_env.snake_pos[1])
        snake_env.path = snake_env.find_hamiltonian_path((2, (snake_env.frame_size_y // snake_env.block_size)-1), False)


    # Code to determine movement
    # We skip if skipping direction is not none
    if snake_env.skipping_direction == None:
        snake_env.action = snake_env.path[snake_env.path_id]
        snake_env.direction = snake_env.change_direction(snake_env.action, snake_env.direction)
        snake_env.snake_pos = snake_env.move(snake_env.direction, snake_env.snake_pos)
        snake_env.path_id += 1
    else:
        snake_env.action = snake_env.skipping_direction
        snake_env.direction = snake_env.change_direction(snake_env.action, snake_env.direction)
        snake_env.snake_pos = snake_env.move(snake_env.direction, snake_env.snake_pos)
        snake_env.path_id = snake_env.skipping_pos
        #print("SKIPPING POS", snake_env.skipping_pos)

    # DO path skipping here
    snake_env.skipping_direction = None

    path_skipped, skip_pos = snake_env.path_skipping()

    # Follow the regular path if not skipping
    if path_skipped != None:

        cur_move = snake_env.snake_pos
        next_move = path_skipped

        new_direction = ""

        # GOING RIGHT
        if cur_move[0] < next_move[0]:
            new_direction = "RIGHT"
        # GOING LEFT
        elif cur_move[0] > next_move[0]:
            new_direction = "LEFT"
        # Going UP
        elif cur_move[1] < next_move[1]:
            new_direction = "DOWN"
        # Going DOWN
        elif cur_move[1] > next_move[1]:
            new_direction = "UP"
        else:
            print("ERROR! Cannot find direction!")

        #print("NEW DIR", new_direction)
        snake_env.skipping_direction = new_direction
        snake_env.skipping_pos = skip_pos

    # Check if we ate food
    snake_env.snake_body.insert(0, list(snake_env.snake_pos))
    if snake_env.eat():
        snake_env.score += 1
        if len(snake_env.snake_body) >= (snake_env.frame_size_x // snake_env.block_size) * (snake_env.frame_size_x // snake_env.block_size):
            snake_env.end_game()
        snake_env.food_spawn = False
        # print("BODY AFTER EAT:", snake_env.snake_body)
    else:
        # print("SHAPE B4:", snake_env.snake_body)
        snake_env.snake_body.pop()
        # print("SAHPE AFTER:", snake_env.snake_body)



    # Check if spawn new food
    if snake_env.can_spawn_food():
        if not snake_env.food_spawn:
            snake_env.food_pos = snake_env.spawn_food()
            snake_env.food_spawn = True
            # If we can reach the food...
            #snake_env.set_path()
            """
            can_reach_food, snake_body = snake_env.can_a_star_to_goal(snake_env.food_pos, snake_env.snake_body)
            if can_reach_food:
                # If we can reach the end from the food
                can_reach_end, _ = snake_env.can_a_star_to_goal(snake_body[-1], snake_body)
                print("CAN REACH END:", can_reach_end)
                # print("CAN REACH:", can_reach_food)
                # If we can reach the end...
                # Do a_star to the food
                if can_reach_end:
                    # print("CAN REACH FOOD AND END:", snake_env.score)
                    snake_env.path, _ = snake_env.a_star_to_goal(snake_env.food_pos)
                    # if len(snake_env.path) == 0:
                    #    snake_env.path, _ = snake_env.a_star_to_end()
                # Otherwise a star to the end
                else:
                    #snake_env.path, _ = snake_env.a_star_to_goal(snake_body[-1])
                    snake_env.path, _ = snake_env.a_star_to_goal(snake_env.snake_body[-1])
                    snake_env.finding_end = True
            # If we cannot reach food... a star to end
            else:
                snake_env.path, _ = snake_env.a_star_to_goal(snake_env.snake_body[-1])
                snake_env.finding_end = True
            """


    # Draw the background
    snake_env.game_window.fill(BLACK)

    # Draw the snake
    # Used to see what postiion in the snake we are in for drawing certain parts
    i = 0
    for pos in snake_env.snake_body:
        # Head
        if i == 0:
            next_snake = snake_env.snake_body[1]
            if next_snake[0] < pos[0]:
                snake_env.game_window.blit(head_right_img, head_right_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif next_snake[0] > pos[0]:
                snake_env.game_window.blit(head_left_img, head_left_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif next_snake[1] < pos[1]:
                snake_env.game_window.blit(head_down_img, head_down_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif next_snake[1] > pos[1]:
                snake_env.game_window.blit(head_up_img, head_up_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
        # Tail
        elif i == len(snake_env.snake_body) - 1:
            prev_snake = snake_env.snake_body[i - 1]
            if prev_snake[0] > pos[0]:
                snake_env.game_window.blit(tail_right_img, tail_right_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif prev_snake[0] < pos[0]:
                snake_env.game_window.blit(tail_left_img, tail_left_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif prev_snake[1] < pos[1]:
                snake_env.game_window.blit(tail_down_img, tail_down_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif prev_snake[1] > pos[1]:
                snake_env.game_window.blit(tail_up_img, tail_up_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
        # Body
        else:
            # pygame.draw.rect(snake_env.game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))
            prev_snake = snake_env.snake_body[i - 1]
            next_snake = snake_env.snake_body[i + 1]
            curr_snake = snake_env.snake_body[i]

            if prev_snake[0] < curr_snake[0] and next_snake[0] > curr_snake[0] or next_snake[0] < curr_snake[0] and \
                    prev_snake[0] > curr_snake[0]:
                # Left RIght
                snake_env.game_window.blit(body_left_right_img, body_left_right_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif prev_snake[1] < curr_snake[1] and next_snake[1] > curr_snake[1] or next_snake[1] < curr_snake[1] and \
                    prev_snake[1] > curr_snake[1]:
                # Up Down
                snake_env.game_window.blit(body_up_down_img, body_up_down_img.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif prev_snake[0] < curr_snake[0] and next_snake[1] > curr_snake[1] or next_snake[0] < curr_snake[0] and \
                    prev_snake[1] > curr_snake[1]:
                # Corner Left Down
                #print("corner left down")
                # snake_env.game_window.blit(corner_bottom_left, corner_bottom_left.get_rect(
                #    center=(pos[0] + 4, pos[1] + 4)))
                snake_env.game_window.blit(corner_top_right, corner_top_right.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            elif prev_snake[1] < curr_snake[1] and next_snake[0] < curr_snake[0] or next_snake[1] < curr_snake[1] and \
                    prev_snake[0] < curr_snake[0]:
                # Corner Left Up
                #print("corner left up")
                # snake_env.game_window.blit(corner_top_left, corner_top_left.get_rect(
                #    center=(pos[0] + 4, pos[1] + 4)))
                snake_env.game_window.blit(corner_bottom_right, corner_bottom_right.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
            # else if (pseg.x > segx && nseg.y < segy || nseg.x > segx && pseg.y < segy) {
            elif prev_snake[0] > curr_snake[0] and next_snake[1] < curr_snake[1] or next_snake[0] > curr_snake[0] and \
                    prev_snake[1] < curr_snake[1]:
                # Corner Right Up
                # ACTUALLY corner left down
                #print("corner right up")
                snake_env.game_window.blit(corner_bottom_left, corner_bottom_left.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))
                # snake_env.game_window.blit(corner_top_right, corner_top_right.get_rect(
                #    center=(pos[0] + 4, pos[1] + 4)))
            # } else if (pseg.y > segy && nseg.x > segx || nseg.y > segy && pseg.x > segx) {
            elif prev_snake[1] > curr_snake[1] and next_snake[0] > curr_snake[0] or next_snake[1] > curr_snake[1] and \
                    prev_snake[0] > curr_snake[0]:
                # Corner Right Down
                #print("corner right down")
                # snake_env.game_window.blit(corner_bottom_right, corner_bottom_right.get_rect(
                #    center=(pos[0] + 4, pos[1] + 4)))
                snake_env.game_window.blit(corner_top_left, corner_top_left.get_rect(
                    center=(pos[0] + snake_env.block_size // 2, pos[1] + snake_env.block_size // 2)))

        i += 1

    # Draw the food
    snake_env.game_window.blit(apple_img,
                               apple_img.get_rect(center=(snake_env.food_pos[0] + snake_env.block_size // 2, snake_env.food_pos[1] + snake_env.block_size // 2)))

    # OPTIONAL: Draw a grid!
    # drawing_grid set at beginning
    if drawing_grid:
        for x in range(0, snake_env.frame_size_x, snake_env.block_size):
            for y in range(0, snake_env.frame_size_y, snake_env.block_size):
                rect = pygame.Rect(x, y, snake_env.block_size, snake_env.block_size)
                pygame.draw.rect(snake_env.game_window, WHITE, rect, 1)

    pygame.display.flip()

    # OLD WAY
    #pygame.draw.rect(snake_env.game_window, WHITE, pygame.Rect(snake_env.food_pos[0], snake_env.food_pos[1], 10, 10))

    # Check if end game
    snake_env.game_over()
    # Refresh game screen
    snake_env.display_score(WHITE, 'consolas', 20)

    pygame.display.update()

    fps_controller.tick(difficulty)

    img = array3d(snake_env.game_window)