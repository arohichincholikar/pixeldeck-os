import pygame
import sys
from screens.pixelart import open_pixelart
from screens.library import open_library
from screens.games_menu import open_games_menu
from screens.gallery import open_gallery
from screens.music_player import open_music_player
from ui.theme import *
from ui.icons import draw_book, draw_art, draw_gallery, draw_game, draw_music
pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PixelDeck")
clock = pygame.time.Clock()


title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 100)
button_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 30)
small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 20)

class Button:
    def __init__(self, text, x, y, w, h, icon=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.icon = icon

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        color = HOVER_CARD if self.rect.collidepoint(mouse_pos) else CARD

        pygame.draw.rect(screen, color, self.rect, border_radius=14)
        pygame.draw.rect(screen, BORDER, self.rect, 2, border_radius=14)

        if self.icon:
            self.icon(screen, self.rect.x + 22, self.rect.y + 16, 3)

        text_surface = button_font.render(self.text, True, TEXT)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 70, self.rect.centery))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


library_btn = Button("library", 300, 190, 300, 55, draw_book)
pixelart_btn = Button("pixel art studio", 300, 255, 300, 55, draw_art)
games_btn = Button("games", 300, 385, 300, 55, draw_game)
music_btn = Button("music", 300, 450, 300, 55, draw_music)
gallery_btn = Button("gallery", 300, 320, 300, 55, draw_gallery)
buttons = [library_btn, pixelart_btn, games_btn, music_btn, gallery_btn]


def draw_home():
    screen.fill(BG)

    draw_panel(screen, pygame.Rect(1100, 55, 680, 500), PANEL, 2)

    title = title_font.render("PIXELDECK", True, ACCENT)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    screen.blit(title, title_rect)

    subtitle = small_font.render(
        "reading • art • games • music",
        True,
        TEXT_DIM
    )
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 150))
    screen.blit(subtitle, subtitle_rect)

    for button in buttons:
        button.draw()

    footer = small_font.render("PIXELDECK OS • v1.0", True, TEXT_DIM)
    screen.blit(footer, (28, HEIGHT - 32))

    battery = small_font.render("BAT 100%", True, TEXT_DIM)
    screen.blit(battery, (WIDTH - 120, HEIGHT - 32))

def placeholder_screen(name):
    running = True
    while running:
        screen.fill(BG)
        title = title_font.render(name, True, ACCENT)
        title_rect = title.get_rect(center=(WIDTH // 2, 220))
        screen.blit(title, title_rect)
        msg = small_font.render("coming soon! press esc to go back.", True, TEXT)
        msg_rect = msg.get_rect(center=(WIDTH // 2, 300))
        screen.blit(msg, msg_rect)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        clock.tick(60)

def main():
    while True:
        draw_home()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if library_btn.is_clicked(event):
                open_library(screen)
            if pixelart_btn.is_clicked(event):
                open_pixelart(screen)
            if games_btn.is_clicked(event):
                open_games_menu(screen)
            if music_btn.is_clicked(event):
                open_music_player(screen)
            if gallery_btn.is_clicked(event):
                open_gallery(screen)
        clock.tick(60)

if __name__ == "__main__":
    main()