import pygame
import random
import os
import json
from ui.theme import *

WIDTH, HEIGHT = 900, 600

BIRD = ACCENT2
PIPE = BORDER
PIPE_DARK = BORDER_DIM

DATA_FOLDER = "data"
SCORE_FILE = os.path.join(DATA_FOLDER, "flappy_score.json")

MAIN_PANEL = pygame.Rect(25, 25, 850, 540)
GAME_BOX = pygame.Rect(55, 115, 790, 380)


class FlappyBird:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 48)
        self.text_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 26)
        self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 20)
        self.tiny_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 16)

        os.makedirs(DATA_FOLDER, exist_ok=True)
        self.high_score = self.load_high_score()

        self.reset()

    def load_high_score(self):
        if not os.path.exists(SCORE_FILE):
            return 0

        try:
            with open(SCORE_FILE, "r") as file:
                data = json.load(file)
                return data.get("high_score", 0)
        except:
            return 0

    def save_high_score(self):
        with open(SCORE_FILE, "w") as file:
            json.dump({"high_score": self.high_score}, file, indent=4)

    def reset(self):
        self.bird_x = GAME_BOX.x + 150
        self.bird_y = GAME_BOX.centery
        self.velocity = 0
        self.gravity = 0.45
        self.jump_strength = -8

        self.pipes = []
        self.pipe_timer = 0
        self.score = 0
        self.game_over = False

        self.spawn_pipe()

    def spawn_pipe(self):
        gap = 145

        min_top = GAME_BOX.y + 60
        max_top = GAME_BOX.bottom - gap - 70

        top_height = random.randint(min_top, max_top)

        pipe = {
            "x": GAME_BOX.right,
            "top_height": top_height,
            "bottom_y": top_height + gap,
            "passed": False
        }

        self.pipes.append(pipe)

    def draw_text(self, text, x, y, font, color=TEXT):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def draw_pixel_heart(self, x, y, s=4):
        heart = [
            "0110110",
            "1111111",
            "1111111",
            "0111110",
            "0011100",
            "0001000",
        ]

        for row, line in enumerate(heart):
            for col, ch in enumerate(line):
                if ch == "1":
                    pygame.draw.rect(self.screen, ACCENT, (x + col * s, y + row * s, s, s))

    def jump(self):
        if not self.game_over:
            self.velocity = self.jump_strength

    def update(self):
        if self.game_over:
            return

        self.velocity += self.gravity
        self.bird_y += self.velocity

        self.pipe_timer += 1

        if self.pipe_timer > 95:
            self.spawn_pipe()
            self.pipe_timer = 0

        for pipe in self.pipes:
            pipe["x"] -= 4

            if not pipe["passed"] and pipe["x"] + 70 < self.bird_x:
                pipe["passed"] = True
                self.score += 1

        self.pipes = [pipe for pipe in self.pipes if pipe["x"] > GAME_BOX.x - 100]

        self.check_collision()

    def check_collision(self):
        bird_rect = pygame.Rect(self.bird_x - 16, int(self.bird_y) - 16, 32, 32)

        if self.bird_y < GAME_BOX.y + 18 or self.bird_y > GAME_BOX.bottom - 18:
            self.end_game()
            return

        for pipe in self.pipes:
            top_rect = pygame.Rect(
                pipe["x"],
                GAME_BOX.y,
                70,
                pipe["top_height"] - GAME_BOX.y
            )

            bottom_rect = pygame.Rect(
                pipe["x"],
                pipe["bottom_y"],
                70,
                GAME_BOX.bottom - pipe["bottom_y"]
            )

            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                self.end_game()
                return

    def end_game(self):
        self.game_over = True

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def draw_bird(self):
        bird_rect = pygame.Rect(self.bird_x - 16, int(self.bird_y) - 16, 32, 32)

        pygame.draw.rect(self.screen, BIRD, bird_rect, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT, bird_rect, 3, border_radius=8)

        pygame.draw.circle(self.screen, BG, (self.bird_x + 7, int(self.bird_y) - 6), 3)

    def draw_pipes(self):
        for pipe in self.pipes:
            top_rect = pygame.Rect(
                pipe["x"],
                GAME_BOX.y,
                70,
                pipe["top_height"] - GAME_BOX.y
            )

            bottom_rect = pygame.Rect(
                pipe["x"],
                pipe["bottom_y"],
                70,
                GAME_BOX.bottom - pipe["bottom_y"]
            )

            pygame.draw.rect(self.screen, PIPE, top_rect, border_radius=6)
            pygame.draw.rect(self.screen, PIPE_DARK, top_rect, 3, border_radius=6)

            pygame.draw.rect(self.screen, PIPE, bottom_rect, border_radius=6)
            pygame.draw.rect(self.screen, PIPE_DARK, bottom_rect, 3, border_radius=6)

    def draw_sparkles(self):
        sparkles = [
            (120, 165, 4),
            (225, 305, 3),
            (710, 175, 3),
            (785, 400, 4),
            (430, 230, 3),
        ]

        for x, y, size in sparkles:
            pygame.draw.line(self.screen, STAR, (x - size, y), (x + size, y), 1)
            pygame.draw.line(self.screen, STAR, (x, y - size), (x, y + size), 1)

    def draw(self):
        self.screen.fill(BG)

        draw_panel(self.screen, MAIN_PANEL, PANEL, BORDER, 2, 12)

        self.draw_text("flappy bird", 55, 52, self.title_font, ACCENT)
        self.draw_pixel_heart(820, 60, s=4)

        self.draw_text(f"score: {self.score}", 335, 68, self.text_font, TEXT_DIM)
        self.draw_text(f"high score: {self.high_score}", 500, 68, self.text_font, TEXT_DIM)

        draw_panel(self.screen, GAME_BOX, CARD, BORDER, 2, 10)

        self.draw_sparkles()
        self.draw_pipes()
        self.draw_bird()

        self.draw_text("space = flap • r = restart • esc = back", 55, 525, self.small_font, TEXT_DIM)

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))

            popup = pygame.Rect(275, 220, 350, 150)
            draw_panel(self.screen, popup, PANEL, BORDER, 2, 10)

            self.draw_text("game over", popup.x + 85, popup.y + 35, self.title_font, ACCENT)
            self.draw_text("press r to restart", popup.x + 80, popup.y + 95, self.text_font, TEXT_DIM)

    def run(self):
        running = True

        while running:
            self.clock.tick(60)

            self.update()
            self.draw()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if event.key == pygame.K_SPACE:
                        self.jump()

                    if event.key == pygame.K_r:
                        self.reset()


def open_flappy(screen):
    FlappyBird(screen).run()