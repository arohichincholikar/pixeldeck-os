import pygame
import os
from datetime import datetime

from ui.theme import *

WIDTH, HEIGHT = 900, 600

PALETTE = [
    ("red",         "#E07A7A"),
    ("pink",        "#F0B6C8"),
    ("orange",      "#F3A56B"),
    ("yellow",      "#F2D27A"),
    ("light green", "#D8E3A5"),
    ("dark green",  "#667A47"),
    ("light blue",  "#AFC9E8"),
    ("dark blue",   "#536A91"),
    ("purple",      "#9E8BC7"),
    ("magenta",     "#D184B7"),
    ("brown",       "#8A6A52"),
    ("black",       "#1A1A24"),
    ("white",       "#F7F4EE"),
    ("cream",       "#E9DFC9"),
    ("grey",        "#8D8A95"),
    ("Miffy Blue",  "#2D69A8")
]

GRID_SIZE = 32
CELL_SIZE = 12

CANVAS_X = 70
CANVAS_Y = 135

WHITE = (247, 244, 238)
GRID_LINE = BORDER_DIM


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


class PixelArtStudio:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 48)
        self.text_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 24)
        self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 18)
        self.tiny_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 16)
        self.current_color = hex_to_rgb(PALETTE[0][1])
        self.grid = [[WHITE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.palette_rects = []
        self.message = "left click draw • right click erase • s save • c clear • esc back"

    def draw_text(self, text, x, y, font, color=TEXT):
        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))

    def draw_canvas(self):
        canvas_panel = pygame.Rect(45, 95, 435, 445)
        draw_panel(self.screen, canvas_panel, PANEL, BORDER, 2, 12)
        self.draw_text("canvas 32x32", canvas_panel.x + 20, canvas_panel.y + 15, self.text_font, ACCENT)
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color = self.grid[row][col]
                rect = pygame.Rect(
                    CANVAS_X + col * CELL_SIZE,
                    CANVAS_Y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 1)
        border = pygame.Rect(
            CANVAS_X,
            CANVAS_Y,
            GRID_SIZE * CELL_SIZE,
            GRID_SIZE * CELL_SIZE
        )
        pygame.draw.rect(self.screen, BORDER, border, 2)

    def draw_palette(self):
        self.palette_rects = []
        palette_panel = pygame.Rect(515, 95, 335, 330)
        draw_panel(self.screen, palette_panel, PANEL, BORDER, 2, 12)
        self.draw_text("palette", palette_panel.x + 20, palette_panel.y + 18, self.text_font, ACCENT)
        start_x = palette_panel.x + 28
        start_y = palette_panel.y + 65
        box_size = 42
        gap = 18
        for index, (name, hex_code) in enumerate(PALETTE):
            row = index // 4
            col = index % 4
            x = start_x + col * (box_size + gap)
            y = start_y + row * (box_size + gap)
            color = hex_to_rgb(hex_code)
            rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            if color == self.current_color:
                pygame.draw.rect(self.screen, ACCENT2, rect, 4, border_radius=6)
            else:
                pygame.draw.rect(self.screen, BORDER_DIM, rect, 2, border_radius=6)
            self.palette_rects.append((rect, color, name))

    def draw_preview(self):
        preview_panel = pygame.Rect(515, 445, 335, 95)
        draw_panel(self.screen, preview_panel, PANEL, BORDER, 2, 12)
        self.draw_text("selected colour", preview_panel.x + 20, preview_panel.y + 16, self.small_font, TEXT_DIM)
        rect = pygame.Rect(preview_panel.x + 220, preview_panel.y + 24, 58, 42)
        pygame.draw.rect(self.screen, self.current_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, BORDER, rect, 2, border_radius=8)
        selected_name = "custom"
        for name, hex_code in PALETTE:
            if hex_to_rgb(hex_code) == self.current_color:
                selected_name = name
                break
        self.draw_text(selected_name, preview_panel.x + 20, preview_panel.y + 48, self.small_font, ACCENT)

    def handle_canvas_click(self, mouse_pos, erase=False):
        x, y = mouse_pos
        if not (
            CANVAS_X <= x < CANVAS_X + GRID_SIZE * CELL_SIZE
            and CANVAS_Y <= y < CANVAS_Y + GRID_SIZE * CELL_SIZE
        ):
            return
        col = (x - CANVAS_X) // CELL_SIZE
        row = (y - CANVAS_Y) // CELL_SIZE
        self.grid[row][col] = WHITE if erase else self.current_color

    def handle_palette_click(self, mouse_pos):
        for rect, color, name in self.palette_rects:
            if rect.collidepoint(mouse_pos):
                self.current_color = color
                self.message = f"selected {name}"
                return

    def clear_canvas(self):
        self.grid = [[WHITE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.message = "canvas cleared"

    def save_sprite(self):
        os.makedirs("sprites", exist_ok=True)
        sprite = pygame.Surface((GRID_SIZE, GRID_SIZE))
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                sprite.set_at((col, row), self.grid[row][col])
        scaled_sprite = pygame.transform.scale(sprite, (256, 256))
        filename = datetime.now().strftime("sprite_%Y%m%d_%H%M%S.png")
        filepath = os.path.join("sprites", filename)
        pygame.image.save(scaled_sprite, filepath)
        self.message = f"saved: {filename}"

    def draw(self):
        self.screen.fill(BG)
        self.draw_text("pixel studio", 45, 35, self.title_font, ACCENT)
        self.draw_text("draw sprites for pixeldeck", 45, 78, self.small_font, TEXT_DIM)
        self.draw_canvas()
        self.draw_palette()
        self.draw_preview()
        self.draw_text(self.message, 45, 555, self.tiny_font, ACCENT)
        #self.draw_text("s save • c clear • right click erase • esc back", 455, 555, self.tiny_font, TEXT_DIM)

    def run(self):
        running = True
        while running:
            self.draw()
            pygame.display.update()
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                self.handle_canvas_click(pygame.mouse.get_pos(), erase=False)
            if mouse_buttons[2]:
                self.handle_canvas_click(pygame.mouse.get_pos(), erase=True)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_c:
                        self.clear_canvas()
                    if event.key == pygame.K_s:
                        self.save_sprite()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_palette_click(event.pos)
                    if event.button == 3:
                        self.handle_canvas_click(event.pos, erase=True)
            self.clock.tick(60)

def open_pixelart(screen):
    studio = PixelArtStudio(screen)
    studio.run()