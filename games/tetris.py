import pygame
import random
from ui.theme import *

WIDTH, HEIGHT = 900, 600

CELL = 22
COLS, ROWS = 10, 20

MAIN_PANEL = pygame.Rect(25, 25, 850, 540)
BOARD_X, BOARD_Y = 395, 105

COLORS = [
    ACCENT,
    ACCENT2,
    BAR_FILL,
    BORDER,
    TEXT_DIM,
    STAR,
    (160, 180, 210),
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
]


class Tetris:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 48)
        self.text_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 24)
        self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 20)

        self.reset()

    def reset(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.spawn_piece()

    def spawn_piece(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

        if self.collides(self.shape, self.x, self.y):
            self.game_over = True

    def rotate(self, shape):
        return [list(row) for row in zip(*shape[::-1])]

    def collides(self, shape, x, y):
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell:
                    bx, by = x + c, y + r
                    if bx < 0 or bx >= COLS or by >= ROWS:
                        return True
                    if by >= 0 and self.board[by][bx]:
                        return True
        return False

    def lock_piece(self):
        for r, row in enumerate(self.shape):
            for c, cell in enumerate(row):
                if cell:
                    self.board[self.y + r][self.x + c] = self.color

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        cleared = ROWS - len(new_board)

        for _ in range(cleared):
            new_board.insert(0, [None for _ in range(COLS)])

        self.board = new_board
        self.lines += cleared
        self.score += cleared * 100

    def move(self, dx, dy):
        if not self.collides(self.shape, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.lock_piece()

    def draw_text(self, text, x, y, font, color=TEXT):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def draw_pixel_heart(self, x, y, s=4):
        heart = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
        for r, line in enumerate(heart):
            for c, ch in enumerate(line):
                if ch == "1":
                    pygame.draw.rect(self.screen, ACCENT, (x + c * s, y + r * s, s, s))

    def draw_board(self):
        board_panel = pygame.Rect(
            BOARD_X - 15,
            BOARD_Y - 15,
            COLS * CELL + 30,
            ROWS * CELL + 30
        )
        draw_panel(self.screen, board_panel, CARD, BORDER, 2, 10)

        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(BOARD_X + c * CELL, BOARD_Y + r * CELL, CELL, CELL)
                pygame.draw.rect(self.screen, BORDER_DIM, rect, 1)

                if self.board[r][c]:
                    pygame.draw.rect(self.screen, self.board[r][c], rect, border_radius=4)

        for r, row in enumerate(self.shape):
            for c, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        BOARD_X + (self.x + c) * CELL,
                        BOARD_Y + (self.y + r) * CELL,
                        CELL,
                        CELL
                    )
                    pygame.draw.rect(self.screen, self.color, rect, border_radius=4)
                    pygame.draw.rect(self.screen, BORDER_DIM, rect, 1, border_radius=4)

    def draw_info_panel(self):
        info = pygame.Rect(65, 130, 250, 260)
        draw_panel(self.screen, info, CARD, BORDER_DIM, 1, 10)

        self.draw_text(f"score: {self.score}", info.x + 25, info.y + 30, self.text_font, TEXT)
        self.draw_text(f"lines: {self.lines}", info.x + 25, info.y + 70, self.text_font, TEXT_DIM)

        self.draw_text("controls", info.x + 25, info.y + 130, self.text_font, ACCENT)
        self.draw_text("left/right move", info.x + 25, info.y + 165, self.small_font, TEXT_DIM)
        self.draw_text("up rotate", info.x + 25, info.y + 190, self.small_font, TEXT_DIM)
        self.draw_text("space drop", info.x + 25, info.y + 215, self.small_font, TEXT_DIM)

    def draw(self):
        self.screen.fill(BG)
        draw_panel(self.screen, MAIN_PANEL, PANEL, BORDER, 2, 12)

        self.draw_text("tetris", 55, 52, self.title_font, ACCENT)
        self.draw_pixel_heart(820, 60, s=4)

        self.draw_info_panel()
        self.draw_board()

        self.draw_text("r restart • esc back", 55, 525, self.small_font, TEXT_DIM)

        if self.game_over:
            popup = pygame.Rect(275, 220, 350, 150)
            draw_panel(self.screen, popup, PANEL, BORDER, 2, 10)
            self.draw_text("game over", popup.x + 85, popup.y + 35, self.title_font, ACCENT)
            self.draw_text("press r to restart", popup.x + 80, popup.y + 95, self.text_font, TEXT_DIM)

    def run(self):
        running = True
        fall_timer = 0
        fall_delay = 500

        while running:
            dt = self.clock.tick(60)
            fall_timer += dt

            if fall_timer >= fall_delay and not self.game_over:
                if not self.move(0, 1):
                    self.lock_piece()
                fall_timer = 0

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

                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                        elif event.key == pygame.K_UP:
                            rotated = self.rotate(self.shape)
                            if not self.collides(rotated, self.x, self.y):
                                self.shape = rotated
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()


def open_tetris(screen):
    Tetris(screen).run()