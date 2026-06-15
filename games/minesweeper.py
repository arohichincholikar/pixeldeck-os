import pygame
import random
from ui.theme import *

WIDTH, HEIGHT = 900, 600

CELL = 28
ROWS, COLS = 12, 16
MINES = 28

MAIN_PANEL = pygame.Rect(25, 25, 850, 540)
GAME_BOX = pygame.Rect(210, 120, COLS * CELL, ROWS * CELL)

class Minesweeper:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 48)
        self.text_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 24)
        self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 20)
        self.reset()

    def reset(self):
        self.revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.flags = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.mines = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.game_over = False
        self.won = False
        placed = 0
        while placed < MINES:
            r = random.randint(0, ROWS - 1)
            c = random.randint(0, COLS - 1)
            if not self.mines[r][c]:
                self.mines[r][c] = True
                placed += 1

    def draw_text(self, text, x, y, font, color=TEXT):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def draw_pixel_heart(self, x, y, s=4):
        heart = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
        for r, line in enumerate(heart):
            for c, ch in enumerate(line):
                if ch == "1":
                    pygame.draw.rect(self.screen, ACCENT, (x + c * s, y + r * s, s, s))

    def count_mines(self, r, c):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.mines[nr][nc]:
                    count += 1
        return count

    def reveal(self, r, c):
        if self.flags[r][c] or self.revealed[r][c] or self.game_over:
            return
        self.revealed[r][c] = True
        if self.mines[r][c]:
            self.game_over = True
            self.reveal_all_mines()
            return
        if self.count_mines(r, c) == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and not self.revealed[nr][nc]:
                        self.reveal(nr, nc)
        self.check_win()

    def reveal_all_mines(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.mines[r][c]:
                    self.revealed[r][c] = True

    def check_win(self):
        for r in range(ROWS):
            for c in range(COLS):
                if not self.mines[r][c] and not self.revealed[r][c]:
                    return
        self.won = True
        self.game_over = True

    def draw_board(self):
        draw_panel(
            self.screen,
            pygame.Rect(GAME_BOX.x - 15, GAME_BOX.y - 15, GAME_BOX.w + 30, GAME_BOX.h + 30),
            CARD,
            BORDER,
            2,
            10
        )
        for r in range(ROWS):
            for c in range(COLS):
                x = GAME_BOX.x + c * CELL
                y = GAME_BOX.y + r * CELL
                rect = pygame.Rect(x, y, CELL, CELL)

                if self.revealed[r][c]:
                    pygame.draw.rect(self.screen, PANEL, rect)
                    if self.mines[r][c]:
                        pygame.draw.circle(self.screen, ACCENT2, rect.center, 8)
                    else:
                        count = self.count_mines(r, c)
                        if count > 0:
                            self.draw_text(count, x + 9, y + 5, self.text_font, ACCENT)
                else:
                    pygame.draw.rect(self.screen, CARD, rect)
                    if self.flags[r][c]:
                        self.draw_text("F", x + 9, y + 5, self.text_font, ACCENT2)
                pygame.draw.rect(self.screen, BORDER, rect, 1)

    def draw(self):
        self.screen.fill(BG)
        draw_panel(self.screen, MAIN_PANEL, PANEL, BORDER, 2, 12)
        self.draw_text("minesweeper", 55, 52, self.title_font, ACCENT)
        self.draw_pixel_heart(820, 60, s=4)
        remaining = MINES - sum(sum(row) for row in self.flags)
        self.draw_text(f"mines: {remaining}", 520, 68, self.text_font, TEXT_DIM)
        self.draw_board()
        self.draw_text("left click reveal • right click flag • r restart • esc back", 55, 525, self.small_font, TEXT_DIM)
        if self.game_over:
            side_box = pygame.Rect(690, 190, 145, 150)
            draw_panel(self.screen, side_box, PANEL, BORDER, 2, 10)
            msg = "you win" if self.won else "boom!"
            self.draw_text(msg, side_box.x + 25, side_box.y + 35, self.text_font, ACCENT)
            self.draw_text("press r", side_box.x + 25, side_box.y + 80, self.small_font, TEXT_DIM)
            self.draw_text("restart", side_box.x + 25, side_box.y + 105, self.small_font, TEXT_DIM)

    def handle_click(self, pos, button):
        x, y = pos
        if not (
            GAME_BOX.x <= x < GAME_BOX.right and
            GAME_BOX.y <= y < GAME_BOX.bottom
        ):
            return
        c = (x - GAME_BOX.x) // CELL
        r = (y - GAME_BOX.y) // CELL
        if button == 1:
            self.reveal(r, c)
        if button == 3 and not self.revealed[r][c]:
            self.flags[r][c] = not self.flags[r][c]

    def run(self):
        running = True
        while running:
            self.draw()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r:
                        self.reset()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)
            self.clock.tick(60)

def open_minesweeper(screen):
    Minesweeper(screen).run()