import pygame
from games.snake import open_snake
from games.tetris import open_tetris
from games.minesweeper import open_minesweeper
from games.flappy import open_flappy
from games.tamagotchi import open_tamagotchi
from ui.theme import *

WIDTH, HEIGHT = 900, 600

class GameButton:
    def __init__(self, text, x, y, w, h, action):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.action = action

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        color = HOVER_CARD if self.rect.collidepoint(mouse_pos) else CARD
        pygame.draw.rect(screen, color, self.rect, border_radius=14)
        pygame.draw.rect(screen, ACCENT, self.rect, 2, border_radius=14)
        text_surface = font.render(self.text, True, TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def placeholder(screen, name):
    clock = pygame.time.Clock()
    title_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 54)
    small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 24)
    running = True
    while running:
        screen.fill(BG)
        title = title_font.render(name, True, ACCENT)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 230)))
        msg = small_font.render("coming soon! press esc to go back.", True, TEXT)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, 310)))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        clock.tick(60)


def open_games_menu(screen):
    clock = pygame.time.Clock()
    title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 72)
    button_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 34)
    small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 22)
    buttons = [
        GameButton("snake", 300, 145, 300, 60, lambda: open_snake(screen)),
        GameButton("tetris", 300, 210, 300, 60, lambda: open_tetris(screen)),
        GameButton("minesweeper", 300, 275, 300, 60, lambda: open_minesweeper(screen)),
        GameButton("flappy bird", 300, 340, 300, 60, lambda: open_flappy(screen)),
        GameButton("tamagotchi", 300, 405, 300, 60, lambda: open_tamagotchi(screen)),
    ]
    running = True
    while running:
        screen.fill(BG)
        title = title_font.render("games", True, ACCENT)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))
        subtitle = small_font.render("retro games + pixel pet collection", True, TEXT)
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 125)))
        for button in buttons:
            button.draw(screen, button_font)
        hint = small_font.render("esc = back to home", True, TEXT)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 530)))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            for button in buttons:
                if button.clicked(event):
                    button.action()
        clock.tick(60)