import pygame
from ui.theme import ACCENT, ACCENT2, TEXT_DIM


def draw_pixel_icon(surf, pattern, x, y, s=3, color=ACCENT):
    for row, line in enumerate(pattern):
        for col, char in enumerate(line):
            if char == "1":
                pygame.draw.rect(surf, color, (x + col * s, y + row * s, s, s))


BOOK_ICON = [
    "011110",
    "010010",
    "010010",
    "011110",
    "010010",
    "010010",
    "011110",
]

ART_ICON = [
    "000100",
    "001100",
    "011000",
    "110000",
    "111000",
    "011100",
    "001000",
]

GALLERY_ICON = [
    "111111",
    "100001",
    "101101",
    "101101",
    "100001",
    "111111",
]

GAME_ICON = [
    "011110",
    "111111",
    "101101",
    "111111",
    "010010",
]

MUSIC_ICON = [
    "001111",
    "001001",
    "001001",
    "001001",
    "111001",
    "111000",
]

def draw_book(surf, x, y, s=4):
    draw_pixel_icon(surf, BOOK_ICON, x, y, s, ACCENT)

def draw_art(surf, x, y, s=4):
    draw_pixel_icon(surf, ART_ICON, x, y, s, ACCENT2)

def draw_gallery(surf, x, y, s=4):
    draw_pixel_icon(surf, GALLERY_ICON, x, y, s, ACCENT)

def draw_game(surf, x, y, s=4):
    draw_pixel_icon(surf, GAME_ICON, x, y, s, ACCENT2)

def draw_music(surf, x, y, s=4):
    draw_pixel_icon(surf, MUSIC_ICON, x, y, s, ACCENT)