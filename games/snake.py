import pygame
import random
import os
import json
from ui.theme import *

WIDTH, HEIGHT = 900, 600
CELL = 22

DATA_FOLDER = "data"
SCORE_FILE = os.path.join(DATA_FOLDER, "snake_score.json")

MAIN_PANEL = pygame.Rect(25, 25, 850, 540)
GAME_BOX = pygame.Rect(55, 115, 790, 380)

SNAKE_COLOR = ACCENT2
FOOD_COLOR = ACCENT
GRID_COLOR = BORDER_DIM


class SnakeGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 48)
        self.text_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 26)
        self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 20)

        os.makedirs(DATA_FOLDER, exist_ok=True)
        self.high_score = self.load_high_score()
        self.reset_game()

    def load_high_score(self):
        if not os.path.exists(SCORE_FILE):
            return 0
        try:
            with open(SCORE_FILE, "r") as file:
                return json.load(file).get("high_score", 0)
        except:
            return 0

    def save_high_score(self):
        with open(SCORE_FILE, "w") as file:
            json.dump({"high_score": self.high_score}, file, indent=4)

    def reset_game(self):
        self.cols = GAME_BOX.w // CELL
        self.rows = GAME_BOX.h // CELL
        self.snake = [(7, 7), (6, 7), (5, 7)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        while True:
            food = (
                random.randint(1, self.cols - 2),
                random.randint(1, self.rows - 2)
            )
            if food not in self.snake:
                return food

    def draw_text(self, text, x, y, font, color=TEXT):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def draw_pixel_heart(self, x, y, s=4):
        heart = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
        for r, line in enumerate(heart):
            for c, ch in enumerate(line):
                if ch == "1":
                    pygame.draw.rect(self.screen, ACCENT, (x + c * s, y + r * s, s, s))

    def draw_grid(self):
        for x in range(GAME_BOX.x, GAME_BOX.right, CELL):
            pygame.draw.line(self.screen, GRID_COLOR, (x, GAME_BOX.y), (x, GAME_BOX.bottom), 1)
        for y in range(GAME_BOX.y, GAME_BOX.bottom, CELL):
            pygame.draw.line(self.screen, GRID_COLOR, (GAME_BOX.x, y), (GAME_BOX.right, y), 1)

    def board_to_screen(self, pos):
        x, y = pos
        return GAME_BOX.x + x * CELL, GAME_BOX.y + y * CELL

    def draw_snake(self):
        for i, part in enumerate(self.snake):
            x, y = self.board_to_screen(part)
            rect = pygame.Rect(x, y, CELL, CELL)
            pygame.draw.rect(self.screen, SNAKE_COLOR, rect, border_radius=6)
            if i == 0:
                pygame.draw.rect(self.screen, BORDER, rect, 2, border_radius=6)

    def draw_food(self):
        x, y = self.board_to_screen(self.food)
        rect = pygame.Rect(x + 3, y + 3, CELL - 6, CELL - 6)
        pygame.draw.rect(self.screen, FOOD_COLOR, rect, border_radius=8)

    def move_snake(self):
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        hit_wall = (
            new_head[0] < 0 or new_head[0] >= self.cols or
            new_head[1] < 0 or new_head[1] >= self.rows
        )

        if hit_wall or new_head in self.snake:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BG)
        draw_panel(self.screen, MAIN_PANEL, PANEL, BORDER, 2, 12)
        self.draw_text("snake", 55, 52, self.title_font, ACCENT)
        self.draw_pixel_heart(820, 60, s=4)
        self.draw_text(f"score: {self.score}", 335, 68, self.text_font, TEXT_DIM)
        self.draw_text(f"high score: {self.high_score}", 500, 68, self.text_font, TEXT_DIM)
        draw_panel(self.screen, GAME_BOX, CARD, BORDER, 2, 10)
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_text("arrow keys move • r restart • esc back", 55, 525, self.small_font, TEXT_DIM)
        if self.game_over:
            popup = pygame.Rect(275, 220, 350, 150)
            draw_panel(self.screen, popup, PANEL, BORDER, 2, 10)
            self.draw_text("game over", popup.x + 85, popup.y + 35, self.title_font, ACCENT)
            self.draw_text("press r to restart", popup.x + 80, popup.y + 95, self.text_font, TEXT_DIM)
    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            return False
        if key == pygame.K_r:
            self.reset_game()
        if not self.game_over:
            if key == pygame.K_UP and self.direction != (0, 1):
                self.next_direction = (0, -1)
            if key == pygame.K_DOWN and self.direction != (0, -1):
                self.next_direction = (0, 1)
            if key == pygame.K_LEFT and self.direction != (1, 0):
                self.next_direction = (-1, 0)
            if key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.next_direction = (1, 0)
        return True

    def run(self):
        running = True
        move_timer = 0
        move_delay = 120
        while running:
            dt = self.clock.tick(60)
            move_timer += dt
            if move_timer >= move_delay:
                self.move_snake()
                move_timer = 0
            self.draw()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    running = self.handle_key(event.key)

def open_snake(screen):
    SnakeGame(screen).run()