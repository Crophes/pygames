import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple("Point", "x, y")

BLOCK_SIZE = 40
# window size needs to be even multiplier of blocksize cause draw_grid
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 480
INITIAL_SPEED = 6

# rgb/hex colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN_DARK = "#4f7353"
GREEN_LIGHT = "#7ba57e"
BROWN_DARK = "#E0AB8B"
BROWN_LIGHT = "#B06C49"

class SnakeGame:

    def __init__(self, w=WINDOW_WIDTH, h=WINDOW_HEIGHT):
        self.w = w
        self.h = h
        self.speed = INITIAL_SPEED
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(BLOCK_SIZE, self.h/2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y),
        ]
        self.left, self.right, self.up, self.down = True,True,True,True

        self.score = 0
        self._place_food()

    def _place_food(self):
        while True:
            x = round(sum(random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) for __ in range(2))/2) *BLOCK_SIZE
            y = round(sum(random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) for __ in range(2))/2) *BLOCK_SIZE
            self.food = Point(x, y)

            if self.food not in self.snake:
                break

    def play_step(self):
        # collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a) and self.left:
                    self.direction = Direction.LEFT
                    self.left, self.right, self.up, self.down = True,False,True,True
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.right:
                    self.direction = Direction.RIGHT
                    self.left, self.right, self.up, self.down = False,True,True,True                    
                elif event.key in (pygame.K_UP, pygame.K_w) and self.up:
                    self.direction = Direction.UP
                    self.left, self.right, self.up, self.down = True,True,True,False
                elif event.key in (pygame.K_DOWN, pygame.K_s) and self.down:
                    self.direction = Direction.DOWN
                    self.left, self.right, self.up, self.down = True,True,False,True


        # move
        self._move(self.direction)  # update the head
        self.snake.insert(0, self.head)

        # check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over

        # place new food or just move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)

        # win condition
        max_size = (WINDOW_WIDTH*  WINDOW_HEIGHT)//BLOCK_SIZE**2
        win_size = max_size - 4
        if self.score == win_size:
            game_over=True
            return game_over

        # return game over
        return game_over

    def _is_collision(self):
        # hits boundary
        if (
            self.head.x > self.w - BLOCK_SIZE
            or self.head.x < 0
            or self.head.y > self.h - BLOCK_SIZE
            or self.head.y < 0
        ):
            return True
        
        # hits itself
        if self.head in self.snake[1:]:
            return True
        return False

    def _update_ui(self):

        # draws background
        self.display.fill(BROWN_LIGHT)
        self.draw_grid()

        # draws snake 
        self.draw_snake()

        # draws food
        self.draw_food()

        pygame.display.flip()

    def draw_snake(self):
        for pt in self.snake:
            if pt == self.snake[0]:
                pygame.draw.rect(
                    self.display, GREEN_LIGHT, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)
                )
            else:
                pygame.draw.rect(
                    self.display, GREEN_DARK, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)
                )
            # Not sure if snake looks better with or without borders
            # pygame.draw.rect(
            #     self.display, BLACK, pygame.Rect(pt.x, pt.y, BLOCK_SIZE,BLOCK_SIZE),1
            # )

    def draw_grid(self):
        i = 0
        for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
            i += 1
            for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
                i += 1
                if i % 2 != 0:
                    continue

                rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.display, BROWN_DARK, rect, BLOCK_SIZE)

    def draw_food(self):
        pygame.draw.circle(
        self.display,
        RED,
        (self.food.x + BLOCK_SIZE // 2, self.food.y + BLOCK_SIZE // 2),
        BLOCK_SIZE // 2.2
    )

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)


if __name__ == "__main__":
    game = SnakeGame()

    # game loop
    while True:
        game_over = game.play_step()

        if game_over == True:
            pygame.time.wait(100)
            break

    pygame.quit()
