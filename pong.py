import pygame
import random
import sys

pygame.init()

BLOCK_SIZE = 20
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GAME_SPEED = 30
BALL_SPEED = 10
BALL_ANGLE = 3
MAX_ANGLE = BALL_ANGLE * 2

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
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Ping Pong")

        self.ball = (self.w // 2, self.h // 2)
        self.ball_size = int(BLOCK_SIZE // 1.5)
        self.ball_speed = random.choice([-BALL_SPEED, BALL_SPEED])
        self.ball_angle = random.choice([-BALL_ANGLE, BALL_ANGLE])

        self.paddle_height = self.h // 3
        self.paddle = pygame.Rect(
            BLOCK_SIZE * 3, self.paddle_height, self.ball_size, self.paddle_height
        )
        self.enemy_paddle = pygame.Rect(
            self.w - BLOCK_SIZE * 3,
            self.paddle_height,
            self.ball_size,
            self.paddle_height,
        )
        self.paddle_offset = 0

        self.game_over = False

    def _hit_upperlower_walls(self):
        # hits upper or lower wall
        if (self.ball[1] >= self.h - self.ball_size and self.ball_angle > 0) or (
            self.ball[1] <= 0 + self.ball_size and self.ball_angle < 0
        ):
            self.ball_angle = -self.ball_angle

    def _hit_leftright_walls(self):
        # hits left or right wall
        if (
            self.ball[0] >= self.w - self.ball_size
            or self.ball[0] <= 0 + self.ball_size
        ):
            self.game_over = True

    def _hit_paddle(self):
        paddle_center_height = self.paddle_height / 2
        my_paddle_center = self.paddle.y + paddle_center_height
        enemy_paddle_center = self.enemy_paddle.y + paddle_center_height

        # my paddle
        if (
            self.ball[0] <= self.paddle.x + self.ball_size * 2
            and self.ball[0] >= self.paddle.x - self.ball_size
            and self.ball[1] >= self.paddle.y - self.ball_size
            and self.ball[1] <= self.paddle.y + self.paddle_height + self.ball_size
            and self.ball_speed < 0
        ):
            offset = (self.ball[1] - my_paddle_center) / paddle_center_height
            offset = max(-1, min(offset, 1))
            return True, offset

        # enemy paddle
        if (
            self.ball[0] <= self.enemy_paddle.x + self.ball_size * 2
            and self.ball[0] >= self.enemy_paddle.x - self.ball_size
            and self.ball[1] >= self.enemy_paddle.y - self.ball_size
            and self.ball[1]
            <= self.enemy_paddle.y + self.paddle_height + self.ball_size
            and self.ball_speed > 0
        ):
            offset = (self.ball[1] - enemy_paddle_center) / paddle_center_height
            offset = max(-1, min(offset, 1))
            self.paddle_offset = random.randint(-BLOCK_SIZE, BLOCK_SIZE)
            return True, offset
        return False, 0

    def _move_paddle(self):
        y = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            y -= BLOCK_SIZE
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            y += BLOCK_SIZE
        self.paddle.y = max(0, min(self.paddle.y + y, self.h - self.paddle_height))

    def _move_enemy_paddle(self):
        enemy_speed = BLOCK_SIZE // 3
        if self.ball_speed > 0:
            movement = round(
                self.ball[1] - ((self.enemy_paddle.y + self.enemy_paddle.h // 2))
            )
            movement += self.paddle_offset
            movement = (
                max(movement, -enemy_speed)
                if movement < 0
                else min(movement, enemy_speed)
            )
            self.enemy_paddle.y = max(
                0, min(self.enemy_paddle.y + movement, self.h - self.paddle_height)
            )
        else:
            movement = self.h // 3 - self.enemy_paddle.y
            movement = (
                max(movement, -enemy_speed)
                if movement < 0
                else min(movement, enemy_speed)
            )
            self.enemy_paddle.y = self.enemy_paddle.y + movement

    def _move_ball(self):
        steps = max(1, abs(self.ball_speed) // 4)
        for _ in range(steps):
            self._hit_upperlower_walls()
            self._hit_leftright_walls()

            paddle_hit, offset = self._hit_paddle()
            if paddle_hit:
                self.ball_speed = (
                    min(-(self.ball_speed - 1), 60)
                    if self.ball_speed < 0
                    else max(-(self.ball_speed + 1), -60)
                )
                self.ball_angle = offset * MAX_ANGLE

            self.ball = (
                max(
                    self.ball_size,
                    min(
                        self.ball[0] + self.ball_speed / steps, self.w - self.ball_size
                    ),
                ),
                max(
                    self.ball_size,
                    min(
                        self.ball[1] + self.ball_angle / steps, self.h - self.ball_size
                    ),
                ),
            )

    def _draw_paddle(self):
        pygame.draw.rect(self.display, WHITE, self.paddle)
        pygame.draw.rect(self.display, GREY, self.enemy_paddle)

    def _draw_ball(self):
        pygame.draw.circle(
            self.display,
            RED,
            (round(self.ball[0]), round(self.ball[1])),
            self.ball_size,
        )

    def _update_ui(self):
        self.display.fill(BLACK)
        self._draw_paddle()
        self._draw_ball()
        pygame.display.flip()

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self._move_paddle()
        self._move_enemy_paddle()
        self._move_ball()
        self._update_ui()
        self.clock.tick(self.speed)

        return self.game_over


if __name__ == "__main__":
    game = PingPong()

    while True:
        game_over = game.play_step()
        if game_over == True:
            pygame.time.wait(100)
            break

    pygame.quit()
