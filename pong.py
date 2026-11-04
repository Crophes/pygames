import pygame
import random
from enum import Enum
from collections import namedtuple
from gifrecorder import GifRecorder


pygame.init()
# font = pygame.font.SysFont("arial", 25)


class Direction(Enum):
    NONE = 0
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple("Point", "x, y")

BLOCK_SIZE = 20
# window size needs to be even multiplier of blocksize cause draw_grid
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 680
GAME_SPEED = 30
BALL_SPEED = 10
BALL_ANGLE = 4

# rgb/hex colors
WHITE = (255, 255, 255)
GREY = (180, 180, 180)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN_DARK = "#4f7353"
GREEN_LIGHT = "#7ba57e"
BROWN_DARK = "#E0AB8B"
BROWN_LIGHT = "#B06C49"

class PingPong:

    def __init__(self, w=WINDOW_WIDTH, h=WINDOW_HEIGHT):
        self.w = w
        self.h = h
        self.speed = GAME_SPEED

        # # init game state
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Ping Pong")
        self.clock = pygame.time.Clock()

        self.ball = (self.w//2, self.h//2)
        self.ball_size = BLOCK_SIZE//1.5
        self.ball_speed = random.choice([-BALL_SPEED,BALL_SPEED])
        self.ball_angle = random.choice([-BALL_ANGLE,BALL_ANGLE])

        self.paddle_height = self.h//3
        self.paddle = pygame.Rect(BLOCK_SIZE*3, self.paddle_height, self.ball_size, self.paddle_height)
        self.enemy_paddle = pygame.Rect(self.w - BLOCK_SIZE*3, self.paddle_height, self.ball_size, self.paddle_height)

        self.score = 0
        self.game_over = False

        self.recorder = GifRecorder(self.display, scale=0.75)


    def _hit_horizontal_walls(self):
        # hits upper or lower wall
        if self.ball[1] >= self.h - self.ball_size or self.ball[1] <= 0 + self.ball_size:
            return True
        return False
    
    def _hit_vertical_walls(self):
        # hits left or right wall
        if self.ball[0] >= self.w - self.ball_size or self.ball[0] <= 0 + self.ball_size:
            gif_fps = self.speed -1
            self.recorder.save("pong.gif", fps=gif_fps)
            self.game_over = True
        return False

    def _hit_paddle(self):
        max_dist = self.paddle.y -(self.paddle.y + self.paddle_height//2)
        if (self.ball[0] <= self.paddle.x + self.ball_size * 2 and
            self.ball[0] >= self.paddle.x - self.ball_size and
            self.ball[1] >= self.paddle.y and
            self.ball[1] <= self.paddle.y + self.paddle_height):
            ball_dist = abs(self.ball[1] -(self.paddle.y + self.paddle_height//2))
            rel_dist = round(abs(ball_dist/max_dist),2)
            self.score += 1
            return True, rel_dist

        elif (self.ball[0] <= self.enemy_paddle.x + self.ball_size * 2 and
            self.ball[0] >= self.enemy_paddle.x - self.ball_size and
            self.ball[1] >= self.enemy_paddle.y and
            self.ball[1] <= self.enemy_paddle.y + self.paddle_height):
            ball_dist = abs(self.ball[1] -(self.enemy_paddle.y + self.paddle_height//2))
            rel_dist = round(abs(ball_dist/max_dist),2)
            # random offset for imperfect enemy
            # self.offset  = random.Random.randint
        
            
            return True , rel_dist
        return False,0


    def _move_paddle(self):
            y = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                y -= BLOCK_SIZE
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                y += BLOCK_SIZE
            self.paddle.y = max(1, min(self.paddle.y+ y, self.h - self.paddle_height - 1 ))

    def _move_enemy_paddle(self):
        # currently unbeatable
        self.enemy_paddle.y += round(self.ball[1]- (self.enemy_paddle.y + self.enemy_paddle.h //2))
        self.enemy_paddle.y = max(1, min(self.enemy_paddle.y, self.h - self.paddle_height - 1 ))

    def _move_ball(self):
        # max ball speed is ~ 30, then it clips
        self._hit_vertical_walls()
        extra_angle = 1

        hit_paddle,angle = self._hit_paddle()
        if hit_paddle:
            extra_angle += angle
            self.ball_speed = -self.ball_speed
            if self.ball_speed > 0 and self.ball_speed<29:
                self.ball_speed += 1
            elif self.ball_speed < 0 and self.ball_speed<-29:
                self.ball_speed -= 1

        if self._hit_horizontal_walls():
            self.ball_angle = -self.ball_angle


        calc_angle = round(self.ball_angle * extra_angle)
        self.ball = (max(self.ball_size, min(self.ball[0]+ self.ball_speed, self.w - self.ball_size)),
                      max(self.ball_size, min(self.ball[1]+ calc_angle, self.h - self.ball_size )))


    def _draw_paddle(self):
        pygame.draw.rect(self.display, WHITE, self.paddle)
        pygame.draw.rect(self.display, GREY, self.enemy_paddle)

    def _draw_ball(self):
        pygame.draw.circle(self.display, RED, (self.ball[0], self.ball[1]), self.ball_size)
        
    def _update_ui(self):
        self.display.fill(BLACK)
        # for i in range(self.h //100):
        #     pygame.draw.rect(self.display, WHITE, (0, (i+1)*100, self.w, 1))
        self._draw_paddle()
        self._draw_ball()
        pygame.display.flip()

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        self._move_paddle()
        self._move_enemy_paddle()
        self._move_ball()

        self._update_ui()
        self.clock.tick(self.speed)

        self.recorder.capture()
        return self.game_over, self.score


if __name__ == "__main__":
    game = PingPong()

    while True:
        game_over, score = game.play_step()
        if game_over == True: 
            break

    print("Final Score", score)

    pygame.quit()

