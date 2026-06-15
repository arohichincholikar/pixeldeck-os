import pygame
import os
import fitz
import textwrap
import json
from ui.theme import *

WIDTH, HEIGHT = 900, 600
BOOKS_FOLDER = "books"
DATA_FOLDER = "data"
PROGRESS_FILE = os.path.join(DATA_FOLDER, "reading_progress.json")
LINES_PER_SCREEN = 15
WRAP_WIDTH = 78


class Library:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 48)
        self.text_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 24)
        self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 18)
        self.tiny_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 16)
        os.makedirs(BOOKS_FOLDER, exist_ok=True)
        os.makedirs(DATA_FOLDER, exist_ok=True)
        self.files = [
            file for file in os.listdir(BOOKS_FOLDER)
            if file.lower().endswith(".pdf")
        ]
        self.selected_index = 0
        self.pdf_doc = None
        self.current_book = None
        self.current_page = 0
        self.text_page = 0
        self.mode = "list"
        self.current_text_lines = []
        self.progress = self.load_progress()

    def load_progress(self):
        if not os.path.exists(PROGRESS_FILE):
            return {}
        try:
            with open(PROGRESS_FILE, "r") as file:
                return json.load(file)
        except:
            return {}

    def save_progress(self):
        with open(PROGRESS_FILE, "w") as file:
            json.dump(self.progress, file, indent=4)

    def save_current_page(self):
        if self.current_book is not None:
            self.progress[self.current_book] = {
                "pdf_page": self.current_page,
                "text_page": self.text_page
            }
            self.save_progress()

    def blit(self, text, x, y, font, color=TEXT):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def clean_book_name(self, filename):
        name = os.path.splitext(filename)[0]
        return name.replace("_", " ").replace("-", " ")

    def get_progress_data(self, filename):
        progress_data = self.progress.get(filename, {"pdf_page": 0, "text_page": 0})
        if isinstance(progress_data, int):
            return progress_data, 0
        return progress_data.get("pdf_page", 0), progress_data.get("text_page", 0)

    def draw_book_icon(self, x, y, s=3):
        pattern = [
            "011110",
            "010010",
            "010010",
            "011110",
            "010010",
            "010010",
            "011110",
        ]
        for row, line in enumerate(pattern):
            for col, ch in enumerate(line):
                if ch == "1":
                    pygame.draw.rect(self.screen, ACCENT, (x + col * s, y + row * s, s, s))

    def draw_list(self):
        self.screen.fill(BG)
        self.blit("library", 45, 38, self.title_font, ACCENT)
        self.blit("text-only pdf reader", 45, 82, self.small_font, TEXT_DIM)
        list_rect = pygame.Rect(35, 120, 830, 390)
        draw_panel(self.screen, list_rect, PANEL, BORDER, 2, 12)
        self.blit("books", list_rect.x + 22, list_rect.y + 18, self.text_font, ACCENT)
        if not self.files:
            self.blit("no pdfs found yet", list_rect.x + 25, list_rect.y + 90, self.text_font, TEXT)
            self.blit("add files to cyberdeck/books/", list_rect.x + 25, list_rect.y + 125, self.small_font, TEXT_DIM)
            self.blit("esc = back to home", 45, 555, self.tiny_font, TEXT_DIM)
            return
        start_y = list_rect.y + 65
        for i, file in enumerate(self.files[:8]):
            row = pygame.Rect(list_rect.x + 20, start_y + i * 38, list_rect.w - 40, 30)
            mouse_pos = pygame.mouse.get_pos()
            selected = i == self.selected_index
            color = HOVER_CARD if row.collidepoint(mouse_pos) or selected else CARD
            pygame.draw.rect(self.screen, color, row, border_radius=6)
            if selected:
                pygame.draw.rect(self.screen, BORDER, row, 1, border_radius=6)
            self.draw_book_icon(row.x + 10, row.y + 6, s=2)
            pdf_page, text_page = self.get_progress_data(file)
            label = self.clean_book_name(file)[:45]
            progress = f"page {pdf_page + 1} • screen {text_page + 1}"
            self.blit(label, row.x + 35, row.y + 5, self.tiny_font, TEXT)
            self.blit(progress, row.right - 165, row.y + 5, self.tiny_font, TEXT_DIM)
        self.blit("enter/click open • ↑↓ select • esc back", 45, 555, self.tiny_font, TEXT_DIM)

    def wrap_text(self, text, width=WRAP_WIDTH):
        lines = []
        for paragraph in text.split("\n"):
            paragraph = paragraph.strip()
            if paragraph == "":
                lines.append("")
            else:
                lines.extend(textwrap.wrap(paragraph, width=width))
        return lines

    def load_page_text(self):
        page = self.pdf_doc[self.current_page]
        text = page.get_text("text")
        if text.strip() == "":
            text = "[no selectable text found on this page. this PDF may be scanned/images.]"
        self.current_text_lines = self.wrap_text(text)
        if not self.current_text_lines:
            self.current_text_lines = [""]

    def max_text_page(self):
        return max(0, (len(self.current_text_lines) - 1) // LINES_PER_SCREEN)

    def open_pdf(self, filename):
        path = os.path.join(BOOKS_FOLDER, filename)
        self.pdf_doc = fitz.open(path)
        self.current_book = filename
        saved_pdf_page, saved_text_page = self.get_progress_data(filename)
        if saved_pdf_page < 0 or saved_pdf_page >= len(self.pdf_doc):
            saved_pdf_page = 0
        self.current_page = saved_pdf_page
        self.load_page_text()
        if saved_text_page < 0 or saved_text_page > self.max_text_page():
            saved_text_page = 0
        self.text_page = saved_text_page
        self.mode = "reader"

    def draw_progress_bar(self, rect):
        if not self.pdf_doc:
            return
        total_pages = max(1, len(self.pdf_doc))
        progress = (self.current_page + 1) / total_pages
        pygame.draw.rect(self.screen, BAR_BG, rect, border_radius=5)
        fill = pygame.Rect(rect.x, rect.y, int(rect.w * progress), rect.h)
        pygame.draw.rect(self.screen, BAR_FILL, fill, border_radius=5)

    def draw_arrow(self, x, y, direction="right", s=3):
        if direction == "right":
            pattern = [
                "1000",
                "1100",
                "1110",
                "1111",
                "1110",
                "1100",
                "1000",
            ]
        else:
            pattern = [
                "0001",
                "0011",
                "0111",
                "1111",
                "0111",
                "0011",
                "0001",
            ]
        for row, line in enumerate(pattern):
            for col, ch in enumerate(line):
                if ch == "1":
                    pygame.draw.rect(
                        self.screen,
                        ACCENT,
                        (x + col * s, y + row * s, s, s)
                    )

    def draw_reader(self):
        self.screen.fill(BG)
        self.blit("reader", 45, 30, self.title_font, ACCENT)
        book_title = self.clean_book_name(self.current_book)[:45]
        self.blit(book_title, 45, 78, self.small_font, TEXT_DIM)
        reader_rect = pygame.Rect(40, 115, 820, 390)
        draw_panel(self.screen, reader_rect, PANEL, BORDER, 2, 12)
        screen_info = (
            f"page {self.current_page + 1}/{len(self.pdf_doc)}"
            f"  •  screen {self.text_page + 1}/{self.max_text_page() + 1}"
        )
        self.blit(screen_info, reader_rect.x + 22, reader_rect.y + 18, self.tiny_font, ACCENT)
        start = self.text_page * LINES_PER_SCREEN
        end = start + LINES_PER_SCREEN
        visible_lines = self.current_text_lines[start:start + LINES_PER_SCREEN]
        y = reader_rect.y + 55
        line_height = 22
        for line in visible_lines:
            self.blit(line, reader_rect.x + 28, y, self.small_font, TEXT)
            y += line_height
        progress_rect = pygame.Rect(reader_rect.x + 28, reader_rect.bottom + 10, reader_rect.w - 56, 8)
        self.draw_progress_bar(progress_rect)
        self.draw_arrow(45, 555, "left")
        self.blit("prev", 70, 552, self.tiny_font, TEXT_DIM)
        self.draw_arrow(140, 555, "right")
        self.blit("next", 165, 552, self.tiny_font, TEXT_DIM)
        self.blit("esc save & return", 245, 552, self.tiny_font, TEXT_DIM)

    def next_page(self):
        if self.text_page < self.max_text_page():
            self.text_page += 1
        elif self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.text_page = 0
            self.load_page_text()
        else:
        # final screen of final PDF page → loop back to start
            self.current_page = 0
            self.text_page = 0
            self.load_page_text()
        self.save_current_page()

    def previous_page(self):
        if self.text_page > 0:
            self.text_page -= 1
        elif self.current_page > 0:
            self.current_page -= 1
            self.load_page_text()
            self.text_page = self.max_text_page()
        else:
        # first screen of first page → jump to end of book
            self.current_page = len(self.pdf_doc) - 1
            self.load_page_text()
            self.text_page = self.max_text_page()
        self.save_current_page()

    def handle_list_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_DOWN and self.files:
                self.selected_index = (self.selected_index + 1) % len(self.files)
            if event.key == pygame.K_UP and self.files:
                self.selected_index = (self.selected_index - 1) % len(self.files)
            if event.key == pygame.K_RETURN and self.files:
                self.open_pdf(self.files[self.selected_index])
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            list_rect = pygame.Rect(35, 120, 830, 390)
            start_y = list_rect.y + 65
            for i, file in enumerate(self.files[:8]):
                row = pygame.Rect(list_rect.x + 20, start_y + i * 38, list_rect.w - 40, 30)
                if row.collidepoint(event.pos):
                    self.selected_index = i
                    self.open_pdf(file)
        return True

    def handle_reader_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.save_current_page()
                self.mode = "list"
            if event.key == pygame.K_RIGHT:
                self.next_page()
            if event.key == pygame.K_LEFT:
                self.previous_page()

    def run(self):
        running = True
        while running:
            if self.mode == "list":
                self.draw_list()
            else:
                self.draw_reader()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if self.mode == "list":
                    running = self.handle_list_event(event)
                else:
                    self.handle_reader_event(event)
            self.clock.tick(60)

def open_library(screen):
    library = Library(screen)
    library.run()