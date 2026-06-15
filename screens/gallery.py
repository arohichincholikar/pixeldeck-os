import pygame
import os
from ui.theme import *

WIDTH, HEIGHT = 900, 600
SPRITES_FOLDER = "sprites"


class Gallery:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 58)
        self.text_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 26)
        self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 20)

        os.makedirs(SPRITES_FOLDER, exist_ok=True)

        self.files = [
            file for file in os.listdir(SPRITES_FOLDER)
            if file.lower().endswith(".png")
        ]

        self.mode = "list"
        self.selected_image = None
        self.selected_name = ""

    def draw_text(self, text, x, y, font, color=TEXT):
        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))

    def draw_list(self):
        self.screen.fill(BG)

        self.draw_text("gallery", 60, 40, self.title_font, ACCENT)
        self.draw_text("saved pixel sprites", 60, 95, self.small_font)

        if not self.files:
            self.draw_text("no sprites found yet.", 60, 170, self.text_font)
            self.draw_text("draw something in pixel art studio and press s to save.", 60, 210, self.small_font)
            self.draw_text("esc = back to home", 60, 530, self.small_font)
            return

        start_x = 70
        start_y = 140
        card_w = 150
        card_h = 150
        gap = 25

        for i, file in enumerate(self.files):
            row = i // 4
            col = i % 4

            x = start_x + col * (card_w + gap)
            y = start_y + row * (card_h + gap)

            rect = pygame.Rect(x, y, card_w, card_h)
            mouse_pos = pygame.mouse.get_pos()

            color = HOVER_CARD if rect.collidepoint(mouse_pos) else CARD
            pygame.draw.rect(self.screen, color, rect, border_radius=14)
            pygame.draw.rect(self.screen, ACCENT, rect, 2, border_radius=14)

            path = os.path.join(SPRITES_FOLDER, file)

            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (90, 90))
                self.screen.blit(img, (x + 30, y + 18))
            except:
                self.draw_text("Error", x + 45, y + 50, self.small_font)

            name = file[:16]
            self.draw_text(name, x + 14, y + 118, self.small_font)

        self.draw_text("click a sprite to preview • esc = back to home", 60, 540, self.small_font)

    def open_image(self, filename):
        path = os.path.join(SPRITES_FOLDER, filename)

        try:
            image = pygame.image.load(path).convert_alpha()
            self.selected_image = image
            self.selected_name = filename
            self.mode = "preview"
        except:
            pass

    def draw_preview(self):
        self.screen.fill(BG)

        self.draw_text(self.selected_name, 60, 40, self.text_font, ACCENT)

        if self.selected_image:
            preview = pygame.transform.scale(self.selected_image, (320, 320))
            rect = preview.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(preview, rect)

            border = pygame.Rect(rect.x, rect.y, 320, 320)
            pygame.draw.rect(self.screen, ACCENT, border, 3)

        self.draw_text("esc = back to gallery", 60, 540, self.small_font)

    def handle_list_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            start_x = 70
            start_y = 140
            card_w = 150
            card_h = 150
            gap = 25

            for i, file in enumerate(self.files):
                row = i // 4
                col = i % 4

                x = start_x + col * (card_w + gap)
                y = start_y + row * (card_h + gap)

                rect = pygame.Rect(x, y, card_w, card_h)

                if rect.collidepoint(event.pos):
                    self.open_image(file)

        return True

    def handle_preview_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.mode = "list"

    def run(self):
        running = True

        while running:
            if self.mode == "list":
                self.draw_list()
            else:
                self.draw_preview()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if self.mode == "list":
                    running = self.handle_list_event(event)
                else:
                    self.handle_preview_event(event)

            self.clock.tick(60)


def open_gallery(screen):
    gallery = Gallery(screen)
    gallery.run()